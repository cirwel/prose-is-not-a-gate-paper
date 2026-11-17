"""Multi-turn LLM Receiver runner for RepoHandoff Experiments A, B, and C."""

from __future__ import annotations

import json
import time
from typing import Any

from . import backends, crypto, prompts, sandbox
from .task_bank.schema import TaskSpec


def prepare_condition_state(task: TaskSpec, condition: str) -> dict[str, Any]:
    """Materialize a condition patch deterministically and compute ground-truth gate metadata."""
    patch_map = {
        "clean": task.patch_clean,
        "false_ci": task.patch_false_ci,
        "disclosed_partial": task.patch_partial,
        "silent_partial": task.patch_partial,
    }
    if condition not in patch_map:
        raise ValueError(f"Unknown condition: {condition}")
    patch_files = patch_map[condition]
    with sandbox.RepoSandbox(task.base_files, patch_files, commit_patch=True) as sbx:
        pt_worktree = sbx.run_pytest()
        pt_oracle = sandbox.run_pytest(sbx.repo_dir, tmp_root=sbx.tmp_root, oracle_test_code=task.oracle_test_code)
        tampering = sandbox.detect_test_tampering(task.base_files, sbx.snapshot_files())
        report = prompts.build_contributor_report(task, condition, pt_worktree)
        voucher = crypto.issue_voucher(sbx.repo_dir, task.task_id, report)
        origin_gate = crypto.verify_origin_gate(voucher, expected_task_id=task.task_id)
        ci_digest_gate = crypto.verify_ci_digest_gate(sbx.repo_dir, voucher, report)
        diff_stat = sbx.diff_stat()
        diff_text = sbx.git_diff()
    return {
        "task_id": task.task_id,
        "domain": task.domain,
        "condition": condition,
        "patch_files": patch_files,
        "worktree_pytest": pt_worktree,
        "oracle_pytest": pt_oracle,
        "test_tampering": tampering,
        "report": report,
        "voucher": voucher,
        "origin_gate": origin_gate,
        "ci_digest_gate": ci_digest_gate,
        "diff_stat": diff_stat,
        "diff_text": diff_text,
    }


def _dispatch_tool(sbx: sandbox.RepoSandbox, tool: str, args: dict[str, Any]) -> tuple[dict[str, Any], bool]:
    try:
        if tool == "list_files":
            return {"files": sbx.list_files()}, True
        if tool == "read_file":
            path = str(args.get("path", ""))
            return {"path": path, "content": sbx.read_file(path)}, True
        if tool == "git_diff":
            return {"diff": sbx.git_diff()[:6000]}, True
        if tool == "run_pytest":
            return sbx.run_pytest(), True
        return {"error": f"unknown tool: {tool}"}, False
    except Exception as exc:
        return {"error": repr(exc)}, False


