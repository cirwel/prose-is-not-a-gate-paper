"""Resumable sweep orchestrator with provider-bounded concurrency and Exp A->B cache reuse."""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import threading
from pathlib import Path
from typing import Any, Callable

from . import backends, briefs, receiver, worker
from .tasks import CONFIRMATORY_TASKS, TASK_BY_ID, select_tasks

BALANCED_18_IDS: tuple[str, ...] = tuple(
    [f"T{i:02d}" for i in range(9)] + [f"T{i:02d}" for i in range(18, 27)]
)


def _safe_slug(name: str) -> str:
    return name.replace(":", "_").replace("/", "_")


def _write_json_atomic(out_path: Path, payload: dict[str, Any]) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = out_path.with_name(f".{out_path.name}.tmp.{threading.get_ident()}")
    tmp_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    os.replace(tmp_path, out_path)


def _load_or_run(out_path: Path, fn: Callable[[], dict[str, Any]]) -> dict[str, Any]:
    if out_path.is_file():
        return json.loads(out_path.read_text(encoding="utf-8"))
    res = fn()
    _write_json_atomic(out_path, res)
    return res


def _max_workers_for(model: str) -> int:
    prov = backends.provider_for_model(model)
    if prov == "openai":
        return 6
    if prov == "claude-cli":
        return 3
    return 1


def _run_jobs(jobs: list[tuple[Path, Callable[[], dict[str, Any]]]], max_workers: int) -> None:
    pending = [(p, fn) for p, fn in jobs if not p.is_file()]
    if not pending:
        return
    if max_workers <= 1:
        for p, fn in pending:
            _load_or_run(p, fn)
        return
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as pool:
        futs = [pool.submit(_load_or_run, p, fn) for p, fn in pending]
        for fut in concurrent.futures.as_completed(futs):
            fut.result()


def _prepare_all(tasks: list[Any], conditions: tuple[str, ...]) -> dict[tuple[str, str], dict[str, Any]]:
    cache: dict[tuple[str, str], dict[str, Any]] = {}
    for t in tasks:
        for c in conditions:
            cache[(t.task_id, c)] = receiver.prepare_condition_state(t, c)
    return cache


def _run_exp_a(tasks: list[Any], models: list[str], out_dir: Path, seeds: list[int], prep_cache: dict | None = None) -> None:
    cond_signals: dict[str, tuple[str, ...]] = {
        "clean": ("neutral", "bare_verified", "scoped_verified", "green_ci_badge"),
        "false_ci": ("neutral", "bare_verified", "scoped_verified", "ci_mismatch_prose"),
        "silent_partial": ("neutral", "bare_verified", "scoped_verified", "green_ci_badge"),
    }
    prep = prep_cache or _prepare_all(tasks, ("clean", "false_ci", "silent_partial"))
    for model in models:
        slug = _safe_slug(model)
        jobs: list[tuple[Path, Callable[[], dict[str, Any]]]] = []
        for task in tasks:
            for cond, sigs in cond_signals.items():
                pr = prep[(task.task_id, cond)]
                for sig in sigs:
                    for seed in seeds:
                        p = out_dir / "exp_a" / slug / sig / cond / f"{task.task_id}_s{seed}.json"
                        jobs.append(
                            (
                                p,
                                lambda t=task, c=cond, m=model, s=sig, sd=seed, st=pr: receiver.run_receiver_trial(
                                    task=t,
                                    condition=c,
                                    model=m,
                                    experiment="exp_a",
                                    signal=s,
                                    duty="discretion",
                                    seed=sd,
                                    prepared=st,
                                ),
                            )
                        )
        _run_jobs(jobs, _max_workers_for(model))
        backends.unload_ollama_model(model)
        print(f"[sweep] finished exp_a {model} (n_tasks={len(tasks)})", flush=True)


