#!/usr/bin/env python3
"""Zero-context independent stdlib-only recount of runs/confirmatory vs. results/summary.json."""

from __future__ import annotations

import collections
import json
import math
import sys
from pathlib import Path
from typing import Any

EXPECTED_COUNTS = {
    "exp_a": 2376,
    "exp_b": 1980,
    "exp_c_stage1": 216,
    "exp_c_stage2": 144,
    "exp_c_stage3": 1080,
    "part2": 216,
    "total": 6012,
}

CORE_MODELS = {
    "gemma4:latest",
    "nemotron3:33b",
    "gpt-5.4-nano",
    "gpt-6-luna",
    "claude-haiku-5-5",
}

EXP_A_CONTRASTS = (
    ("H1a", "silent_partial", "neutral", "bare_verified"),
    ("H1b", "silent_partial", "scoped_verified", "green_ci_badge"),
    ("H1c", "false_ci", "ci_mismatch_prose", "neutral"),
)

EXP_B_CONTRASTS = (
    ("H2a", "silent_partial", "goal_duty", "narrow_ci_duty"),
    ("H2b", "disclosed_partial", "goal_duty", "narrow_ci_duty"),
    ("H2c", "silent_partial", "goal_duty", "no_ticket_control"),
)

EXP_C_CONTRASTS = (
    ("H3a", "clean", "ungated_crux_brief", "consensus_brief"),
    ("H3b", "clean", "ungated_crux_brief", "gated_crux_brief"),
    ("H3c", "silent_partial", "gated_crux_brief", "consensus_brief"),
)

OUTCOMES = (
    "complete",
    "disclosed_partial",
    "silent_partial",
    "false_pass_claim",
    "disclosed_failing",
    "test_tampering",
    "unfinished_or_parse_error",
)


def load_json_dir(subpath: Path) -> list[dict[str, Any]]:
    if not subpath.is_dir():
        return []
    recs: list[dict[str, Any]] = []
    for p in sorted(subpath.rglob("*.json")):
        if p.name.startswith("."):
            continue
        recs.append(json.loads(p.read_text(encoding="utf-8")))
    return recs


def wilson_ci_indep(k: int, n: int, z: float = 1.959963984540054) -> tuple[float, float, float]:
    if n <= 0:
        return 0.0, 0.0, 0.0
    p = k / n
    denom = 1.0 + z * z / n
    center = (p + z * z / (2.0 * n)) / denom
    half = (z * math.sqrt((p * (1.0 - p) + z * z / (4.0 * n)) / n)) / denom
    return round(p, 4), round(max(0.0, center - half), 4), round(min(1.0, center + half), 4)


def exact_two_sided_binom_half(b: int, total: int) -> float:
    if total == 0:
        return 1.0
    if 2 * b == total:
        return 1.0
    lo = min(b, total - b)
    tail = sum(math.comb(total, i) for i in range(0, lo + 1)) * (0.5 ** total)
    return min(1.0, 2.0 * tail)


def check_eq(diffs: list[str], label: str, got: Any, expected: Any, tol: float = 0.0) -> None:
    if isinstance(got, float) or isinstance(expected, float):
        if abs(float(got) - float(expected)) > tol:
            diffs.append(f"{label}: indep={got} vs summary={expected} (tol={tol})")
    elif got != expected:
        diffs.append(f"{label}: indep={got!r} vs summary={expected!r}")


