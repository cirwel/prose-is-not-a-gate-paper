"""Stage-1 advisor panel, Stage-2 consensus/crux synthesis, and programmatic gate for Exp C."""

from __future__ import annotations

import json
import re
from typing import Any

from . import backends, prompts
from .receiver import prepare_condition_state
from .task_bank.schema import TaskSpec

ADVISOR_PANEL: tuple[str, ...] = (
    "gemma4:latest",
    "nemotron3:33b",
    "qwen3.6:27b-coding-mxfp8",
)

_REQ_MENTION_RE = re.compile(
    r"(req\s*[_#]?\s*[12]|missing|unimplemented|omitted|not\s+implemented|lacks|absent|ticket\s+req)",
    re.IGNORECASE,
)
_TEST_FAIL_RE = re.compile(r"(pytest|test\w*\s+fail|failing\s+test|tests?\s+failed|exit\s+code)", re.IGNORECASE)


def run_stage1_advisor(
    task: TaskSpec,
    condition: str,
    advisor_model: str,
    seed: int = 0,
    temperature: float = 0.2,
    prepared: dict[str, Any] | None = None,
) -> dict[str, Any]:
    state = prepared or prepare_condition_state(task, condition)
    header = prompts.deterministic_header(state["worktree_pytest"], state["diff_stat"])
    user_msg = prompts.format_stage1_advisor_prompt(task, state["report"], state["diff_text"], header)
    messages = [
        {"role": "system", "content": prompts.STAGE1_ADVISOR_SYSTEM},
        {"role": "user", "content": user_msg},
    ]
    raw, meta = backends.call_model(advisor_model, messages, seed=seed, temperature=temperature)
    try:
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            parsed = {"summary": raw, "recommendation": "hold", "missing_or_broken": ["invalid_json_shape"]}
    except json.JSONDecodeError:
        parsed = {"summary": raw, "recommendation": "hold", "missing_or_broken": ["json_parse_error"]}
    rec = str(parsed.get("recommendation", "hold")).strip().lower()
    if rec not in ("approve", "hold"):
        rec = "hold"
    return {
        "task_id": task.task_id,
        "condition": condition,
        "advisor_model": advisor_model,
        "summary": str(parsed.get("summary", "")),
        "key_findings": [str(x) for x in (parsed.get("key_findings") or [])],
        "recommendation": rec,
        "missing_or_broken": [str(x) for x in (parsed.get("missing_or_broken") or [])],
        "verification_check": str(parsed.get("verification_check", "")),
        "confidence": float(parsed.get("confidence", 0.5) or 0.5),
        "meta": meta,
    }


def apply_programmatic_gate(
    crux_json: dict[str, Any],
    stage1_panel: list[dict[str, Any]],
    worktree_pytest: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    """Programmatically gate Stage-2 Crux JSON against deterministic pytest and panel split rules.

    1. When deterministic pytest exited 0 and all 3 Stage-1 advisors approve cleanly, clear leaked cruxes/premises.
    2. When deterministic pytest exited 0 and a solitary 1-of-3 'hold' cites only test-execution failure
       contradicted by exit==0 without citing a missing requirement, suppress that contradicted dissent.
    3. Otherwise (failing pytest, >=2 holds, or any requirement-omission dissent), preserve the Crux brief intact.
    """
    gated = dict(crux_json)
    pytest_ok = worktree_pytest.get("exit_code") == 0 and not worktree_pytest.get("failed_tests")
    holds = [a for a in stage1_panel if a.get("recommendation") != "approve"]

    if pytest_ok and len(holds) == 0:
        had_leak = bool(gated.get("cruxes") or gated.get("unverified_premises"))
        gated["cruxes"] = []
        gated["unverified_premises"] = []
        gated["suggested_check"] = "Confirm clean PR passes final review."
        return gated, ("suppressed_unanimous_leak" if had_leak else "unanimous_clean")

    if pytest_ok and len(holds) == 1:
        dissenter = holds[0]
        blob = " ".join(
            [dissenter.get("summary", "")]
            + list(dissenter.get("missing_or_broken") or [])
            + list(dissenter.get("key_findings") or [])
        )
        cites_req_omission = bool(_REQ_MENTION_RE.search(blob))
        cites_test_fail = bool(_TEST_FAIL_RE.search(blob))
        if cites_test_fail and not cites_req_omission:
            gated["cruxes"] = []
            gated["unverified_premises"] = []
            gated["suggested_check"] = "Deterministic pytest passed; solitary contradicted test-fail note suppressed."
            return gated, "suppressed_contradicted_minority_hold"
        return gated, "preserved_requirement_minority_hold"

    return gated, f"preserved_panel_holds_{len(holds)}"


def synthesize_briefs(
    task: TaskSpec,
    condition: str,
    synth_model: str,
    stage1_panel: list[dict[str, Any]],
    prepared: dict[str, Any],
    seed: int = 0,
    temperature: float = 0.2,
) -> dict[str, Any]:
    header = prompts.deterministic_header(prepared["worktree_pytest"], prepared["diff_stat"])
    panel_input = prompts.format_stage2_panel_input(task, header, stage1_panel, seed=seed)

    # 1. Consensus brief
    c_raw, c_meta = backends.call_model(
        synth_model,
        [
            {"role": "system", "content": prompts.STAGE2_CONSENSUS_SYSTEM},
            {"role": "user", "content": panel_input},
        ],
        seed=seed,
        temperature=temperature,
    )
    try:
        c_json = json.loads(c_raw)
    except json.JSONDecodeError:
        c_json = {"overview": c_raw, "key_points": [], "suggested_check": "Inspect PR manually."}

    # 2. Ungated Crux brief
    x_raw, x_meta = backends.call_model(
        synth_model,
        [
            {"role": "system", "content": prompts.STAGE2_CRUX_SYSTEM},
            {"role": "user", "content": panel_input},
        ],
        seed=seed,
        temperature=temperature,
    )
    try:
        x_json = json.loads(x_raw)
    except json.JSONDecodeError:
        x_json = {
            "overview": x_raw,
            "cruxes": [{"topic": "parse", "side_a": "approve", "side_b": "hold", "at_stake": "unknown"}],
            "unverified_premises": [],
            "suggested_check": "Inspect PR manually.",
        }

    # 3. Programmatically gated Crux brief (reuses exact same x_json before deterministic gate)
    gated_json, gate_action = apply_programmatic_gate(x_json, stage1_panel, prepared["worktree_pytest"])

    return {
        "task_id": task.task_id,
        "condition": condition,
        "synth_model": synth_model,
        "header_line": header,
        "stage1_hold_count": sum(1 for a in stage1_panel if a.get("recommendation") != "approve"),
        "gate_action": gate_action,
        "consensus_json": c_json,
        "ungated_crux_json": x_json,
        "gated_crux_json": gated_json,
        "briefs": {
            "consensus_brief": prompts.render_neutral_brief(header, c_json, "consensus_brief"),
            "ungated_crux_brief": prompts.render_neutral_brief(header, x_json, "ungated_crux_brief"),
            "gated_crux_brief": prompts.render_neutral_brief(header, gated_json, "gated_crux_brief"),
        },
        "meta": {"consensus": c_meta, "crux": x_meta},
    }