def _run_exp_b(
    tasks: list[Any],
    models: list[str],
    out_dir: Path,
    seeds: list[int],
    prep_cache: dict | None = None,
) -> None:
    cond_duties: dict[str, tuple[str, ...]] = {
        "clean": ("discretion", "narrow_ci_duty", "goal_duty"),
        "disclosed_partial": ("discretion", "narrow_ci_duty", "goal_duty"),
        "silent_partial": ("discretion", "narrow_ci_duty", "goal_duty", "no_ticket_control"),
    }
    prep = prep_cache or _prepare_all(tasks, ("clean", "disclosed_partial", "silent_partial"))
    for model in models:
        slug = _safe_slug(model)
        jobs: list[tuple[Path, Callable[[], dict[str, Any]]]] = []
        for task in tasks:
            for cond, duties in cond_duties.items():
                pr = prep[(task.task_id, cond)]
                for duty in duties:
                    inc_ticket = duty != "no_ticket_control"
                    for seed in seeds:
                        p = out_dir / "exp_b" / slug / duty / cond / f"{task.task_id}_s{seed}.json"
                        if duty == "discretion" and cond in ("clean", "silent_partial"):
                            src_p = out_dir / "exp_a" / slug / "neutral" / cond / f"{task.task_id}_s{seed}.json"
                            if not p.is_file() and src_p.is_file():
                                copied = json.loads(src_p.read_text(encoding="utf-8"))
                                copied["experiment"] = "exp_b"
                                copied["reused_from_exp_a"] = f"exp_a/{slug}/neutral/{cond}/{task.task_id}_s{seed}.json"
                                _write_json_atomic(p, copied)
                                continue
                        jobs.append(
                            (
                                p,
                                lambda t=task, c=cond, m=model, d=duty, inc=inc_ticket, sd=seed, st=pr: receiver.run_receiver_trial(
                                    task=t,
                                    condition=c,
                                    model=m,
                                    experiment="exp_b",
                                    signal="neutral",
                                    duty=d,
                                    include_ticket=inc,
                                    seed=sd,
                                    prepared=st,
                                ),
                            )
                        )
        _run_jobs(jobs, _max_workers_for(model))
        backends.unload_ollama_model(model)
        print(f"[sweep] finished exp_b {model} (n_tasks={len(tasks)})", flush=True)


def _prepare_exp_c_stages_1_2(
    tasks: list[Any],
    synth_models: list[str],
    out_dir: Path,
    conditions: tuple[str, ...] = ("clean", "silent_partial"),
    prep_cache: dict | None = None,
) -> dict[tuple[str, str, str], dict[str, Any]]:
    prep = prep_cache or _prepare_all(tasks, conditions)
    stage1_cache: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for adv in briefs.ADVISOR_PANEL:
        adv_slug = _safe_slug(adv)
        jobs: list[tuple[Path, Callable[[], dict[str, Any]]]] = []
        paths: list[tuple[str, str, Path]] = []
        for task in tasks:
            for cond in conditions:
                p = out_dir / "exp_c" / "stage1" / adv_slug / cond / f"{task.task_id}.json"
                paths.append((task.task_id, cond, p))
                jobs.append(
                    (
                        p,
                        lambda t=task, c=cond, a=adv, st=prep[(task.task_id, cond)]: briefs.run_stage1_advisor(t, c, a, prepared=st),
                    )
                )
        _run_jobs(jobs, _max_workers_for(adv))
        for tid, cond, p in paths:
            stage1_cache.setdefault((tid, cond), []).append(json.loads(p.read_text(encoding="utf-8")))
        backends.unload_ollama_model(adv)
        print(f"[sweep] finished exp_c_stage1 advisor={adv} (n_tasks={len(tasks)})", flush=True)

    stage2_cache: dict[tuple[str, str, str], dict[str, Any]] = {}
    for synth in sorted(set(synth_models)):
        s_slug = _safe_slug(synth)
        jobs = []
        s2_paths: list[tuple[str, str, Path]] = []
        for task in tasks:
            for cond in conditions:
                p = out_dir / "exp_c" / "stage2" / s_slug / cond / f"{task.task_id}.json"
                panel = stage1_cache[(task.task_id, cond)]
                s2_paths.append((task.task_id, cond, p))
                jobs.append(
                    (
                        p,
                        lambda t=task, c=cond, sm=synth, pnl=panel, st=prep[(task.task_id, cond)]: briefs.synthesize_briefs(t, c, sm, pnl, st),
                    )
                )
        _run_jobs(jobs, _max_workers_for(synth))
        for tid, cond, p in s2_paths:
            stage2_cache[(synth, tid, cond)] = json.loads(p.read_text(encoding="utf-8"))
        backends.unload_ollama_model(synth)
        print(f"[sweep] finished exp_c_stage2 synth={synth} (n_tasks={len(tasks)})", flush=True)
    return stage2_cache


