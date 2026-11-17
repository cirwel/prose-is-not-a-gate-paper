"""Unified model adapters for Ollama, OpenAI API, and Claude CLI with hard USD circuit breaker."""

from __future__ import annotations

import json
import os
import re
import ssl
import subprocess
import tempfile
import threading
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

OLLAMA_CHAT_URL = "http://localhost:11434/api/chat"
OPENAI_CHAT_URL = "https://api.openai.com/v1/chat/completions"
MAX_OPENAI_USD = 20.00
DEFAULT_USAGE_LOG = Path("runs/api_usage.jsonl")

# Conservative upper-bound USD per 1M tokens for spend tracking / hard stop.
OPENAI_RATES_PER_1M: dict[str, tuple[float, float]] = {
    "gpt-6.1-sol": (3.00, 12.00),
    "gpt-6-luna": (0.80, 3.20),
    "gpt-5.4-nano": (0.25, 1.00),
}

_NO_TEMPERATURE: set[str] = set()
_SSL_CTX: ssl.SSLContext | None = None
_LOCK = threading.Lock()
_EMPTY_DIR = Path(tempfile.mkdtemp(prefix="rh_cli_"))


class BudgetExceededError(RuntimeError):
    """Raised when cumulative OpenAI spend reaches MAX_OPENAI_USD."""


def _ssl_context() -> ssl.SSLContext:
    global _SSL_CTX
    if _SSL_CTX is None:
        _SSL_CTX = ssl.create_default_context()
        try:
            import certifi

            _SSL_CTX.load_verify_locations(certifi.where())
        except ImportError:
            pass
    return _SSL_CTX


def load_openai_api_key() -> str:
    env_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if env_key:
        return env_key
    secrets_path = Path.home() / ".config/cirwel/secrets.env"
    if secrets_path.is_file():
        for line in secrets_path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\s*(?:export\s+)?OPENAI_API_KEY\s*=\s*(.*?)\s*$", line)
            if m:
                val = m.group(1).strip().strip('"').strip("'")
                if val:
                    return val
    raise RuntimeError("OPENAI_API_KEY not set in env or ~/.config/cirwel/secrets.env")


def estimate_usd(model: str, prompt_tokens: int, output_tokens: int) -> float:
    for prefix, (in_rate, out_rate) in OPENAI_RATES_PER_1M.items():
        if model.startswith(prefix):
            return (prompt_tokens * in_rate + output_tokens * out_rate) / 1_000_000.0
    return (prompt_tokens * 5.0 + output_tokens * 15.0) / 1_000_000.0


def current_openai_spend_usd(usage_log: Path = DEFAULT_USAGE_LOG) -> float:
    if not usage_log.is_file():
        return 0.0
    total = 0.0
    for line in usage_log.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        total += float(d.get("estimated_usd", 0.0))
    return total


def first_json_object(text: str) -> str:
    start = text.find("{")
    if start < 0:
        return text
    depth, in_string, escaped = 0, False, False
    for i in range(start, len(text)):
        ch = text[i]
        if in_string:
            if escaped:
                escaped = False
            elif ch == "\\":
                escaped = True
            elif ch == '"':
                in_string = False
        elif ch == '"':
            in_string = True
        elif ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]
    return text[start:]


def _render_cli_prompt(messages: list[dict[str, str]]) -> tuple[str, str]:
    system = messages[0]["content"]
    parts = [messages[1]["content"]]
    turn = 0
    for m in messages[2:]:
        if m["role"] == "assistant":
            turn += 1
            parts.append(f"--- Your reply {turn} ---\n{m['content']}")
        else:
            parts.append(f"--- Tool output after reply {turn} ---\n{m['content']}")
    if turn:
        parts.append("Reply with your next single JSON object only.")
    return system, "\n\n".join(parts)


def provider_for_model(model: str) -> str:
    if model.startswith("gpt-"):
        return "openai"
    if model.startswith("claude-"):
        return "claude-cli"
    return "ollama"


def unload_ollama_model(model: str) -> None:
    if provider_for_model(model) != "ollama":
        return
    body = json.dumps({"model": model, "keep_alive": 0}).encode("utf-8")
    req = urllib.request.Request(OLLAMA_CHAT_URL, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15):
            pass
    except Exception:
        pass


def call_ollama(model: str, messages: list[dict[str, str]], seed: int = 0, temperature: float = 0.2) -> tuple[str, dict[str, Any]]:
    last_error: str = "no attempt"
    for attempt in range(6):
        opts: dict[str, Any] = {
            "temperature": temperature if attempt == 0 else min(0.7, round(temperature + 0.12 * attempt, 2)),
            "seed": seed if attempt == 0 else seed + 101 * attempt,
            "num_ctx": 8192,
            "num_predict": 2048 if attempt < 2 else 1024,
        }
        if attempt > 0:
            opts["repeat_penalty"] = round(1.15 + 0.08 * attempt, 2)
            opts["repeat_last_n"] = 256
        req_messages = messages
        if attempt == 5 and messages:
            req_messages = list(messages[:-1]) + [
                {
                    "role": messages[-1]["role"],
                    "content": messages[-1]["content"] + "\n\nReply with ONE valid JSON object only.",
                }
            ]
        body: dict[str, Any] = {
            "model": model,
            "messages": req_messages,
            "stream": False,
            "think": False,
            "options": opts,
        }
        if attempt < 5:
            body["format"] = "json"
        req = urllib.request.Request(
            OLLAMA_CHAT_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={"Content-Type": "application/json"},
        )
        started = time.time()
        try:
            with urllib.request.urlopen(req, timeout=180) as resp:
                data = json.load(resp)
            elapsed = round(time.time() - started, 3)
            msg = data.get("message") or {}
            content = first_json_object(msg.get("content") or "")
            meta = {
                "provider": "ollama",
                "model": model,
                "prompt_tokens": int(data.get("prompt_eval_count") or 0),
                "output_tokens": int(data.get("eval_count") or 0),
                "seconds": elapsed,
                "retry_attempt": attempt,
                "estimated_usd": 0.0,
            }
            return content, meta
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            last_error = f"HTTP {exc.code}: {detail}"
            if exc.code >= 500:
                if "repeat" in detail.lower():
                    if attempt == 5:
                        return '{"error": "ollama_repeat_abort"}', {
                            "provider": "ollama",
                            "model": model,
                            "prompt_tokens": 0,
                            "output_tokens": 0,
                            "seconds": round(time.time() - started, 3),
                            "retry_attempt": attempt,
                            "aborted_repeat": True,
                            "estimated_usd": 0.0,
                        }
                    time.sleep(0.5)
                    continue
                unload_ollama_model(model)
            else:
                raise
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = repr(exc)[:300]
        time.sleep(min(30, 2 * (2**attempt)))
    raise RuntimeError(f"Ollama failed after retries for {model}: {last_error}")


