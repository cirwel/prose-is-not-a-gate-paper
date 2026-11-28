# Review & Adversarial Critique Dispositions

(The manuscript was retitled on 2026-11-20; see section 5. Earlier sections keep the working title.)

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

---

## 4. Pre-Release Cold Reads and Fixture Audit (2026-11-20)

- **OpenAI cold read:** Codex CLI (`model: gpt-6.2-sol`, `sandbox: read-only`), complete this time; the session in section 3 had timed out before reporting. Full text: [reviews/2026-11-20-cold-read-gpt-6.2-sol.md](reviews/2026-11-20-cold-read-gpt-6.2-sol.md). Score `2.5/5`, "major revision before minting a DOI". It reproduced the tables and statistics from the raw records and objected to what the paper said they establish.
- **Anthropic cold read:** `claude-fable-5-2`, reading the manuscript, lock, prompts and worker harness. Main findings: Part 2 reported the instructed outcome (disclosed partial) as a worker failure; the Stage-2 `36/36` and `34/34` figures are prompt compliance and a restatement of the gate rule; `H2c` is a control with an expected direction; the field section was presented as evidence.
- **Fixture audit:** [CLEAN-LABEL-AUDIT.md](CLEAN-LABEL-AUDIT.md). 7 of the 22 clean fixtures that drew a hold in Experiment A depart from their written tickets; 59 of 110 holds cite a reproduced departure.
- **Reference check:** all 28 bibliography entries verified against arXiv, Crossref, RFC Editor or the cited page. Four corrected (a missing ToolEmu author, a misspelled MASK author, two URLs that pointed at homepages).
- **Dispositions.** Every point from both reads was checked against the code and records before being applied; each is listed in `CLAIMS-LEDGER.md` section 6. Applied: abstract, introduction, results framing, figure text, captions, methods disclosures (record reuse, cost, decoding, post-lock scoring rules), related-work sentences, design rules, bibliography. Not done, and stated as limits in the manuscript: repeated seeds, a blinded multi-annotator label adjudication, an audit of clean holds outside Experiment A, a freeze-free worker control, and a repository-clustered interval for Part 2. The title was left unchanged. No confirmatory data, hypothesis or statistic changed.

---

## 5. Five-Seat Review, Decision Ballot and Second Revision (2026-11-20)

**Review of the first revision.** Five independent reads, none of which changed the repository:

| Seat | Family | Method | Outcome |
|---|---|---|---|
| Ground truth | `anthropic` (`claude-fable-5-2`) | Own script over the raw records | 32 of 32 recomputed items match the manuscript; all 7 first-audit fixture deviations reproduce. Not checked: Wilson intervals, Wilcoxon and per-model Holm values, tool-call rates, the cumulative spend figure |
| Code review | `anthropic` (`claude-fable-5-2`) | Harness and statistics code | Statistics code correct. `silent_partial` in Part 2 is a keyword-rule label; all 5 Experiment C parse errors sit in one pairing; 2 of the 5 "tampering" runs filed no report; the AST test check ignores `conftest.py`, pytest configuration and module-level skips |
| Argument | `anthropic` (`claude-fable-5-2`) | Manuscript against its own evidence | Title contradicted by Experiment B; the four-layer stack is a frame; rules 3 to 5 unsupported; six internal contradictions |
| Consult | `openai` (Codex host) | Abstract, rules and method notes inline | `3/5`, release after named edits |
| Consult | `google` (Antigravity host) | Same material | `2/5`, needs more work: audit all fixtures, disentangle or reframe Experiment B, retitle |

The consult hosts cannot read files, so those two seats judged from text supplied inline.

**Decision ballot.** The author delegated the open decisions to the panel. Three seats voted (one per family: an Anthropic subagent reading the repository, and the OpenAI and Google consult hosts from an inline brief). All three chose the same option on every item:

| Decision | Outcome (3 of 3) |
|---|---|
| Title | *What the Reviewer Is Told to Check: Instruction Scope, Notices, and Test-Passing Partial Work in Multi-Agent Code Handoffs* |
| Experiment C | One paragraph in the body, full report in an appendix (not removed: it was pre-registered) |
| Field anecdotes and rule 5 | Deleted from the manuscript |
| Four-layer stack and signal-detection values | Table 1 kept as a by-construction setup; stack dropped as a contribution; architecture figure dropped; signal-detection values moved to an appendix |
| Experiment B disentangling arm | Run post hoc on the four no-cost models, labelled exploratory, and reframe Experiment B as a bundled instruction change regardless |
| Clean-label ground truth | Audit all 36 with two independent passes from different families, executable reproductions, a per-task table, and a sensitivity analysis on audited subsets; fixtures and records unchanged |
| Rules | Keep only what has experimental support, as scoped observations |

Vetoes raised and honored: no claim that Experiment B shows narrowed attention specifically; no hold on a clean-labelled patch called a false alarm; no construction-defined result presented as a measurement; the four Part 2 "silent" labels and five "tampering" labels not presented as verified concealment; the locked protocol still traceable under its working title.

**What was done.** Each ballot outcome was carried out (`CLAIMS-LEDGER.md` section 7 lists the changed statements).

