#!/usr/bin/env python3
"""Post hoc exploratory arm for Experiment B (not pre-registered).

narrow_ci_duty changes two things relative to goal_duty: it points the receiver at
the CI result only, and it dictates the verdict ("if it exits 0 and matches, return
merge"). attention_only_duty keeps the first and drops the second. Records go to
runs/exploratory/exp_b_attention/, outside runs/confirmatory, so the confirmatory
recount is unaffected.

Only models that cost nothing to call are run. For a model that was not an
Experiment B receiver (qwen3.6), goal_duty and narrow_ci_duty are run here too so
that its three arms are matched; like every other use of that model in the study, it
runs on the BALANCED_18 slice because of its latency.
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from repohandoff import backends, receiver  # noqa: E402
from repohandoff.sweep import BALANCED_18_IDS, _max_workers_for, _prepare_all, _run_jobs, _safe_slug  # noqa: E402
from repohandoff.tasks import select_tasks  # noqa: E402

CONDITIONS = ("clean", "disclosed_partial", "silent_partial")
ORIGINAL_RECEIVERS = ("gemma4:latest", "nemotron3:33b", "claude-haiku-5-5")
NEW_RECEIVERS = ("qwen3.6:27b-coding-mxfp8",)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="runs/exploratory/exp_b_attention")
    ap.add_argument("--models", default=",".join(ORIGINAL_RECEIVERS + NEW_RECEIVERS))
    args = ap.parse_args()
    out_dir = Path(args.out)
    os.environ["REPOHANDOFF_USAGE_LOG"] = str((out_dir / "api_usage.jsonl").resolve())
    tasks = select_tasks("confirmatory")
    prep = _prepare_all(tasks, CONDITIONS)
    for model in [m.strip() for m in args.models.split(",") if m.strip()]:
        if backends.provider_for_model(model) == "openai":
            raise SystemExit(f"{model}: paid backend, not part of this arm")
        duties = ("attention_only_duty",)
        if model in NEW_RECEIVERS:
            duties = ("attention_only_duty", "narrow_ci_duty", "goal_duty")
        jobs = []
        model_tasks = [t for t in tasks if t.task_id in BALANCED_18_IDS] if model in NEW_RECEIVERS else tasks
        for task in model_tasks:
            for cond in CONDITIONS:
                for duty in duties:
                    p = out_dir / _safe_slug(model) / duty / cond / f"{task.task_id}_s0.json"
                    jobs.append(
                        (
                            p,
                            lambda t=task, c=cond, m=model, d=duty, st=prep[(task.task_id, cond)]: receiver.run_receiver_trial(
                                task=t,
                                condition=c,
                                model=m,
                                experiment="exp_b_exploratory",
                                signal="neutral",
                                duty=d,
                                include_ticket=True,
                                seed=0,
                                prepared=st,
                            ),
                        )
                    )
        _run_jobs(jobs, _max_workers_for(model))
        backends.unload_ollama_model(model)
        print(f"[exploratory] finished {model} ({len(jobs)} cells)", flush=True)


if __name__ == "__main__":
    main()