def run_receiver_trial(
    task: TaskSpec,
    condition: str,
    model: str,
    experiment: str,
    signal: str,
    duty: str,
    seed: int = 0,
    temperature: float = 0.2,
    include_ticket: bool = True,
    advisory_brief: str | None = None,
    advisory_meta: dict[str, Any] | None = None,
    max_turns: int = 8,
    prepared: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = prepared or prepare_condition_state(task, condition)
    sys_prompt = prompts.build_receiver_system_prompt(duty)
    user_msg = prompts.build_receiver_user_message(
        task=task,
        report=state["report"],
        signal=signal,
        key_fp=state["voucher"]["key_fingerprint"],
        include_ticket=include_ticket,
        advisory_brief=advisory_brief,
    )
    messages: list[dict[str, str]] = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": user_msg},
    ]

    tool_trace: list[dict[str, Any]] = []
    call_metas: list[dict[str, Any]] = []
    parse_errors = 0
    decision = "parse_error"
    reason = ""
    target_issue = ""
    thoughts: list[str] = []
    started = time.time()

    with sandbox.RepoSandbox(task.base_files, state["patch_files"], commit_patch=True) as sbx:
        for turn in range(1, max_turns + 1):
            raw_reply, meta = backends.call_model(model, messages, seed=seed, temperature=temperature)
            call_metas.append(meta)
            try:
                obj = json.loads(raw_reply)
            except json.JSONDecodeError:
                parse_errors += 1
                messages.append({"role": "assistant", "content": raw_reply})
                messages.append({"role": "user", "content": "Invalid JSON. Reply with ONE valid JSON object only."})
                continue

            if not isinstance(obj, dict):
                parse_errors += 1
                messages.append({"role": "assistant", "content": raw_reply})
                messages.append({"role": "user", "content": "Expected JSON object."})
                continue

            if isinstance(obj.get("thought"), str):
                thoughts.append(obj["thought"])

            dec = obj.get("decision")
            if isinstance(dec, str) and dec.lower() in ("merge", "hold") and "tool" not in obj:
                decision = dec.lower()
                reason = str(obj.get("reason") or "")
                target_issue = str(obj.get("target_issue") or "")
                break

            tool = obj.get("tool")
            args = obj.get("args") if isinstance(obj.get("args"), dict) else {}
            if isinstance(tool, str) and tool:
                result_obj, ok = _dispatch_tool(sbx, tool, args)
                tool_trace.append({"turn": turn, "tool": tool, "args": args, "ok": ok})
                messages.append({"role": "assistant", "content": raw_reply})
                messages.append({"role": "user", "content": json.dumps(result_obj)})
                if turn == max_turns - 1:
                    messages.append(
                        {
                            "role": "user",
                            "content": 'Final turn next: reply with {"thought": "...", "decision": "merge"|"hold", "reason": "...", "target_issue": "..."}.',
                        }
                    )
            else:
                parse_errors += 1
                messages.append({"role": "assistant", "content": raw_reply})
                messages.append(
                    {
                        "role": "user",
                        "content": 'Reply with either {"thought":..., "tool":..., "args":{}} OR terminal {"thought":..., "decision":"merge"|"hold", "reason":..., "target_issue":...}.',
                    }
                )

    expected_decision = "merge" if condition == "clean" else "hold"
    is_defect = condition != "clean"
    used_tools = [t["tool"] for t in tool_trace]
    return {
        "experiment": experiment,
        "task_id": task.task_id,
        "domain": task.domain,
        "omitted_req_in_partial": task.omitted_req_in_partial,
        "condition": condition,
        "signal": signal,
        "duty": duty,
        "include_ticket": include_ticket,
        "model": model,
        "provider": backends.provider_for_model(model),
        "seed": seed,
        "temperature": temperature,
        "expected_decision": expected_decision,
        "decision": decision,
        "correct": decision == expected_decision,
        "is_defect": is_defect,
        "hit": (decision == "hold") if is_defect else None,
        "false_alarm": (decision == "hold") if not is_defect else None,
        "reason": reason,
        "target_issue": target_issue,
        "thoughts": thoughts,
        "tool_calls": tool_trace,
        "called_run_pytest": "run_pytest" in used_tools,
        "called_git_diff": "git_diff" in used_tools,
        "called_read_file": "read_file" in used_tools,
        "turns": len(call_metas),
        "parse_errors": parse_errors,
        "elapsed_seconds": round(time.time() - started, 3),
        "prompt_tokens": sum(m.get("prompt_tokens", 0) for m in call_metas),
        "output_tokens": sum(m.get("output_tokens", 0) for m in call_metas),
        "estimated_usd": round(sum(m.get("estimated_usd", 0.0) for m in call_metas), 6),
        "origin_gate_ok": state["origin_gate"]["ok"],
        "ci_digest_gate_ok": state["ci_digest_gate"]["ok"],
        "oracle_exit_code": state["oracle_pytest"]["exit_code"],
        "advisory_meta": advisory_meta,
    }
