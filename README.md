# What the Reviewer Is Told to Check: Instruction Scope, Notices, and Test-Passing Partial Work in Multi-Agent Code Handoffs

**Author:** Kenny Wang (`founder@cirwel.org`, ORCID `0009-0006-7544-2374`)

This repository contains the `RepoHandoff` benchmark, pre-registration protocol, raw confirmatory dataset (`6,012` JSON execution records, `5,616` unique, across `7` models from `5` developers), statistical analysis, a separate recount script, a label audit, figures, and the LaTeX manuscript (`paper/main.pdf`).

The repository and the locked protocol carry the working title *Prose Is Not a Gate*. The manuscript was retitled on 2026-11-20 to reflect the change in hold rates when a single reviewer instruction was rewritten.

---

## Findings

Revised 2026-11-20 after two rounds of outside review (`docs/REVIEWS.md` sections 4 and 5, `CLAIMS-LEDGER.md` sections 6 and 7). The hypotheses were locked in `HYPOTHESES.md` at commit `f7ec48c` before any confirmatory task ran. A second script recounts the reported counts from the raw records (`results/recount_check.txt`, `DISCREPANCIES: 0`).

1. **Experiment B (`H2`): changing the scope and verdict rule changes holds on scripted partials.**
   - Changing one sentence of the receiver's instruction from `goal_duty` (verify every ticket requirement) to `narrow_ci_duty` (verify CI passes and matches the report; merge if so) lowers holds on `silent_partial` patches from `147/180` to `20/180` (`-70.6 pp`, `36/36` concordant repositories, `p_sign_holm = 8.73e-11`), and in each of the 6 models (`p_holm < 0.05`).
   - Under the narrow sentence, `gpt-6-luna` and `gpt-6.1-sol` return `merge` for PRs whose notes disclose an omitted requirement (holding `2/36` and `0/18`). That is what the sentence says to do. Three other models, including `gpt-5.4-nano` from the same developer, hold all 36.
   - The two sentences differ in both the scope of the check and the dictated verdict. A post hoc arm (`attention_only_duty`: the same CI-only check with the verdict left open, four no-cost models, not pre-registered) removes the verdict rule and keeps the check, one draw per cell: `claude-haiku-5-5` and `qwen3.6` hold every silent partial again (`36/36`, `18/18`), while `gemma4` and `nemotron3` still hold none (`0/36` each; `nemotron3` rarely ran the tests at all). The arm cannot assign the effect to one clause.
   - Without the ticket (`H2c`), `silent_partial` holds fall by `74.4 pp`. The arm removes the ticket and also rewords the duty, so it cannot apportion the drop.

2. **Experiment A (`H1`): badge contrasts are non-significant; an accurate mismatch notice helps two receivers.**
   - On `silent_partial`, the two pre-registered badge contrasts are small and non-significant across the five core models: `H1a` `+3.3 pp` (`p_sign_holm = 0.2188`), `H1b` `+1.7 pp` (`p_sign_holm = 0.5811`). Several cells sit at ceiling or floor.
   - An accurate mismatch notice on `false_ci` raises holds from `133/180` to `179/180` (`+25.6 pp`, `36/36` concordant repositories), entirely through `nemotron3:33b` (`0/36` to `35/36`, the one non-hold being a parse error) and `gemma4:latest` (`25/36` to `36/36`). Both models also called `run_pytest` more often on these fixtures, from 0/36 to 22/36 for Nemotron and from 12/36 to 36/36 for Gemma. The experiment tested only an accurate mismatch notice.

3. **The `clean` label does not mean "conforms to the ticket".**
   - Two independent audits (Anthropic and OpenAI models, blind to receiver decisions, executable reproductions) agree that 11 of the 36 `clean` patches depart from their written tickets on inputs the oracle does not test. 11 more are disputed, 10 are ambiguous at most, and 4 drew no objection (`docs/CLEAN-LABEL-AUDIT.md`).
   - In Experiment A, 110 of 792 decisions on clean-labelled patches were holds; 73 of them fall on the 11 (an overlap by task; the blinded auditors did not see hold reasons). Of the remaining 37 holds, 36 were on disputed or ambiguous patches. The four unobjected patches drew one hold across 80 decisions. Hold counts and pooled contrasts that use the label are recomputed on the audited subsets in `results/clean_label_sensitivity.md`.

4. **Experiment C (`H3`): the three pre-registered contrasts on disagreement briefs are non-significant.**
   - At the Stage-3 decision, brief type makes no significant pooled difference (largest `+2.8 pp`, `p_sign_holm = 0.68`). Every decider had code tools in every arm. Reported in an appendix of the manuscript.
   - Both synthesizers populated a crux or unverified-premise field on all 36 clean-labelled patches. The gate cleared these fields on all 34 unanimously approved, test-passing patches. In the Gemma Stage-2 records, those 34 include nine of the 11 patches with agreed ticket deviations. All five terminal parse errors sit in one pairing, and three of them make up its only discordant pairs on `silent_partial`.
   - Exploratory: on the 25 tasks without an agreed departure, the ungated brief drew `10/125` clean holds against `0/125` for the gated brief.