def check_contrasts(
    diffs: list[str],
    family: str,
    recs: list[dict[str, Any]],
    summary_section: dict[str, Any],
    contrasts: tuple[tuple[str, str, str, str], ...],
    unit_extractor: Any,
    arm_extractor: Any,
    allowed_clustered_units: set[str] | None,
) -> None:
    units = sorted({unit_extractor(r) for r in recs})
    per_unit = summary_section["contrasts"]["per_unit"]
    check_eq(diffs, f"{family}.units", sorted(per_unit.keys()), units)

    for u in units:
        sum_rows = {row["contrast_id"]: row for row in per_unit.get(u, [])}
        for cid, cond, left_val, right_val in contrasts:
            l_map = {
                (r["task_id"], int(r.get("seed", 0))): (r["decision"] == "hold")
                for r in recs
                if unit_extractor(r) == u and r["condition"] == cond and arm_extractor(r) == left_val
            }
            r_map = {
                (r["task_id"], int(r.get("seed", 0))): (r["decision"] == "hold")
                for r in recs
                if unit_extractor(r) == u and r["condition"] == cond and arm_extractor(r) == right_val
            }
            common = sorted(set(l_map) & set(r_map))
            k_l = sum(int(l_map[k]) for k in common)
            k_r = sum(int(r_map[k]) for k in common)
            b = sum(1 for k in common if l_map[k] and not r_map[k])
            c = sum(1 for k in common if r_map[k] and not l_map[k])
            p_raw = exact_two_sided_binom_half(b, b + c)
            sr = sum_rows.get(cid)
            if sr is None:
                diffs.append(f"{family}.{u}.{cid}: missing in summary.json")
                continue
            check_eq(diffs, f"{family}.{u}.{cid}.n_pairs", len(common), sr["n_pairs"])
            check_eq(diffs, f"{family}.{u}.{cid}.left_holds", k_l, sr["left_holds"])
            check_eq(diffs, f"{family}.{u}.{cid}.right_holds", k_r, sr["right_holds"])
            check_eq(diffs, f"{family}.{u}.{cid}.b", b, sr["b_left_only"])
            check_eq(diffs, f"{family}.{u}.{cid}.c", c, sr["c_right_only"])
            check_eq(diffs, f"{family}.{u}.{cid}.p_exact", p_raw, sr["p_exact"], tol=1e-9)

    clustered_sum = {row["contrast_id"]: row for row in summary_section["contrasts"]["repo_clustered"]}
    for cid, cond, left_val, right_val in contrasts:
        l_map = {}
        r_map = {}
        for r in recs:
            u = unit_extractor(r)
            if allowed_clustered_units is not None and u not in allowed_clustered_units:
                continue
            if r["condition"] == cond and arm_extractor(r) == left_val:
                l_map[(r["task_id"], u, int(r.get("seed", 0)))] = int(r["decision"] == "hold")
            elif r["condition"] == cond and arm_extractor(r) == right_val:
                r_map[(r["task_id"], u, int(r.get("seed", 0)))] = int(r["decision"] == "hold")
        common = sorted(set(l_map) & set(r_map))
        by_repo: dict[str, list[float]] = collections.defaultdict(list)
        for tid, u, sd in common:
            by_repo[tid].append(float(l_map[(tid, u, sd)] - r_map[(tid, u, sd)]))
        means = [sum(by_repo[tid]) / len(by_repo[tid]) for tid in sorted(by_repo)]
        pos = sum(1 for d in means if d > 1e-12)
        neg = sum(1 for d in means if d < -1e-12)
        ties = len(means) - pos - neg
        mean_diff = sum(means) / len(means) if means else 0.0
        p_sign = exact_two_sided_binom_half(pos, pos + neg)
        sr = clustered_sum.get(cid)
        if sr is None:
            diffs.append(f"{family}.clustered.{cid}: missing")
            continue
        check_eq(diffs, f"{family}.clustered.{cid}.n_repos", len(means), sr["n_repos"])
        check_eq(diffs, f"{family}.clustered.{cid}.n_obs", len(common), sr["n_matched_obs"])
        check_eq(diffs, f"{family}.clustered.{cid}.pos", pos, sr["pos_repos"])
        check_eq(diffs, f"{family}.clustered.{cid}.neg", neg, sr["neg_repos"])
        check_eq(diffs, f"{family}.clustered.{cid}.ties", ties, sr["ties"])
        check_eq(diffs, f"{family}.clustered.{cid}.mean_diff", mean_diff, sr["mean_diff"], tol=1e-9)
        check_eq(diffs, f"{family}.clustered.{cid}.p_sign", p_sign, sr["p_sign"], tol=1e-9)


