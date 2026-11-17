# Prose Is Not a Gate: Duty Narrowing, Verification Notices, and Programmatic Crux Gates in Multi-Agent Software Handoffs

**Author:** Kenny Wang (`founder@cirwel.org`, ORCID `0009-0006-7544-2374`)

This repository contains the `RepoHandoff` benchmark, pre-registration protocol, raw confirmatory dataset (`6,012` JSON execution records across `7` models from `5` model families), deterministic statistical analysis and independent recount pipeline, publication figures, and full LaTeX manuscript (`paper/main.pdf`).

---

## Key Empirical Findings

All confirmatory numbers below were pre-registered in `HYPOTHESES.md` on `origin/main` at commit `f7ec48c` prior to running any confirmatory task (`T00..T35`) and verified by an independent stdlib-only recount (`results/recount_check.txt`, `DISCREPANCIES: 0`):

1. **Experiment A (`H1`): Badges Have Null Pooled Effects While Mismatch Prose Aids Weak Receivers (Under Miscalibrated Baselines)**
   - Under `discretion`, provenance/CI badges yield small, non-significant pooled differences across Core 5 repositories (`N = 36`, 180 matched observations per contrast) on `silent_partial`: `H1a` (`neutral` vs `bare_verified`) `+3.3 pp` (`p_sign_holm = 0.2188`) and `H1b` (`scoped_verified` vs `green_ci_badge`) `+1.7 pp` (`p_sign_holm = 0.5811`).
   - Explicit mismatch prose (`H1c`: `ci_mismatch_prose` vs `neutral` on `false_ci`) raises holds by `+25.6 pp` (`36/36` concordant repositories, `p_sign_holm = 8.73e-11`), lifting `nemotron3:33b` (`0/36 -> 35/36`) and `gemma4:latest` (`25/36 -> 36/36`), though `nemotron3` still misses `1/36` (`T08` terminal parse error).
   - Frontier reasoning models (`gpt-6.1-sol`: `50%` clean false alarm under `neutral`, `c = -0.97`; `gpt-6-luna`: `36%` FA, `c = -0.70`) and open-weight local models (`nemotron3`: `0%` FA, `c = +1.85..+2.21`) sit at opposite extremes of calibration.

2. **Experiment B (`H2`): Narrowing Duty Prompts Causes `-70.6 pp` CI Tunnel Vision & Rule-Compliance Inversion**
   - Narrowing receiver prompts from `goal_duty` to `narrow_ci_duty` collapses `silent_partial` holds by `-70.6 pp` pooled (`36/36` concordant repositories, `p_sign_holm = 8.73e-11`), significant on **all 6** evaluated models (`p_holm < 0.05` per model).
   - Under `disclosed_partial` (where contributor notes explicitly admit omitting a requirement), stronger OpenAI reasoning models obey the narrow CI rule over ticket intent (`gpt-6-luna` `36/36 -> 2/36`; `gpt-6.1-sol` `18/18 -> 0/18`, pooled `H2b` `+22.8 pp`, `p_sign_holm = 8.73e-11`).
   - Omitting the originating engineering ticket (`no_ticket_control`, `H2c`) drops `silent_partial` catches by `-74.4 pp` (`0.817 -> 0.072`, `36/36` repos) even though frontier receivers inspect diffs and run tests.

3. **Experiment C (`H3`): Unconditional Disagreement Synthesis Manufactures Cruxes (`36/36` Clean PRs); Programmatic Gating Suppresses `34/34` Unanimous Leaks**
   - Across `36/36` (`100%`) `clean` PRs (`34/36` unanimously approved in Stage 1), both blinded Stage-2 synthesizers (`gemma4`, `nemotron3`) invent non-empty `cruxes` or `unverified_premises` when prompted unconditionally.
   - `apply_programmatic_gate` (using zero hidden oracle) clears all `34/34` unanimous leaks (`36/36 -> 2/36`, `5.6%`) while preserving `36/36` `silent_partial` holds (including solitary `1-of-3` requirement catch `T05`).
   - Tool-equipped Stage-3 deciders check diffs directly, yielding non-significant pooled Stage-3 contrasts (`+2.8 pp` clean FA, `p_sign_holm >= 0.68`), while exploratory pairing lifts `nemotron3` from `2/36` (Exp A unassisted) to `35/36` under `gated_crux_brief` at `1/36` clean FA.