- **Label audit.** `docs/CLEAN-LABEL-AUDIT.md`. Passes by `claude-fable-5-2` and `gpt-6.2-sol`, each blind to receiver decisions. 11 of 36 clean patches deviate by agreement of both, 11 are disputed, 10 ambiguous, 4 unobjected. All reproductions re-execute (`scripts/verify_clean_label_audit.py`).
- **Sensitivity analysis.** `results/clean_label_sensitivity.md`.
- **Post hoc arm.** `runs/exploratory/exp_b_attention/`, `results/exploratory_attention_arm.md`.
- **Part 2 labels.** The ten reports behind `H4b` were read individually; the manuscript now describes what each says.
- **Not done.** No fixture was repaired and no experiment re-run on repaired fixtures. The arm does not include `gpt-6-luna` or `gpt-6.1-sol` (paid backends). No human adjudicated the audit. Repeated seeds, a freeze-free worker control and a repository-clustered interval for Part 2 remain undone, as in section 4.

---

## 6. Final Reads of the Rendered PDF (2026-11-21)

The author delegated the last read of the PDF to two model families outside the one that revised the manuscript. Each read all 22 rendered pages as images, with the extracted text alongside.

| Reader | Family | Access | Outcome |
|---|---|---|---|
| `gpt-6.2-sol` (Codex CLI, read-only) | `openai` | Page images, extracted text, repository | `3.5/5`, ready after the listed fixes. [Report](reviews/2026-11-21-pdf-read-gpt-6.2-sol.md) |
| `Gemini 4 Neon` (Antigravity CLI, sandboxed) | `google` | Page images and extracted text only | `3.5/5`, ready after the listed fixes. [Report](reviews/2026-11-21-pdf-read-gemini-4-neon.md) |

Each finding was checked against the records before it was applied.

**Applied.**

- Rendering: a file path that ran off the page in Appendix C, two overfull lines in the reproducibility section, Table 9's width, hyphens inserted into two identifiers, Python quotes collapsed into typographic ones in the audit table, an unclosed quotation in the Table 5 caption, a citation printed without brackets, missing PDF title and author metadata, small figure text, and a figure panel that left out the seven runs that passed both suites.
- The paper named no location for its materials. It now gives the repository URL and the release.
- The mismatch-notice result said the two local models "rarely ran the tests themselves" and that a notice "can substitute for a check". The records show both models ran the tests more often with the notice (`nemotron3` on 0/36 then 22/36 false-CI trials, `gemma4` on 12/36 then 36/36), and the text now says so.
- Table 1 showed `TestIntegrityGate` as "n/a" on `false_ci`. Computed from the fixture preparation, it flags 8 of the 36 `false_ci` patches, which also loosen or change a legacy test (`T02`, `T04`, `T10`, `T11`, `T18`, `T21`, `T33`, `T35`). The table and the fixture description now state it.
- The abstract's count of 16 disclosed partials that changed no file was not in the body; it is now, by model. The abstract also says how the `disclosed_partial` label is assigned and which 3 of the 131 the digest check blocked.
- The oracle exit code 2 is no longer called a collection error outright; the text gives the likely cause and says the archive cannot confirm it per run.
- Abstract wording: the Experiment B result is introduced as a comparison of two instruction sentences, counts are given as decisions, not patches; both badge contrasts are named with their direction; the post hoc arm states that one of its four models was not an original receiver.
- `H3a` to `H3c` are defined where first used; Youden's `J` is in Table 7; `Dis_Fail` and `Unfin` are defined in the Table 5 caption; the Table 5 column "Evaded" is now "Both_Pass"; the `H2b` difference carries the same sign as `H2a` and `H2c`; `H3a` on the audited subset is reported next to `H3b`.
- Smaller corrections: tool-call counts that used a 36-task denominator for an 18-task model, the description of what Stage-1 advisors see, the reason the Experiment C stages overlap, "redundant" removed from a tool-call count, "Part 1" and "Stage-1/2" used before definition, abbreviations expanded at first use, and sentences that read as revision notes.
- Bibliography: RFC 9162 added and cited, published venues added to five arXiv entries, journal details added to one `Science` entry, a title capitalisation fixed. 29 entries.

**Not applied.**

- Moving file paths out of table captions into one availability section: the paths are how a reader finds each table's source, and the repository is now linked.
- Removing `CLAIMS-LEDGER.md` and this file from the availability statement, and removing the retry, cost and deviation bookkeeping from the methods: they are disclosures and stay.
- Dated snapshot identifiers for three hosted models: none was recorded, and the paper now says so.
- Volume and page details for the 2026 `Science` entry, DOIs for three older journal articles, and a uniform author-list length: left as they are; every entry has a working identifier.
- Larger type in the dense tables: they are scaled to the text width and legible at page size on screen.

**Fix check.** `gpt-6.2-sol` then read the 23 rebuilt pages and the diff: no new rendering defect, and four wording points (the abstract's "largest effect", the `Unfin` definition, which report field the three blocked partials set, and a table reference), all applied. The Google reader did not re-read, and the last four edits were not re-read by anyone.

