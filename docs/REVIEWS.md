# Review & Adversarial Critique Dispositions

This log documents all cross-family reviews conducted across the design, implementation, statistical audit, and manuscript revision phases of *Prose Is Not a Gate: Duty Narrowing, Verification Notices, and Programmatic Crux Gates in Multi-Agent Software Handoffs*.

---

## 1. Pre-Implementation Design Critique (Anthropic, Before Lock)

- **Reviewer / Method:** `claude:host-adapter` (`anthropic`, thorough effort) via `unitares-governance:consult`
- **Consultation ID:** `d2e9d95b-f160-40db-b03e-d7ff3f421e87` (`2026-11-17T06:15Z`)
- **Summary & Dispositions:** Recorded in [DESIGN-CRITIQUE.md](DESIGN-CRITIQUE.md). Led directly to separating calibration `C00..C03` from confirmatory `T00..T35` (`N = 36` across 12 domains), explicit `no_ticket_control`, matched fixed-position `PR Metadata:` headers, deterministic header matching across all 3 Exp C arms, and AST-based test-tampering detection prior to locking `HYPOTHESES.md` (`f7ec48c`).

---

## 2. Post-Draft Adversarial Critique (Anthropic)

- **Reviewer / Method:** `claude:host-adapter` (`anthropic`, thorough effort) via `unitares-governance:consult`
- **Consultation ID:** `f912a8c6-5c02-4948-b9d4-5bf87dc695aa` (`2026-11-17T17:26Z`)
- **Key Findings & Dispositions in Final Revision:**
  1. **Title & Abstract Scope (`A1`, `A2`, `F4`):** Updated manuscript title to foreground duty narrowing, verification notices, and programmatic crux gates accurately; placed `H1a`/`H1b` (`+3.3 pp`, `+1.7 pp`) and Stage-3 `H3a-c` (`+2.8 pp`) nulls explicitly alongside positive findings in the Abstract; replaced bare `"100%"` on small-`n` cells with exact fractions (`1/1`, `5/5`, `34/34`); paired `"Prose Is Not a Gate"` explicitly with syntactic gate omissions (`0/4` silent partial, `3/131` disclosed partial) and surface evasions (`7/216`).
  2. **Rule-Compliance Framing & Interpretive Nuance (`A3`, `A4`):** Reframed Exp B `H2b` as a rule-compliance inversion across evaluated models (two of which share the OpenAI family) and explicitly addressed why `narrow_ci_duty` induces locally compliant rubric behavior misaligned with principal intent (`goal_duty`).
  3. **Statistical Precision (`B1`–`B11`):** Named repository-level exact sign tests (`m = 3` Holm per family) as primary pooled test and Wilcoxon as secondary rank check; noted `p = 8.73e-11` as the two-sided sign-test floor at `36/36` concordant repositories; added clean-condition `FA`, Youden `Net J`, and low-prevalence PPV discussion for Exp B; clarified `0.5` Hautus continuity ceiling at `FA = 0%`; added approximate MDE (`~25 pp`) context for single-model nulls; verified exact `133/180` equality across Exp A `neutral` (`silent_partial` and `false_ci`) with per-model sums; proved `BALANCED_18` spans all 12 domains (`9 req_2`, `9 req_1` omitted) and kept pooled `Core 5` tests balanced at `N = 36`; explicitly labeled cross-experiment `nemotron3` Exp A (`2/36`) vs Exp C (`35/36`) comparison as exploratory.
  4. **Accounting, Retry & Parse-Error Sensitivity (`C1`–`C8`):** Pinned exact Ollama image hashes and API snapshot IDs; itemized `$1.43` pre-lock calibration spend (`$13.65` cumulative minus `$12.21` confirmatory); verified only `4` Stage-1/2 records used `attempt = 1` (`0` reached `attempt = 5`) and `8 / 5,436` (`0.15%`) receiver decisions ended in `parse_error` (conservatively scored as non-hold, leaving `H1` and `H2` invariant under flip sensitivity); clarified `scripts/recount_independent.py` verifies arithmetic aggregation rather than semantic annotation reliability.
  5. **Construct, Threat-Model, & Field-Study Guardrails (`D1`–`D6`, `E1`–`E2`, `F1`–`F3`):** Reclassified the `7/216` `"complete"` Part 2 outcomes explicitly as `syntactic freeze evasions` (`**kwargs`, `lambda`, `__getattr__`); proved `apply_programmatic_gate` used zero oracle (`35/36` `>= 2` Stage-1 holds plus `1/36` `T05` solitary `qwen3.6` missing-function catch); framed `gemma4 T01` `TestIntegrityGate` catch as an illustrative `n = 1` boundary case; stated the non-adaptive threat model; disclosed AI-assisted task authoring; and scoped Section 6 strictly as descriptive incidents from a private, author-operated deployment (`cirwel/fleet-ops`) with no efficacy claims.

---

## 3. Independent Second-Family Verification Audit (OpenAI)

- **Reviewer / Method:** OpenAI Codex CLI (`model: gpt-6-astra`, `reasoning effort: xhigh`, `sandbox: read-only`, session `01a1ea8b-c9d1-7640-b71d-501dd6dc953c`, `2026-11-17T17:26Z`) inspecting `CLAIMS-LEDGER.md`, `HYPOTHESES.md`, `results/tables.md`, `results/recount_check.txt`, `results/summary.json`, `paper/main.tex`, `paper/references.bib`, and `scripts/recount_independent.py`.
- **Completed Checks:**
  1. **Independent Holm step-down arithmetic audit:** Verified every per-unit (`per_unit` McNemar) and `repo_clustered` (`p_sign_holm`, `p_wilcoxon_holm`) adjusted p-value across `exp_a`, `exp_b`, and `exp_c` in `results/summary.json`: **PASS (0 mismatches)**.
  2. **Citation resolution audit:** Verified every `\cite*` key in `paper/main.tex` resolves cleanly against `@entry` definitions in `paper/references.bib`: **28 cited, 28 defined, 0 missing**.
  3. **Raw trace & git-diff spot checks:** Inspected `exp_a`/`exp_b`/`exp_c` raw records (`T08_s0.json`, `T17_s0.json`), verified `git diff HYPOTHESES.md` pre/post lock, and checked citation sources.
- **Shortfall Disclosure:** `codex exec` under `xhigh` reasoning hit the 180s wall-clock CLI command timeout (`exit 124`) before emitting final formatted prose bullets, and resuming with tool-suppression exited cleanly without printing new commentary. Per repository review rules, the verified programmatic checks completed in that second-family session are retained and the CLI timeout shortfall is recorded transparently without blocking closeout.