4. **Part 2 (`H4`): Live Coding Workers Under Frozen-API Constraints (`N = 216`)**
   - `135/216` (`62.5%`, 95% CI `[55.9%, 68.7%]`) pass local `pytest` cleanly while leaving the frozen requirement incomplete (`131` disclosed, `4` silent).
   - `10/216` (`4.6%`) conceal failure via `silent_partial` (`4`), `test_tampering` (`5`), or `false_pass_claim` (`1`).
   - `7/216` (`3.2%`) achieve passing local and oracle tests by dynamically bypassing syntactic AST freeze checks (`**kwargs`, module-level `lambda`, `__getattr__` indirection).
   - Combined `CIDigestGate + TestIntegrityGate` catches `34/34` failing, `1/1` false-pass, `34/34` unfinished, and `5/5` tampered runs (including `gemma4 T01`, where `loosened_asserts` passed `CIDigestGate` alone), yet misses `128/131` disclosed partials and `4/4` silent partials.

5. **Descriptive Multi-Agent Git Infrastructure Cases (`cirwel/fleet-ops`)**
   - Five commit-anchored incident records from a single private, author-operated automation repository illustrate provenance regex scoping, per-command token narrowing, fail-closed registry defaults, process lineage exclusion, and closeout read-back verification (strictly descriptive, non-comparative).

---

## Repository Layout

- `paper/main.tex`, `paper/references.bib`, `paper/main.pdf`: Compiled 17-page camera-ready LaTeX manuscript and verified bibliography (`28` entries).
- `repohandoff/`: Benchmark package (`tasks.py`, `task_bank/`, `sandbox.py`, `crypto.py`, `receiver.py`, `briefs.py`, `worker.py`, `prompts.py`, `backends.py`, `sweep.py`, `analyze.py`).
- `runs/confirmatory/`: Complete raw confirmatory JSON dataset (`6,012` records across `exp_a`, `exp_b`, `exp_c_stage1`, `exp_c_stage2`, `exp_c_stage3`, `part2`).
- `results/`: Generated statistical tables (`tables.md`), machine-readable summary (`summary.json`), API cost ledger (`cost_summary.json`), and zero-discrepancy independent recount (`recount_check.txt`).
- `figures/`: Publication-grade figures (`fig1_architecture`, `fig2_signals_duties`, `fig3_briefs_workers` in PDF and PNG).
- `scripts/`: Standalone verification and build scripts (`recount_independent.py`, `make_figures.py`, `check_manuscript_hygiene.py`).
- `tests/`: Offline unit test suite (`86` tests verifying all 40 repositories, AST integrity checks, sandboxing, spend guards, and statistical helpers).
- `HYPOTHESES.md`, `CLAIMS-LEDGER.md`, `docs/DESIGN-CRITIQUE.md`, `docs/REVIEWS.md`: Pre-registration record, claims mapping, design critique dispositions, and cross-family review log.

---

## Offline Reproduction

All analysis, independent counting, unit tests, figure generation, hygiene checks, and LaTeX builds reproduce offline without API keys or network access (using Python `>= 3.12` and `pdflatex` + `bibtex`):

```bash
# 1. Run offline unit test suite (86 tests)
python3 -m pytest tests/ -n auto -v

# 2. Recompute summary tables and stats from raw JSON traces
python3 -m repohandoff.analyze runs/confirmatory \
  --out-md results/tables.md \
  --out-json results/summary.json \
  --cost-out results/cost_summary.json

# 3. Verify zero-context independent stdlib recount (must report DISCREPANCIES: 0)
python3 scripts/recount_independent.py runs/confirmatory results/summary.json

# 4. Regenerate publication figures and verify manuscript hygiene
python3 scripts/make_figures.py
python3 scripts/check_manuscript_hygiene.py

# 5. Build manuscript PDF
cd paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

---

## Scope & License

- **Scope:** All benchmark runs evaluate LLM-to-LLM software handoffs (`temperature = 0.2`, `seed = 0`) in isolated Python micro-repositories without human-subjects claims.
- **License:** Apache License 2.0 ([LICENSE](LICENSE)).