def call_openai(
    model: str,
    messages: list[dict[str, str]],
    seed: int = 0,
    temperature: float = 0.2,
    usage_log: Path | None = None,
    max_usd: float = MAX_OPENAI_USD,
) -> tuple[str, dict[str, Any]]:
    log_path = usage_log or Path(os.environ.get("REPOHANDOFF_USAGE_LOG", str(DEFAULT_USAGE_LOG)))
    with _LOCK:
        spent = current_openai_spend_usd(log_path)
        if spent >= max_usd:
            raise BudgetExceededError(f"OpenAI spend {spent:.4f} >= cap {max_usd:.2f}")
    key = load_openai_api_key()
    last_error = "no attempt"
    for attempt in range(6):
        body: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "response_format": {"type": "json_object"},
            "seed": seed,
        }
        if model not in _NO_TEMPERATURE:
            body["temperature"] = temperature
        req = urllib.request.Request(
            OPENAI_CHAT_URL,
            data=json.dumps(body).encode("utf-8"),
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        started = time.time()
        try:
            with urllib.request.urlopen(req, timeout=180, context=_ssl_context()) as resp:
                data = json.load(resp)
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", "replace")[:300]
            last_error = f"HTTP {exc.code}: {detail}"
            if exc.code == 400 and "temperature" in detail and "temperature" in body:
                _NO_TEMPERATURE.add(model)
                continue
            if exc.code in (408, 409, 429, 500, 502, 503, 504):
                time.sleep(min(45, 3 * (2**attempt)))
                continue
            raise RuntimeError(f"OpenAI HTTP error for {model}: {last_error}") from exc
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            last_error = repr(exc)[:300]
            time.sleep(min(45, 3 * (2**attempt)))
            continue
        usage = data.get("usage") or {}
        ptok = int(usage.get("prompt_tokens") or 0)
        otok = int(usage.get("completion_tokens") or 0)
        resolved = str(data.get("model") or model)
        cost = round(estimate_usd(resolved, ptok, otok), 6)
        meta = {
            "provider": "openai",
            "model": resolved,
            "requested_model": model,
            "prompt_tokens": ptok,
            "output_tokens": otok,
            "seconds": round(time.time() - started, 3),
            "estimated_usd": cost,
        }
        with _LOCK:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            with log_path.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(meta) + "\n")
        raw_content = (data.get("choices") or [{}])[0].get("message", {}).get("content") or ""
        return first_json_object(raw_content), meta
    raise RuntimeError(f"OpenAI retries exhausted for {model}: {last_error}")


def call_claude_cli(model: str, messages: list[dict[str, str]], seed: int = 0, temperature: float = 0.2) -> tuple[str, dict[str, Any]]:
    del seed, temperature
    system, prompt = _render_cli_prompt(messages)
    last_error = "no attempt"
    for attempt in range(4):
        started = time.time()
        proc = subprocess.run(
            [
                "claude",
                "-p",
                "--model",
                model,
                "--setting-sources",
                "local",
                "--system-prompt",
                system,
                "--tools",
                "",
                "--no-session-persistence",
                "--output-format",
                "json",
                prompt,
            ],
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            cwd=str(_EMPTY_DIR),
            timeout=180,
        )
        try:
            data = json.loads(proc.stdout)
        except ValueError:
            last_error = f"exit {proc.returncode}: {proc.stdout[:200]!r} {proc.stderr[:200]!r}"
        else:
            if not data.get("is_error") and isinstance(data.get("result"), str):
                usage = data.get("usage") or {}
                meta = {
                    "provider": "claude-cli",
                    "model": model,
                    "prompt_tokens": int(
                        (usage.get("input_tokens") or 0)
                        + (usage.get("cache_read_input_tokens") or 0)
                        + (usage.get("cache_creation_input_tokens") or 0)
                    ),
                    "output_tokens": int(usage.get("output_tokens") or 0),
                    "seconds": round(time.time() - started, 3),
                    "estimated_usd": 0.0,
                }
                return first_json_object(data["result"]), meta
            last_error = str(data.get("result") or data)[:300]
        time.sleep(10 * (attempt + 1))
    raise RuntimeError(f"Claude CLI failed for {model}: {last_error}")


def call_model(model: str, messages: list[dict[str, str]], seed: int = 0, temperature: float = 0.2) -> tuple[str, dict[str, Any]]:
    prov = provider_for_model(model)
    if prov == "openai":
        return call_openai(model, messages, seed=seed, temperature=temperature)
    if prov == "claude-cli":
        return call_claude_cli(model, messages, seed=seed, temperature=temperature)
    return call_ollama(model, messages, seed=seed, temperature=temperature)
