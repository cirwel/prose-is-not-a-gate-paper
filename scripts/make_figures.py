#!/usr/bin/env python3
"""Generate publication-ready PDF and PNG figures directly from results/summary.json."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "font.size": 9,
        "axes.titlesize": 10,
        "axes.labelsize": 9,
        "xtick.labelsize": 8.6,
        "ytick.labelsize": 8.6,
        "legend.fontsize": 8.6,
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
    ("gemma4:latest", "gemma4:latest"),
    ("nemotron3:33b", "nemotron3:33b"),
]

PAIRING_LABELS = {
    "gemma4:latest -> nemotron3:33b": "gemma4 -> nemotron3",
    "nemotron3:33b -> claude-haiku-5-5": "nemotron3 -> claude-haiku-5-5",
    "nemotron3:33b -> gemma4:latest": "nemotron3 -> gemma4",
    "nemotron3:33b -> gpt-5.4-nano": "nemotron3 -> gpt-5.4-nano",
    "nemotron3:33b -> gpt-6-luna": "nemotron3 -> gpt-6-luna",
}


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

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.8, 5.6), sharey=True)

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
    ax1.set_title("A. Exp A: badges and mismatch notice", fontweight="bold")
    ax1.grid(axis="x", linestyle=":", alpha=0.5)
    ax1.legend(loc="upper center", bbox_to_anchor=(0.48, -0.13), ncol=1, frameon=False, fontsize=8.6)

    # Panel B: Exp B instruction arms
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
    ax2.set_title("B. Exp B: instruction sentence", fontweight="bold")
    ax2.grid(axis="x", linestyle=":", alpha=0.5)
    ax2.legend(loc="upper center", bbox_to_anchor=(0.48, -0.13), ncol=1, frameon=False, fontsize=8.6)

    fig.tight_layout()
    fig.savefig(out_dir / "fig2_signals_duties.pdf", bbox_inches="tight")
    fig.savefig(out_dir / "fig2_signals_duties.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_fig_briefs(summary: dict[str, Any], out_dir: Path) -> None:
    """Appendix figure: Experiment C Stage-2 field counts and Stage-3 holds on clean-labelled PRs."""
    c3_map = _cell_lookup(summary["exp_c"]["cells"], ("pairing", "arm", "condition"))
    s2_map = {(r["synth_model"], r["condition"]): r for r in summary["exp_c"]["stage2"]}

    fig = plt.figure(figsize=(9.2, 3.9))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.0], wspace=1.0)

    # Top-Left: Exp C Stage-2 Clean Crux Leak before vs after programmatic gate
    ax_tl = fig.add_subplot(gs[0, 0])
    synths = ["gemma4:latest", "nemotron3:33b"]
    s_labels = ["gemma4 synth", "nemotron3 synth"]
    x_idx = [0, 1]
    w = 0.34
    ung_vals = [s2_map[(s, "clean")]["ungated_crux_nonempty"]["rate"] for s in synths]
    gat_vals = [s2_map[(s, "clean")]["gated_crux_nonempty"]["rate"] for s in synths]
    ax_tl.bar([x - w / 2 for x in x_idx], ung_vals, width=w, color=COLORS["vermillion"], label="Ungated")
    ax_tl.bar([x + w / 2 for x in x_idx], gat_vals, width=w, color=COLORS["blue"], label="Gated")
    for x, uv, gv in zip(x_idx, ung_vals, gat_vals):
        ax_tl.text(x - w / 2, uv + 0.03, f"{int(round(uv*36))}/36", ha="center", va="bottom", fontsize=8.6)
        ax_tl.text(x + w / 2, gv + 0.03, f"{int(round(gv*36))}/36", ha="center", va="bottom", fontsize=8.6)
    ax_tl.set_xticks(x_idx)
    ax_tl.set_xticklabels(s_labels)
    ax_tl.set_ylim(0, 1.30)
    ax_tl.set_yticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax_tl.set_ylabel("Fraction of clean-labelled PRs")
    ax_tl.set_title("A. Stage-2 non-empty crux fields", fontweight="bold")
    ax_tl.grid(axis="y", linestyle=":", alpha=0.5)
    ax_tl.legend(loc="upper center", ncol=2, frameon=False, fontsize=8.6)

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
    ax_tr.set_xlabel("Hold Rate on Clean-Labelled PRs (95% CI)")
    ax_tr.set_title("B. Stage-3 holds, clean-labelled PRs", fontweight="bold")
    ax_tr.grid(axis="x", linestyle=":", alpha=0.5)
    ax_tr.legend(loc="upper center", bbox_to_anchor=(0.48, -0.22), ncol=3, frameon=False, fontsize=8.6)

    fig.savefig(out_dir / "figA_briefs.pdf", bbox_inches="tight")
    fig.savefig(out_dir / "figA_briefs.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def make_fig3(summary: dict[str, Any], out_dir: Path) -> None:
    """Part 2: live worker outcomes and what the deterministic gates flag."""
    p2_models = [r for r in summary["part2"]["by_model"] if r["model"] != "POOLED_ALL"]
    p2_gates = summary["part2"]["gate_visibility_by_outcome"]

    fig = plt.figure(figsize=(9.6, 4.3))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.0], wspace=1.0)

    # Left: Part 2 Live Worker outcome distribution by model
    ax_bl = fig.add_subplot(gs[0, 0])
    outcome_specs = [
        ("complete", "Passed both suites despite freeze", COLORS["green"]),
        ("disclosed_partial", "Disclosed partial", COLORS["sky"]),
        ("silent_partial", "Partial, completion claimed", COLORS["orange"]),
        ("test_tampering", "Pre-existing test edited", COLORS["vermillion"]),
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
    ax_bl.set_title("A. Worker outcomes (N=216)", fontweight="bold")
    ax_bl.legend(loc="upper center", bbox_to_anchor=(0.45, -0.22), ncol=1, frameon=False, fontsize=8.6)

    # Right: Deterministic Gate Catch Rate by Outcome Channel
    ax_br = fig.add_subplot(gs[0, 1])
    gate_order = [
        ("false_pass_claim", "False-pass claim"),
        ("disclosed_failing", "Disclosed failing"),
        ("unfinished_or_parse_error", "Unfinished / parse err"),
        ("test_tampering", "Pre-existing test edited"),
        ("disclosed_partial", "Disclosed partial"),
        ("silent_partial", "Partial, completion claimed"),
        ("complete", "Passed both suites"),
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
        ax_br.text(comb["rate"] + 0.02, y - h_bar / 2, f"{comb['k']}/{comb['n']}", va="center", ha="left", fontsize=8.6)
    ax_br.set_yticks(yg)
    ax_br.set_yticklabels([f"{lbl} (n={gmap[g]['n']})" for g, lbl in present_gates])
    ax_br.set_xlim(0, 1.15)
    ax_br.set_xlabel("Fraction Blocked by Deterministic Gates")
    ax_br.set_title("B. Flagged by deterministic gates", fontweight="bold")
    ax_br.grid(axis="x", linestyle=":", alpha=0.5)
    ax_br.legend(loc="upper center", bbox_to_anchor=(0.48, -0.22), ncol=1, frameon=False, fontsize=8.6)

    fig.savefig(out_dir / "fig3_workers.pdf", bbox_inches="tight")
    fig.savefig(out_dir / "fig3_workers.png", dpi=300, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    summary = json.loads(Path("results/summary.json").read_text(encoding="utf-8"))
    out_dir = Path("figures")
    out_dir.mkdir(parents=True, exist_ok=True)
    make_fig2(summary, out_dir)
    make_fig3(summary, out_dir)
    make_fig_briefs(summary, out_dir)
    print("Generated figures in figures/: fig2_signals_duties, fig3_workers, figA_briefs (.pdf & .png)")


if __name__ == "__main__":
    main()