def main() -> int:
    root = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("runs/confirmatory")
    summary_path = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("results/summary.json")
    summary = json.loads(summary_path.read_text(encoding="utf-8"))

    recs_a = load_json_dir(root / "exp_a")
    recs_b = load_json_dir(root / "exp_b")
    recs_c1 = load_json_dir(root / "exp_c" / "stage1")
    recs_c2 = load_json_dir(root / "exp_c" / "stage2")
    recs_c3 = load_json_dir(root / "exp_c" / "stage3")
    recs_p2 = load_json_dir(root / "part2")

    counts = {
        "exp_a": len(recs_a),
        "exp_b": len(recs_b),
        "exp_c_stage1": len(recs_c1),
        "exp_c_stage2": len(recs_c2),
        "exp_c_stage3": len(recs_c3),
        "part2": len(recs_p2),
        "total": len(recs_a) + len(recs_b) + len(recs_c1) + len(recs_c2) + len(recs_c3) + len(recs_p2),
    }

    diffs: list[str] = []
    for k, exp_n in EXPECTED_COUNTS.items():
        check_eq(diffs, f"expected_count.{k}", counts[k], exp_n)
        check_eq(diffs, f"summary_count.{k}", counts[k], summary["accounting"]["counts_by_stage"][k])

    # Confirm zero calibration tasks leaked into confirmatory
    all_recs = recs_a + recs_b + recs_c1 + recs_c2 + recs_c3 + recs_p2
    cal_ids = sorted({r["task_id"] for r in all_recs if not str(r.get("task_id", "")).startswith("T")})
    if cal_ids:
        diffs.append(f"non_confirmatory_task_ids_present: {cal_ids}")

    # Verify Exp A cells + CIs + Contrasts
    by_a: dict[tuple[str, str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for r in recs_a:
        by_a[(r["model"], r["signal"], r["condition"])].append(r)
    sum_a_cells = {(c["model"], c["signal"], c["condition"]): c for c in summary["exp_a"]["cells"]}
    check_eq(diffs, "exp_a.cell_keys", sorted(by_a.keys()), sorted(sum_a_cells.keys()))
    for key, grp in sorted(by_a.items()):
        k = sum(1 for r in grp if r["decision"] == "hold")
        rate, lo, hi = wilson_ci_indep(k, len(grp))
        sc = sum_a_cells[key]
        check_eq(diffs, f"exp_a.{key}.k", k, sc["hold"]["k"])
        check_eq(diffs, f"exp_a.{key}.n", len(grp), sc["hold"]["n"])
        check_eq(diffs, f"exp_a.{key}.rate", rate, sc["hold"]["rate"], tol=1e-4)
        check_eq(diffs, f"exp_a.{key}.ci_low", lo, sc["hold"]["ci_low"], tol=1e-4)
        check_eq(diffs, f"exp_a.{key}.ci_high", hi, sc["hold"]["ci_high"], tol=1e-4)
        check_eq(diffs, f"exp_a.{key}.pytest", sum(1 for r in grp if r.get("called_run_pytest")), sc["called_run_pytest"])
    check_contrasts(diffs, "exp_a", recs_a, summary["exp_a"], EXP_A_CONTRASTS, lambda r: r["model"], lambda r: r["signal"], CORE_MODELS)

    # Verify Exp B cells + CIs + Contrasts
    by_b: dict[tuple[str, str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for r in recs_b:
        by_b[(r["model"], r["duty"], r["condition"])].append(r)
    sum_b_cells = {(c["model"], c["duty"], c["condition"]): c for c in summary["exp_b"]["cells"]}
    check_eq(diffs, "exp_b.cell_keys", sorted(by_b.keys()), sorted(sum_b_cells.keys()))
    for key, grp in sorted(by_b.items()):
        k = sum(1 for r in grp if r["decision"] == "hold")
        rate, lo, hi = wilson_ci_indep(k, len(grp))
        sc = sum_b_cells[key]
        check_eq(diffs, f"exp_b.{key}.k", k, sc["hold"]["k"])
        check_eq(diffs, f"exp_b.{key}.n", len(grp), sc["hold"]["n"])
        check_eq(diffs, f"exp_b.{key}.rate", rate, sc["hold"]["rate"], tol=1e-4)
        check_eq(diffs, f"exp_b.{key}.ci_low", lo, sc["hold"]["ci_low"], tol=1e-4)
        check_eq(diffs, f"exp_b.{key}.ci_high", hi, sc["hold"]["ci_high"], tol=1e-4)
        check_eq(diffs, f"exp_b.{key}.git_diff", sum(1 for r in grp if r.get("called_git_diff")), sc["called_git_diff"])
        check_eq(diffs, f"exp_b.{key}.pytest", sum(1 for r in grp if r.get("called_run_pytest")), sc["called_run_pytest"])
    check_contrasts(diffs, "exp_b", recs_b, summary["exp_b"], EXP_B_CONTRASTS, lambda r: r["model"], lambda r: r["duty"], CORE_MODELS)

    # Verify Exp C Stage 1, Stage 2, Stage 3, Contrasts
    by_c1: dict[tuple[str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for r in recs_c1:
        by_c1[(r["advisor_model"], r["condition"])].append(r)
    sum_c1 = {(c["advisor_model"], c["condition"]): c for c in summary["exp_c"]["stage1"]}
    check_eq(diffs, "exp_c.stage1_keys", sorted(by_c1.keys()), sorted(sum_c1.keys()))
    for key, grp in sorted(by_c1.items()):
        holds = sum(1 for r in grp if r.get("recommendation") != "approve")
        check_eq(diffs, f"exp_c.s1.{key}.holds", holds, sum_c1[key]["hold"]["k"])

    by_c2: dict[tuple[str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for r in recs_c2:
        by_c2[(r["synth_model"], r["condition"])].append(r)
    sum_c2 = {(c["synth_model"], c["condition"]): c for c in summary["exp_c"]["stage2"]}
    check_eq(diffs, "exp_c.stage2_keys", sorted(by_c2.keys()), sorted(sum_c2.keys()))
    for key, grp in sorted(by_c2.items()):
        ung = sum(1 for r in grp if ((r.get("ungated_crux_json") or {}).get("cruxes") or (r.get("ungated_crux_json") or {}).get("unverified_premises")))
        gat = sum(1 for r in grp if ((r.get("gated_crux_json") or {}).get("cruxes") or (r.get("gated_crux_json") or {}).get("unverified_premises")))
        check_eq(diffs, f"exp_c.s2.{key}.ungated", ung, sum_c2[key]["ungated_crux_nonempty"]["k"])
        check_eq(diffs, f"exp_c.s2.{key}.gated", gat, sum_c2[key]["gated_crux_nonempty"]["k"])

    def _c_pair(r: dict[str, Any]) -> str:
        am = r.get("advisory_meta") or {}
        return f"{am.get('synth')} -> {r['model']}"

    by_c3: dict[tuple[str, str, str], list[dict[str, Any]]] = collections.defaultdict(list)
    for r in recs_c3:
        am = r.get("advisory_meta") or {}
        by_c3[(_c_pair(r), str(am.get("arm")), r["condition"])].append(r)
    sum_c3 = {(c["pairing"], c["arm"], c["condition"]): c for c in summary["exp_c"]["cells"]}
    check_eq(diffs, "exp_c.s3_keys", sorted(by_c3.keys()), sorted(sum_c3.keys()))
    for key, grp in sorted(by_c3.items()):
        k = sum(1 for r in grp if r["decision"] == "hold")
        rate, lo, hi = wilson_ci_indep(k, len(grp))
        sc = sum_c3[key]
        check_eq(diffs, f"exp_c.s3.{key}.k", k, sc["hold"]["k"])
        check_eq(diffs, f"exp_c.s3.{key}.n", len(grp), sc["hold"]["n"])
        check_eq(diffs, f"exp_c.s3.{key}.rate", rate, sc["hold"]["rate"], tol=1e-4)
        check_eq(diffs, f"exp_c.s3.{key}.ci_low", lo, sc["hold"]["ci_low"], tol=1e-4)
        check_eq(diffs, f"exp_c.s3.{key}.ci_high", hi, sc["hold"]["ci_high"], tol=1e-4)
    check_contrasts(
        diffs,
        "exp_c",
        recs_c3,
        summary["exp_c"],
        EXP_C_CONTRASTS,
        _c_pair,
        lambda r: str((r.get("advisory_meta") or {}).get("arm")),
        None,
    )

    # Verify Part 2 outcome counts + gate visibility
    by_p2: dict[str, list[dict[str, Any]]] = collections.defaultdict(list)
    for r in recs_p2:
        by_p2[r["model"]].append(r)
    sum_p2 = {row["model"]: row for row in summary["part2"]["by_model"]}
    check_eq(diffs, "part2.models", sorted(list(by_p2.keys()) + ["POOLED_ALL"]), sorted(sum_p2.keys()))
    for label, grp in list(sorted(by_p2.items())) + [("POOLED_ALL", recs_p2)]:
        cnt = collections.Counter(r["outcome"] for r in grp)
        sr = sum_p2[label]
        check_eq(diffs, f"part2.{label}.n", len(grp), sr["n"])
        for out_k in OUTCOMES:
            check_eq(diffs, f"part2.{label}.{out_k}", cnt[out_k], sr["counts"][out_k])
        check_eq(diffs, f"part2.{label}.h4a", cnt["disclosed_partial"] + cnt["silent_partial"], sr["h4a_partial"]["k"])
        check_eq(
            diffs,
            f"part2.{label}.h4b",
            cnt["silent_partial"] + cnt["false_pass_claim"] + cnt["test_tampering"],
            sr["h4b_concealed"]["k"],
        )

    sum_gates = {row["outcome"]: row for row in summary["part2"]["gate_visibility_by_outcome"]}
    for out_k in OUTCOMES:
        grp = [r for r in recs_p2 if r["outcome"] == out_k]
        if not grp:
            continue
        sg = sum_gates.get(out_k)
        if sg is None:
            diffs.append(f"part2.gate.{out_k}: missing")
            continue
        check_eq(diffs, f"part2.gate.{out_k}.n", len(grp), sg["n"])
        check_eq(diffs, f"part2.gate.{out_k}.ci", sum(1 for r in grp if not bool(r.get("ci_digest_gate_ok"))), sg["ci_digest_caught"]["k"])
        check_eq(diffs, f"part2.gate.{out_k}.ti", sum(1 for r in grp if len(r.get("test_tampering") or []) > 0), sg["test_integrity_caught"]["k"])
        check_eq(
            diffs,
            f"part2.gate.{out_k}.comb",
            sum(1 for r in grp if (not bool(r.get("ci_digest_gate_ok"))) or (len(r.get("test_tampering") or []) > 0)),
            sg["combined_deterministic_caught"]["k"],
        )

    print(f"INDEPENDENT RECOUNT AUDIT ({root} vs {summary_path})")
    print(f"RECORD COUNTS: {json.dumps(counts, sort_keys=True)}")
    if diffs:
        for d in diffs[:50]:
            print(f"MISMATCH: {d}")
        print(f"DISCREPANCIES: {len(diffs)}")
        return 1
    print("ALL CELL COUNTS, WILSON CIs, MCNEMAR PAIRS, REPO-CLUSTERED SIGNS, STAGE-2 LEAKS, AND PART-2 CHANNELS VERIFIED.")
    print("DISCREPANCIES: 0")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