def _run_exp_c_stage3(
    tasks: list[Any],
    pairings: list[tuple[str, str]],
    stage2_cache: dict[tuple[str, str, str], dict[str, Any]],
    out_dir: Path,
    seeds: list[int],
    conditions: tuple[str, ...] = ("clean", "silent_partial"),
    prep_cache: dict | None = None,
) -> None:
    prep = prep_cache or _prepare_all(tasks, conditions)
    for synth, dec in pairings:
        s_slug = _safe_slug(synth)
        d_slug = _safe_slug(dec)
        dec_family = backends.provider_for_model(dec)
        jobs: list[tuple[Path, Callable[[], dict[str, Any]]]] = []
        for task in tasks:
            for cond in conditions:
                st = prep[(task.task_id, cond)]
                s2 = stage2_cache[(synth, task.task_id, cond)]
                for arm in ("consensus_brief", "ungated_crux_brief", "gated_crux_brief"):
                    brief_txt = s2["briefs"][arm]
                    for seed in seeds:
                        p = out_dir / "exp_c" / "stage3" / f"{s_slug}__to__{d_slug}" / arm / cond / f"{task.task_id}_s{seed}.json"
                        jobs.append(
                            (
                                p,
                                lambda t=task, c=cond, dm=dec, a=arm, bt=brief_txt, gact=s2["gate_action"], hc=s2["stage1_hold_count"], sd=seed, pr=st, sm=synth: receiver.run_receiver_trial(
                                    task=t,
                                    condition=c,
                                    model=dm,
                                    experiment="exp_c",
                                    signal="neutral",
                                    duty="discretion",
                                    seed=sd,
                                    advisory_brief=bt,
                                    advisory_meta={
                                        "arm": a,
                                        "synth": sm,
                                        "decider_family": dec_family,
                                        "gate_action": gact,
                                        "stage1_hold_count": hc,
                                    },
                                    prepared=pr,
                                ),
                            )
                        )
        _run_jobs(jobs, _max_workers_for(dec))
        backends.unload_ollama_model(dec)
        print(f"[sweep] finished exp_c_stage3 {synth} -> {dec} (n_tasks={len(tasks)})", flush=True)


def _run_exp_c(
    tasks: list[Any],
    pairings: list[tuple[str, str]],
    out_dir: Path,
    seeds: list[int],
    conditions: tuple[str, ...] = ("clean", "silent_partial"),
    prep_cache: dict | None = None,
) -> None:
    prep = prep_cache or _prepare_all(tasks, conditions)
    synth_models = sorted({s for s, _ in pairings})
    stage2_cache = _prepare_exp_c_stages_1_2(tasks, synth_models, out_dir, conditions=conditions, prep_cache=prep)
    _run_exp_c_stage3(tasks, pairings, stage2_cache, out_dir, seeds=seeds, conditions=conditions, prep_cache=prep)


