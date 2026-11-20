#!/usr/bin/env python3
"""Re-execute the reproductions from the two clean-label audit passes and write the combined verdicts.

Inputs:  docs/audit/pass_*.json (one file per audit pass, 36 rows each, as the auditors returned them)
Outputs: docs/clean_label_audit.json, and a per-task listing on stdout.

Final verdict per task:
  DEVIATES   both passes independently returned DEVIATES, and for each the main reproduction is a valid
             expression that, run here against the clean patch, gives the result the auditor recorded
  DISPUTED   exactly one pass returned DEVIATES
  AMBIGUOUS  no pass returned DEVIATES and at least one returned AMBIGUOUS
  CONFORMS   both passes returned CONFORMS

What this script establishes is that the recorded behaviour of the patch is real. Whether that behaviour
departs from the ticket is the auditors' reading of the ticket text, quoted in each row; it is not recomputed.

Run from the repository root: PYTHONPATH=. python3 -B scripts/verify_clean_label_audit.py
"""
from __future__ import annotations

import json
import math
import sys
from collections import OrderedDict
from datetime import date, datetime, timedelta
from pathlib import Path

sys.dont_write_bytecode = True
sys.setrecursionlimit(1000)
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from repohandoff.tasks import TASK_BY_ID  # noqa: E402


def observe(task_id: str, expr: str) -> str:
    t = TASK_BY_ID[task_id]
    ns: dict = {}
    exec(t.patch_clean[f"src/{t.module_name}.py"], ns)
    ns.update(OrderedDict=OrderedDict, date=date, datetime=datetime, timedelta=timedelta, Path=Path, math=math)
    try:
        return repr(eval(expr, ns))[:200]
    except Exception as e:  # the exception is the observation
        return f"raises {type(e).__name__}({str(e)[:120]!r})"


INVALID = ("raises NameError", "raises SyntaxError", "raises ImportError", "raises ModuleNotFoundError")


def _norm(x: str) -> str:
    return "".join(x.split()).replace('"', "'").lower()


def reproduces(observed: str, recorded: str) -> bool:
    """The rerun gives what the auditor wrote down: same value, or the same exception type."""
    if not observed or observed.startswith(INVALID):
        return False
    if observed.startswith("raises "):
        return observed.split("(")[0].split()[1].lower() in recorded.lower()
    o = _norm(observed)
    return o[:60] in _norm(recorded)


def main() -> None:
    passes = {}
    for p in sorted((ROOT / "docs" / "audit").glob("pass_*.json")):
        fam = p.stem.split("_")[1]
        passes[fam] = {r["task"]: r for r in json.loads(p.read_text())}
    fams = sorted(passes)
    assert len(fams) == 2, fams
    out = {}
    for i in range(36):
        tid = f"T{i:02d}"
        vs = [passes[f][tid]["verdict"] for f in fams]
        obs = {}
        for f in fams:
            r = passes[f][tid]
            expr = (r.get("repro") or "").strip()
            obs[f] = observe(tid, expr) if expr else ""
            if r["verdict"] == "DEVIATES":
                assert reproduces(obs[f], str(r.get("actual", ""))), (tid, f, expr, obs[f], r.get("actual"))
        if vs.count("DEVIATES") == 2:
            final = "DEVIATES"
        elif vs.count("DEVIATES") == 1:
            final = "DISPUTED"
        elif "AMBIGUOUS" in vs:
            final = "AMBIGUOUS"
        else:
            final = "CONFORMS"
        row = {"final": final, "passes": {}}
        for f in fams:
            r = passes[f][tid]
            expr = (r.get("repro") or "").strip()
            row["passes"][f] = {
                "verdict": r["verdict"],
                "ticket_quote": r.get("ticket_quote", ""),
                "repro": expr,
                "observed_here": obs[f],
                "recorded_by_auditor": str(r.get("actual", "")),
                "required_per_auditor": r.get("required", ""),
            }
        out[tid] = row
        print(f"{tid} {final:9s} " + " | ".join(f"{f}:{row['passes'][f]['verdict']}" for f in fams))
        for f in fams:
            pr = row["passes"][f]
            if pr["repro"]:
                print(f"    [{f}] {pr['repro']}\n        -> {pr['observed_here']}")
    counts = {k: sum(v["final"] == k for v in out.values()) for k in ("DEVIATES", "DISPUTED", "AMBIGUOUS", "CONFORMS")}
    print(counts)
    (ROOT / "docs" / "clean_label_audit.json").write_text(json.dumps({"families": fams, "counts": counts, "tasks": out}, indent=1, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
