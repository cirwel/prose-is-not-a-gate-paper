#!/usr/bin/env python3
"""Generate publication-ready PDF and PNG figures directly from results/summary.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8,
        "ytick.labelsize": 8,
        "legend.fontsize": 8,
        "axes.spines.top": False,
        "axes.spines.right": False,
    }
)

COLORS = {
    "blue": "#0072B2",
    "orange": "#E69F00",
    "vermillion": "#D55E00",
    "green": "#009E73",
    "purple": "#CC79A7",
    "sky": "#56B4E9",
    "black": "#222222",
    "gray": "#7F7F7F",
}

MODEL_ORDER = [
    ("claude-haiku-5-5", "claude-haiku-5-5"),
    ("gpt-6.1-sol", "gpt-6.1-sol (N=18)"),
    ("gpt-6-luna", "gpt-6-luna"),
    ("gpt-5.4-nano", "gpt-5.4-nano"),
    ("gemma4:latest", "gemma4 (8B)"),
    ("nemotron3:33b", "nemotron3 (33B)"),
]

PAIRING_LABELS = {
    "gemma4:latest -> nemotron3:33b": "gemma4 synth -> nemotron3",
    "nemotron3:33b -> claude-haiku-5-5": "nemotron3 -> haiku-5-5",
    "nemotron3:33b -> gemma4:latest": "nemotron3 -> gemma4",
    "nemotron3:33b -> gpt-5.4-nano": "nemotron3 -> gpt-5.4-nano",
    "nemotron3:33b -> gpt-6-luna": "nemotron3 -> gpt-6-luna",
}


def make_fig1(summary: dict[str, Any], out_dir: Path) -> None:
    det = summary["deterministic_gates"]
    eb_cl = {r["contrast_id"]: r for r in summary["exp_b"]["contrasts"]["repo_clustered"]}
    s2 = {(r["synth_model"], r["condition"]): r for r in summary["exp_c"]["stage2"]}
    p2_gates = {r["outcome"]: r for r in summary["part2"]["gate_visibility_by_outcome"]}

    suppressed_clean = sum(
        int(s2[(m, "clean")]["gate_actions"].get("suppressed_unanimous_leak", 0)) for m in ("gemma4:latest",)
    )
    h2a_pp = eb_cl["H2a"]["mean_diff"] * 100.0
    fc_det_block = det["false_ci"]["n_repos"] - det["false_ci"]["ci_digest_gate_pass"]
    sp_det_block = det["silent_partial"]["n_repos"] - det["silent_partial"]["ci_digest_gate_pass"]
    tamper_det = p2_gates["test_tampering"]["combined_deterministic_caught"]["k"]
    tamper_n = p2_gates["test_tampering"]["combined_deterministic_caught"]["n"]

    fig, ax = plt.subplots(figsize=(9.2, 4.6))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.2)
    ax.axis("off")

    ax.text(
        5.0,
        4.92,
        "Multi-Agent Software Handoff Pipeline & Four-Layer Verification Stack",
        ha="center",
        va="center",
        fontsize=11,
        fontweight="bold",
        color=COLORS["black"],
    )

    def draw_box(x: float, y: float, w: float, h: float, title: str, body: str, fc: str, ec: str) -> None:
        box = FancyBboxPatch(
            (x, y),
            w,
            h,
            boxstyle="round,pad=0.06,rounding_size=0.12",
            facecolor=fc,
            edgecolor=ec,
            linewidth=1.5,
        )
        ax.add_patch(box)
        ax.text(x + w / 2, y + h * 0.66, title, ha="center", va="center", fontsize=8.8, fontweight="bold", color=COLORS["black"])
        ax.text(x + w / 2, y + h * 0.28, body, ha="center", va="center", fontsize=7.6, color="#333333")

    # Top row: pipeline actors
    draw_box(0.2, 3.65, 2.0, 0.85, "1. Engineering Ticket", "Counterbalanced Req 1 + Req 2\n(T00..T35, N=36 repos)", "#F4F6F9", COLORS["gray"])
    draw_box(2.7, 3.65, 2.1, 0.85, "2. Contributor A", "Edits worktree & tests\nFiles completion JSON + Sig", "#EEF5FC", COLORS["blue"])
    draw_box(5.3, 3.65, 2.1, 0.85, "3. Advisory Panel", "3 Stage-1 advisors + blinded\nStage-2 brief synthesis (Exp C)", "#FFF7E6", COLORS["orange"])
    draw_box(7.8, 3.65, 2.0, 0.85, "4. Receiver B Gate", "Tools: read_file, git_diff,\nrun_pytest -> merge / hold", "#ECF8F3", COLORS["green"])

    for x0, x1 in ((2.26, 2.64), (4.86, 5.24), (7.46, 7.74)):
        ax.annotate("", xy=(x1, 4.07), xytext=(x0, 4.07), arrowprops=dict(arrowstyle="->", lw=1.6, color=COLORS["black"]))

    # Bottom verification stack (4 layers)
    layers = [
        (
            2.65,
            "Layer 1: OriginGate (Ed25519 Signature + Audience + Task Binding)",
            f"Verifies identity/integrity only: passes {det['false_ci']['origin_gate_pass']}/36 false_ci and {det['silent_partial']['origin_gate_pass']}/36 silent_partial (0 defects stopped).",
            "#FDF2EC",
            COLORS["vermillion"],
        ),
        (
            1.85,
            "Layer 2: CIDigestGate + TestIntegrityGate (Tree SHA-256 + Pytest Exit + AST Integrity)",
            f"Stops {fc_det_block}/36 false_ci claims & {tamper_det}/{tamper_n} tampered tests; stops {sp_det_block}/36 silent_partial when local pytest passes.",
            "#FFF4E5",
            COLORS["orange"],
        ),
        (
            1.05,
            "Layer 3: Programmatic Crux Gate (Deterministic Pytest + Stage-1 Panel Threshold)",
            f"Suppresses {suppressed_clean}/34 unanimous clean Stage-2 crux leaks while preserving 36/36 partial-PR panel holds.",
            "#EEF6FC",
            COLORS["blue"],
        ),
        (
            0.25,
            "Layer 4: Request-Bound Goal Verification (Ticket Reqs vs. Diff & Source)",
            f"Lifts silent_partial hold rate by +{h2a_pp:.1f} pp over Narrow CI Duty (p_holm < 0.05 on 6/6 models).",
            "#E9F7F1",
            COLORS["green"],
        ),
    ]
    for y, title, desc, fc, ec in layers:
        box = FancyBboxPatch(
            (0.35, y),
            9.3,
            0.64,
            boxstyle="round,pad=0.04,rounding_size=0.08",
            facecolor=fc,
            edgecolor=ec,
            linewidth=1.4,
        )
        ax.add_patch(box)
        ax.text(0.55, y + 0.43, title, ha="left", va="center", fontsize=8.6, fontweight="bold", color=COLORS["black"])
        ax.text(0.55, y + 0.18, desc, ha="left", va="center", fontsize=7.8, color="#222222")

    fig.tight_layout()
    fig.savefig(out_dir / "fig1_architecture.pdf", bbox_inches="tight")
    fig.savefig(out_dir / "fig1_architecture.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def _cell_lookup(cells: list[dict[str, Any]], key_fields: tuple[str, ...]) -> dict[tuple[str, ...], dict[str, Any]]:
    return {tuple(c[k] for k in key_fields): c for c in cells}


def _plot_ci_row(ax: Any, y: float, cell: dict[str, Any], color: str, marker: str, label: str | None = None) -> None:
    h = cell["hold"]
    p = h["rate"]
    lo = max(0.0, p - h["ci_low"])
    hi = max(0.0, h["ci_high"] - p)
    ax.errorbar(
        p,
        y,
        xerr=[[lo], [hi]],
        fmt=marker,
        color=color,
        markersize=6.2,
        capsize=3,
        elinewidth=1.4,
        label=label,
        zorder=4,
    )


def make_fig2(summary: dict[str, Any], out_dir: Path) -> None:
    a_map = _cell_lookup(summary["exp_a"]["cells"], ("model", "signal", "condition"))
    b_map = _cell_lookup(summary["exp_b"]["cells"], ("model", "duty", "condition"))

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 5.1), sharey=True)

    # Panel A: Exp A false_ci (neutral vs ci_mismatch_prose) + silent_partial (neutral vs green_ci_badge)
    y_positions = list(range(len(MODEL_ORDER)))[::-1]
    seen_a: set[str] = set()
    for y, (m_id, _) in zip(y_positions, MODEL_ORDER):
        ax1.axhspan(y - 0.42, y + 0.42, color="#F7F8FA" if y % 2 == 0 else "#FFFFFF", zorder=0)
        configs = [
            (0.24, "neutral", "false_ci", COLORS["vermillion"], "o", "false_ci | neutral"),
            (0.08, "ci_mismatch_prose", "false_ci", COLORS["orange"], "s", "false_ci | ci_mismatch_prose"),
            (-0.08, "neutral", "silent_partial", COLORS["blue"], "^", "silent_partial | neutral"),
            (-0.24, "green_ci_badge", "silent_partial", COLORS["sky"], "D", "silent_partial | green_ci_badge"),
        ]
        for dy, sig, cond, col, mk, lbl in configs:
            _plot_ci_row(ax1, y + dy, a_map[(m_id, sig, cond)], col, mk, lbl if lbl not in seen_a else None)
            seen_a.add(lbl)

    ax1.axvline(1.0, color=COLORS["gray"], linestyle="--", linewidth=1.1, label="CIDigestGate on false_ci (1.00)")
    ax1.set_yticks(y_positions)
    ax1.set_yticklabels([lbl for _, lbl in MODEL_ORDER])
    ax1.set_xlim(-0.05, 1.07)
    ax1.set_xlabel("Hold Rate (95% Wilson CI)")
    ax1.set_title("A. Exp A: Badges & Mismatch Prose under Discretion", fontweight="bold")
    ax1.grid(axis="x", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.48, -0.15), ncol=2, frameon=False, fontsize=7.6)

    # Panel B: Exp B procedural CI tunnel vision vs request binding
    seen_b: set[str] = set()
    for y, (m_id, _) in zip(y_positions, MODEL_ORDER):
        ax2.axhspan(y - 0.42, y + 0.42, color="#F7F8FA" if y % 2 == 0 else "#FFFFFF", zorder=0)
        configs = [
            (0.24, "goal_duty", "silent_partial", COLORS["green"], "o", "silent_partial | goal_duty"),
            (0.08, "narrow_ci_duty", "silent_partial", COLORS["vermillion"], "s", "silent_partial | narrow_ci_duty"),
            (-0.08, "no_ticket_control", "silent_partial", COLORS["gray"], "v", "silent_partial | no_ticket_control"),
            (-0.24, "narrow_ci_duty", "disclosed_partial", COLORS["purple"], "D", "disclosed_partial | narrow_ci_duty"),
        ]
        for dy, duty, cond, col, mk, lbl in configs:
            _plot_ci_row(ax2, y + dy, b_map[(m_id, duty, cond)], col, mk, lbl if lbl not in seen_b else None)
            seen_b.add(lbl)

    ax2.set_xlim(-0.05, 1.07)
    ax2.set_xlabel("Hold Rate (95% Wilson CI)")
    ax2.set_title("B. Exp B: Procedural CI Tunnel Vision vs. Goal Duty", fontweight="bold")
    ax2.grid(axis="x", linestyle=":", alpha=0.5)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.48, -0.15), ncol=2, frameon=False, fontsize=7.6)

    fig.tight_layout()
    fig.savefig(out_dir / "fig2_signals_duties.pdf", bbox_inches="tight")
    fig.savefig(out_dir / "fig2_signals_duties.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_fig3(summary: dict[str, Any], out_dir: Path) -> None:
    c3_map = _cell_lookup(summary["exp_c"]["cells"], ("pairing", "arm", "condition"))
    s2_map = {(r["synth_model"], r["condition"]): r for r in summary["exp_c"]["stage2"]}
    p2_models = [r for r in summary["part2"]["by_model"] if r["model"] != "POOLED_ALL"]
    p2_gates = summary["part2"]["gate_visibility_by_outcome"]

    fig = plt.figure(figsize=(12.2, 6.8))
    gs = fig.add_gridspec(2, 2, height_ratios=[1.0, 1.08], width_ratios=[1.0, 1.2], hspace=0.55, wspace=0.58)

    # Top-Left: Exp C Stage-2 Clean Crux Leak before vs after programmatic gate
    ax_tl = fig.add_subplot(gs[0, 0])
    synths = ["gemma4:latest", "nemotron3:33b"]
    s_labels = ["gemma4 synth", "nemotron3 synth"]
    x_idx = [0, 1]
    w = 0.34
    ung_vals = [s2_map[(s, "clean")]["ungated_crux_nonempty"]["rate"] for s in synths]
    gat_vals = [s2_map[(s, "clean")]["gated_crux_nonempty"]["rate"] for s in synths]
    ax_tl.bar([x - w / 2 for x in x_idx], ung_vals, width=w, color=COLORS["vermillion"], label="Ungated Stage-2 Crux")
    ax_tl.bar([x + w / 2 for x in x_idx], gat_vals, width=w, color=COLORS["blue"], label="Gated Stage-2 Crux")
    for x, uv, gv in zip(x_idx, ung_vals, gat_vals):
        ax_tl.text(x - w / 2, uv + 0.03, f"{int(round(uv*36))}/36", ha="center", va="bottom", fontsize=7.8)
        ax_tl.text(x + w / 2, gv + 0.03, f"{int(round(gv*36))}/36", ha="center", va="bottom", fontsize=7.8)
    ax_tl.set_xticks(x_idx)
    ax_tl.set_xticklabels(s_labels)
    ax_tl.set_ylim(0, 1.30)
    ax_tl.set_ylabel("Non-Empty Clean Crux Rate")
    ax_tl.set_title("A1. Stage-2 Clean Crux Fabrication", fontweight="bold")
    ax_tl.grid(axis="y", linestyle=":", alpha=0.5)
    ax_tl.legend(loc="upper center", ncol=2, frameon=False, fontsize=7.5)

    # Top-Right: Exp C Stage-3 Clean FA across 5 cross-family pairings
    ax_tr = fig.add_subplot(gs[0, 1])
    pairs = list(PAIRING_LABELS.keys())
    yp = list(range(len(pairs)))[::-1]
    seen_c: set[str] = set()
    for y, pr in zip(yp, pairs):
        ax_tr.axhspan(y - 0.38, y + 0.38, color="#F7F8FA" if y % 2 == 0 else "#FFFFFF", zorder=0)
        for dy, arm, col, mk, lbl in (
            (0.18, "ungated_crux_brief", COLORS["vermillion"], "o", "ungated_crux"),
            (0.0, "gated_crux_brief", COLORS["blue"], "s", "gated_crux"),
            (-0.18, "consensus_brief", COLORS["green"], "^", "consensus"),
        ):
            _plot_ci_row(ax_tr, y + dy, c3_map[(pr, arm, "clean")], col, mk, lbl if lbl not in seen_c else None)
            seen_c.add(lbl)
    ax_tr.set_yticks(yp)
    ax_tr.set_yticklabels([PAIRING_LABELS[p] for p in pairs])
    ax_tr.set_xlim(-0.03, 0.45)
    ax_tr.set_xlabel("Clean False-Alarm Hold Rate (95% CI)")
    ax_tr.set_title("A2. Stage-3 Decider Clean FA (silent_partial >= 94%)", fontweight="bold")
    ax_tr.grid(axis="x", linestyle=":", alpha=0.5)
    ax_tr.legend(loc="upper center", bbox_to_anchor=(0.48, -0.22), ncol=3, frameon=False, fontsize=7.4)

    # Bottom-Left: Part 2 Live Worker outcome distribution by model
    ax_bl = fig.add_subplot(gs[1, 0])
    outcome_specs = [
        ("complete", "Complete", COLORS["green"]),
        ("disclosed_partial", "Disclosed partial", COLORS["sky"]),
        ("silent_partial", "Silent partial", COLORS["orange"]),
        ("test_tampering", "Test tampering", COLORS["vermillion"]),
        ("false_pass_claim", "False-pass claim", COLORS["purple"]),
        ("disclosed_failing", "Disclosed failing", "#B0B8C1"),
        ("unfinished_or_parse_error", "Unfinished / parse err", COLORS["black"]),
    ]
    ym2 = list(range(len(p2_models)))[::-1]
    lefts = [0.0] * len(p2_models)
    for out_k, lbl, col in outcome_specs:
        vals = [r["counts"][out_k] / r["n"] for r in p2_models]
        ax_bl.barh(ym2, vals, left=lefts, height=0.62, color=col, label=lbl)
        lefts = [l + v for l, v in zip(lefts, vals)]
    ax_bl.set_yticks(ym2)
    ax_bl.set_yticklabels([f"{r['model']} (N={r['n']})" for r in p2_models])
    ax_bl.set_xlim(0, 1.0)
    ax_bl.set_xlabel("Proportion of Worker Runs")
    ax_bl.set_title("B1. Part 2 Worker Outcomes (N=216)", fontweight="bold")
    ax_bl.legend(loc="upper center", bbox_to_anchor=(0.45, -0.22), ncol=2, frameon=False, fontsize=7.2)

    # Bottom-Right: Deterministic Gate Catch Rate by Outcome Channel
    ax_br = fig.add_subplot(gs[1, 1])
    gate_order = [
        ("false_pass_claim", "False-pass claim"),
        ("disclosed_failing", "Disclosed failing"),
        ("unfinished_or_parse_error", "Unfinished / parse err"),
        ("test_tampering", "Test tampering"),
        ("disclosed_partial", "Disclosed partial"),
        ("silent_partial", "Silent partial"),
    ]
    gmap = {r["outcome"]: r for r in p2_gates}
    present_gates = [(g, lbl) for g, lbl in gate_order if g in gmap]
    yg = list(range(len(present_gates)))[::-1]
    h_bar = 0.34
    ci_rates = [gmap[g]["ci_digest_caught"]["rate"] for g, _ in present_gates]
    comb_rates = [gmap[g]["combined_deterministic_caught"]["rate"] for g, _ in present_gates]
    ax_br.barh([y + h_bar / 2 for y in yg], ci_rates, height=h_bar, color=COLORS["orange"], label="CIDigestGate alone")
    ax_br.barh([y - h_bar / 2 for y in yg], comb_rates, height=h_bar, color=COLORS["blue"], label="CIDigestGate + TestIntegrityGate")
    for y, (g, _) in zip(yg, present_gates):
        comb = gmap[g]["combined_deterministic_caught"]
        ax_br.text(comb["rate"] + 0.02, y - h_bar / 2, f"{comb['k']}/{comb['n']}", va="center", ha="left", fontsize=7.8)
    ax_br.set_yticks(yg)
    ax_br.set_yticklabels([f"{lbl} (n={gmap[g]['n']})" for g, lbl in present_gates])
    ax_br.set_xlim(0, 1.15)
    ax_br.set_xlabel("Fraction Blocked by Deterministic Gates")
    ax_br.set_title("B2. Deterministic Gate Blind Spots on Partial Delivery", fontweight="bold")
    ax_br.grid(axis="x", linestyle=":", alpha=0.5)
    ax_br.legend(loc="upper center", bbox_to_anchor=(0.48, -0.22), ncol=1, frameon=False, fontsize=7.4)

    fig.savefig(out_dir / "fig3_briefs_workers.pdf", bbox_inches="tight")
    fig.savefig(out_dir / "fig3_briefs_workers.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    summary = json.loads(Path("results/summary.json").read_text(encoding="utf-8"))
    out_dir = Path("figures")
    out_dir.mkdir(parents=True, exist_ok=True)
    make_fig1(summary, out_dir)
    make_fig2(summary, out_dir)
    make_fig3(summary, out_dir)
    print("Generated figures in figures/: fig1_architecture, fig2_signals_duties, fig3_briefs_workers (.pdf & .png)")


if __name__ == "__main__":
    main()