def _run_part2(tasks: list[Any], models: list[str], out_dir: Path, seeds: list[int]) -> None:
    for model in models:
        slug = _safe_slug(model)
        jobs: list[tuple[Path, Callable[[], dict[str, Any]]]] = []
        for task in tasks:
            for seed in seeds:
                p = out_dir / "part2" / slug / f"{task.task_id}_s{seed}.json"
                jobs.append((p, lambda t=task, m=model, sd=seed: worker.run_worker_trial(t, m, seed=sd)))
        _run_jobs(jobs, _max_workers_for(model))
        backends.unload_ollama_model(model)
        print(f"[sweep] finished part2 {model} (n_tasks={len(tasks)})", flush=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Run resumable RepoHandoff sweeps.")
    ap.add_argument("--suite", default="calibration", help="calibration | confirmatory | all | comma-separated task IDs")
    ap.add_argument("--out", required=True, help="Output directory (e.g. runs/smoke_v2)")
    ap.add_argument("--mode", default="smoke_v2", choices=["smoke_v2", "confirmatory_all", "exp_a", "exp_b", "exp_c", "part2"])
    ap.add_argument("--models", default="", help="Comma-separated models override")
    ap.add_argument("--seeds", default="0", help="Comma-separated integer seeds")
    args = ap.parse_args()

    out_dir = Path(args.out)
    os.environ["REPOHANDOFF_USAGE_LOG"] = str((out_dir.parent / "api_usage.jsonl").resolve())
    tasks = select_tasks(args.suite)
    if any(not t.is_calibration() for t in tasks) and not Path("HYPOTHESES.md").is_file():
        raise SystemExit("Refusing to run confirmatory tasks (T00..T35) before HYPOTHESES.md is locked.")

    seeds = [int(s.strip()) for s in args.seeds.split(",") if s.strip()]

    if args.mode == "smoke_v2":
        prep = _prepare_all(tasks, ("clean", "false_ci", "disclosed_partial", "silent_partial"))
        _run_exp_a(tasks, ["gemma4:latest", "gpt-6-luna"], out_dir, seeds=[0], prep_cache=prep)
        _run_exp_b(tasks, ["gemma4:latest", "gpt-6-luna"], out_dir, seeds=[0], prep_cache=prep)
        _run_exp_c(
            tasks,
            pairings=[("nemotron3:33b", "gemma4:latest"), ("nemotron3:33b", "gpt-6-luna")],
            out_dir=out_dir,
            seeds=[0],
            prep_cache=prep,
        )
        _run_part2(tasks, ["gemma4:latest", "gpt-5.4-nano", "gpt-6-luna"], out_dir, seeds=[0])
    elif args.mode == "confirmatory_all":
        balanced18 = [TASK_BY_ID[tid] for tid in BALANCED_18_IDS]
        prep = _prepare_all(tasks, ("clean", "false_ci", "disclosed_partial", "silent_partial"))
        stage2_box: dict[str, dict[tuple[str, str, str], dict[str, Any]]] = {}

        def _ollama_phase1() -> None:
            _run_exp_a(tasks, ["gemma4:latest", "nemotron3:33b"], out_dir, seeds=[0], prep_cache=prep)
            _run_exp_b(tasks, ["gemma4:latest", "nemotron3:33b"], out_dir, seeds=[0], prep_cache=prep)
            _run_part2(tasks, ["gemma4:latest", "nemotron3:33b"], out_dir, seeds=[0])
            _run_part2(balanced18, ["qwen3.6:27b-coding-mxfp8"], out_dir, seeds=[0])
            stage2_box["cache"] = _prepare_exp_c_stages_1_2(
                tasks, ["gemma4:latest", "nemotron3:33b"], out_dir, ("clean", "silent_partial"), prep_cache=prep
            )

        def _openai_phase1() -> None:
            _run_exp_a(tasks, ["gpt-5.4-nano", "gpt-6-luna"], out_dir, seeds=[0], prep_cache=prep)
            _run_exp_a(balanced18, ["gpt-6.1-sol"], out_dir, seeds=[0], prep_cache=prep)
            _run_exp_b(tasks, ["gpt-5.4-nano", "gpt-6-luna"], out_dir, seeds=[0], prep_cache=prep)
            _run_exp_b(balanced18, ["gpt-6.1-sol"], out_dir, seeds=[0], prep_cache=prep)
            _run_part2(tasks, ["gpt-5.4-nano", "gpt-6-luna"], out_dir, seeds=[0])
            _run_part2(balanced18, ["gpt-6.1-sol"], out_dir, seeds=[0])

        def _claude_phase1() -> None:
            _run_exp_a(tasks, ["claude-haiku-5-5"], out_dir, seeds=[0], prep_cache=prep)
            _run_exp_b(tasks, ["claude-haiku-5-5"], out_dir, seeds=[0], prep_cache=prep)
            _run_part2(tasks, ["claude-haiku-5-5"], out_dir, seeds=[0])

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futs = [pool.submit(_ollama_phase1), pool.submit(_openai_phase1), pool.submit(_claude_phase1)]
            for fut in futs:
                fut.result()

        stage2_cache = stage2_box["cache"]
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            futs = [
                pool.submit(
                    _run_exp_c_stage3,
                    tasks,
                    [("nemotron3:33b", "gemma4:latest"), ("gemma4:latest", "nemotron3:33b")],
                    stage2_cache,
                    out_dir,
                    [0],
                    ("clean", "silent_partial"),
                    prep,
                ),
                pool.submit(
                    _run_exp_c_stage3,
                    tasks,
                    [("nemotron3:33b", "gpt-5.4-nano"), ("nemotron3:33b", "gpt-6-luna")],
                    stage2_cache,
                    out_dir,
                    [0],
                    ("clean", "silent_partial"),
                    prep,
                ),
                pool.submit(
                    _run_exp_c_stage3,
                    tasks,
                    [("nemotron3:33b", "claude-haiku-5-5")],
                    stage2_cache,
                    out_dir,
                    [0],
                    ("clean", "silent_partial"),
                    prep,
                ),
            ]
            for fut in futs:
                fut.result()
    elif args.mode == "exp_a":
        models = [m.strip() for m in args.models.split(",") if m.strip()]
        _run_exp_a(tasks, models, out_dir, seeds=seeds)
    elif args.mode == "exp_b":
        models = [m.strip() for m in args.models.split(",") if m.strip()]
        _run_exp_b(tasks, models, out_dir, seeds=seeds)
    elif args.mode == "exp_c":
        deciders = [m.strip() for m in args.models.split(",") if m.strip()]
        pairings = [(s, d) for d in deciders for s in ("nemotron3:33b", "gemma4:latest") if s != d]
        _run_exp_c(tasks, pairings=pairings, out_dir=out_dir, seeds=seeds)
    elif args.mode == "part2":
        models = [m.strip() for m in args.models.split(",") if m.strip()]
        _run_part2(tasks, models, out_dir, seeds=seeds)


if __name__ == "__main__":
    main()
