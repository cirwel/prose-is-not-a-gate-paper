# Prose Is Not a Gate: Duty Narrowing, Verification Notices, and Programmatic Crux Gates in Multi-Agent Software Handoffs

**Author:** Kenny Wang (`founder@cirwel.org`, ORCID `0009-0006-7544-2374`)

This repository contains the `RepoHandoff` benchmark, pre-registration protocol, raw confirmatory dataset (`6,012` JSON execution records, `5,616` unique, across `7` models from `5` developers), statistical analysis, a separate recount script, figures, and the LaTeX manuscript (`paper/main.pdf`).

---

## Findings

Revised 2026-11-20 after an outside cold read and a fixture audit (`docs/reviews/`, `docs/CLEAN-LABEL-AUDIT.md`, `CLAIMS-LEDGER.md` section 6). The hypotheses were locked in `HYPOTHESES.md` at commit `f7ec48c` before any confirmatory task ran. A second script recounts the reported counts from the raw records (`results/recount_check.txt`, `DISCREPANCIES: 0`).

1. **Experiment A (`H1`): badges show no pooled effect; an accurate mismatch notice helps weak receivers.**
   - On `silent_partial`, the two pre-registered badge contrasts are small and non-significant across the five core models: `H1a` `+3.3 pp` (`p_sign_holm = 0.2188`), `H1b` `+1.7 pp` (`p_sign_holm = 0.5811`). Several cells sit at ceiling or floor.
   - An accurate mismatch notice on `false_ci` raises holds by `+25.6 pp` (`36/36` concordant repositories, `p_sign_holm = 8.73e-11`), driven by `nemotron3:33b` (`0/36` to `35/36`) and `gemma4:latest` (`25/36` to `36/36`). A spurious notice on clean patches was not tested.
   - Receivers held 110 of 792 patches labelled `clean`. An audit found that 59 of those holds cite a reproduced departure of the patch from its written ticket (7 of the 36 clean fixtures deviate on an edge case the oracle does not exercise). These are holds on clean-labelled patches, not false alarms.

2. **Experiment B (`H2`): narrowing the receiver's duty to CI agreement lowers detection.**
   - Changing the prompt from `goal_duty` to `narrow_ci_duty` lowers `silent_partial` holds by `70.6 pp` pooled (`36/36` concordant repositories, `p_sign_holm = 8.73e-11`), and in each of the 6 models (`p_holm < 0.05`).
   - Under the narrow prompt, two models from one developer merge PRs whose notes disclose an omitted requirement (`gpt-6-luna` holds `36/36` then `2/36`; `gpt-6.1-sol` `18/18` then `0/18`). The prompt tells them to merge when tests match, so this is compliance with the instruction as written. Three other models hold all 36.
   - Without the ticket (`H2c`), `silent_partial` holds fall by `74.4 pp`. This is a control with an expected direction; the arm also rewords the duty.

3. **Experiment C (`H3`): the three pre-registered contrasts on disagreement briefs are null.**
   - At the Stage-3 decision, brief type makes no significant pooled difference (largest `+2.8 pp`, `p_sign_holm = 0.68`). Every decider had code tools in every arm.
   - Descriptively, a synthesizer asked to surface disagreement returns non-empty crux fields on `36/36` clean PRs, which is what its prompt asks for. A rule that clears those fields when the panel is unanimous and tests pass removes `34/34` by construction.

4. **Part 2 (`H4`): 216 live coding-worker runs under a visible API freeze.**
   - Workers were told to leave the frozen requirement unimplemented and disclose it. `131/216` did so with green local tests; `4` left it out silently; `5` altered pre-existing tests; `1` reported a pass that failed; `7` completed the requirement by getting around the syntactic freeze check; `34` failed with disclosure and `34` did not finish.
   - `CIDigestGate + TestIntegrityGate` flag every failing, unfinished and tampered run (the tampering result is definitional) and pass `128/131` disclosed and `4/4` silent partials. A green local suite does not separate a disclosed partial from a complete change.

5. **Descriptive incident records.** Five incidents from one private, author-operated repository illustrate the taxonomy. They are not evidence for the experimental claims and readers cannot inspect the commits.

**Limits.** One draw per cell; decoding settings were not uniform across backends; fixtures, tickets and oracles share one AI-assisted authoring process; 396 of the 6,012 records are copies of Experiment A decisions reused as Experiment B baselines; all receivers and workers are LLMs.

---

## Repository Layout

- `paper/main.tex`, `paper/references.bib`, `paper/main.pdf`: Compiled LaTeX manuscript and verified bibliography (`28` entries).
- `repohandoff/`: Benchmark package (`tasks.py`, `task_bank/`, `sandbox.py`, `crypto.py`, `receiver.py`, `briefs.py`, `worker.py`, `prompts.py`, `backends.py`, `sweep.py`, `analyze.py`).
- `runs/confirmatory/`: Complete raw confirmatory JSON dataset (`6,012` records across `exp_a`, `exp_b`, `exp_c_stage1`, `exp_c_stage2`, `exp_c_stage3`, `part2`).
- `results/`: Generated statistical tables (`tables.md`), machine-readable summary (`summary.json`), API cost ledger (`cost_summary.json`), and recount check (`recount_check.txt`).
- `figures/`: Figures (`fig1_architecture`, `fig2_signals_duties`, `fig3_briefs_workers` in PDF and PNG).
- `scripts/`: Standalone verification and build scripts (`recount_independent.py`, `make_figures.py`, `check_manuscript_hygiene.py`).
- `tests/`: Offline unit test suite (`86` tests verifying all 40 repositories, AST integrity checks, sandboxing, spend guards, and statistical helpers).
- `HYPOTHESES.md`, `CLAIMS-LEDGER.md`, `docs/DESIGN-CRITIQUE.md`, `docs/REVIEWS.md`, `docs/reviews/`, `docs/CLEAN-LABEL-AUDIT.md`: Pre-registration record, claims mapping, design critique dispositions, review log, full cold-read reports, and the fixture label audit.

---

## Offline Reproduction

All analysis, independent counting, unit tests, figure generation, hygiene checks, and LaTeX builds reproduce offline without API keys or network access (using Python `>= 3.12` and `pdflatex` + `bibtex`):

```bash
# 1. Run offline unit test suite (86 tests)
python3 -m pip install -r requirements.txt
python3 -m pytest -q tests

# 2. Recompute summary tables and stats from raw JSON traces
python3 -m repohandoff.analyze runs/confirmatory \
  --out-md results/tables.md \
  --out-json results/summary.json \
  --cost-out results/cost_summary.json

# 3. Verify zero-context independent stdlib recount (must report DISCREPANCIES: 0)
python3 scripts/recount_independent.py runs/confirmatory results/summary.json

# 4. Regenerate figures and verify manuscript hygiene
python3 scripts/make_figures.py
python3 scripts/check_manuscript_hygiene.py

# 5. Reproduce the clean-label audit checks (docs/CLEAN-LABEL-AUDIT.md)
PYTHONPATH=. python3 scripts/audit_clean_labels.py

# 6. Build manuscript PDF (tectonic, or pdflatex + bibtex)
cd paper && tectonic main.tex
```

---

## Scope & License

- **Scope:** All benchmark runs evaluate LLM-to-LLM software handoffs (one draw per cell; requested `temperature = 0.2`, `seed = 0`, not applied uniformly by every backend) in isolated Python micro-repositories without human-subjects claims.
- **License:** Apache License 2.0 ([LICENSE](LICENSE)).