5. **Part 2 (`H4`): 216 live coding-worker runs under a visible API freeze.**
   - Workers were told to leave the frozen requirement unimplemented and disclose it. `131/216` were classified as disclosed partials (the instructed outcome; 16 of them changed no file and said so); `7` passed both suites by getting around the syntactic freeze check; `5` edited a pre-existing test; `4` claimed completion while describing a workaround in their notes (the pre-registered `silent_partial` label, assigned by a keyword rule); `1` reported a pass that failed; `34` failed with disclosure and `34` did not finish.
   - Of the five test edits, two reported failing tests, two filed no report, and one (`gemma4 T01`) stripped the freeze test's assertions, passed, and said so in its notes. A digest check alone passes that one.
   - `CIDigestGate + TestIntegrityGate` flag every failing and unfinished run and every test edit the AST check can see (definitional), and pass `128/131` disclosed partials and `4/4` over-claims. All three blocked disclosed partials had a report mismatch. None of these gates checks implementation against the ticket.

**Limits.** One draw per cell; decoding settings were not uniform across backends; fixtures, tickets and oracles share one AI-assisted authoring process and were audited by models, not by an independent human; the Experiment B contrast is a bundled instruction change and the arm that removes its verdict rule is post hoc on four no-cost models; 396 of the 6,012 records are copies of Experiment A decisions reused as Experiment B baselines; all receivers and workers are LLMs; contributors in Experiments A to C are scripted.

---

## Repository Layout

- `paper/main.tex`, `paper/references.bib`, `paper/main.pdf`: Compiled LaTeX manuscript and verified bibliography (`28` entries).
- `repohandoff/`: Benchmark package (`tasks.py`, `task_bank/`, `sandbox.py`, `crypto.py`, `receiver.py`, `briefs.py`, `worker.py`, `prompts.py`, `backends.py`, `sweep.py`, `analyze.py`).
- `runs/confirmatory/`: Complete raw confirmatory JSON dataset (`6,012` records across `exp_a`, `exp_b`, `exp_c/stage1`, `exp_c/stage2`, `exp_c/stage3`, `part2`).
- `runs/exploratory/exp_b_attention/`: Post hoc Experiment B arm (486 records, four no-cost models). Not part of the confirmatory dataset or its recount.
- `results/`: Generated statistical tables (`tables.md`), machine-readable summary (`summary.json`), API cost ledger (`cost_summary.json`), recount check (`recount_check.txt`), clean-label sensitivity analysis (`clean_label_sensitivity.md`), and the post hoc arm table (`exploratory_attention_arm.md`).
- `figures/`: Figures (`fig2_signals_duties`, `fig3_workers`, `figA_briefs` in PDF and PNG).
- `scripts/`: Standalone verification and build scripts (`recount_independent.py`, `make_figures.py`, `check_manuscript_hygiene.py`, `verify_clean_label_audit.py`, `clean_label_sensitivity.py`, `run_exploratory_attention_arm.py`, `analyze_exploratory_attention_arm.py`).
- `tests/`: Offline unit test suite (`86` tests verifying all 40 repositories, AST integrity checks, sandboxing, spend guards, and statistical helpers).
- `HYPOTHESES.md`, `CLAIMS-LEDGER.md`, `docs/DESIGN-CRITIQUE.md`, `docs/REVIEWS.md`, `docs/reviews/`, `docs/CLEAN-LABEL-AUDIT.md`, `docs/audit/`, `docs/clean_label_audit.json`: Pre-registration record, claims mapping, design critique dispositions, review log, full cold-read reports, the fixture label audit, the two raw audit passes with their protocol, and the combined verdicts.

---

## Offline Reproduction

All analysis, independent counting, unit tests, figure generation, hygiene checks, and LaTeX builds run without API keys. Installing the Python requirements needs network access once; the PDF builds with `tectonic` (which downloads TeX packages on first use) or with a local `pdflatex` + `bibtex`:

```bash
# 1. Run offline unit test suite (86 tests)
python3 -m pip install -r requirements.txt
python3 -m pytest -q tests

# 2. Recompute summary tables and stats from raw JSON traces
# (written to a scratch directory: without the original usage log, the analyzer
#  would overwrite the archived cumulative cost figure with zero)
mkdir -p /tmp/repohandoff-check
python3 -m repohandoff.analyze runs/confirmatory \
  --out-md /tmp/repohandoff-check/tables.md \
  --out-json /tmp/repohandoff-check/summary.json \
  --cost-out /tmp/repohandoff-check/cost_summary.json

# 3. Verify zero-context independent stdlib recount (must report DISCREPANCIES: 0)
python3 scripts/recount_independent.py runs/confirmatory /tmp/repohandoff-check/summary.json

# 4. Regenerate figures and verify manuscript hygiene
python3 scripts/make_figures.py
python3 scripts/check_manuscript_hygiene.py

# 5. Re-execute the clean-label audit reproductions and recompute the sensitivity tables
PYTHONPATH=. python3 -B scripts/verify_clean_label_audit.py
python3 scripts/clean_label_sensitivity.py

# 6. Re-tabulate the post hoc Experiment B arm from its records
python3 scripts/analyze_exploratory_attention_arm.py

# 7. Build manuscript PDF (tectonic, or pdflatex + bibtex)
cd paper && tectonic main.tex
# or: pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex
```

---

## Scope & License

- **Scope:** All benchmark runs evaluate LLM-to-LLM software handoffs (one draw per cell; requested `temperature = 0.2`, `seed = 0`, not applied uniformly by every backend) in isolated Python micro-repositories without human-subjects claims.
- **License:** Apache License 2.0 ([LICENSE](LICENSE)).
