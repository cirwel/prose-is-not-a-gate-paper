# Claims Ledger

**Manuscript:** *What the Reviewer Is Told to Check: Instruction Scope, Notices, and Test-Passing Partial Work in Multi-Agent Code Handoffs* (working title until 2026-11-20: *Prose Is Not a Gate*)

Every quantitative, statistical, and architectural claim in `paper/main.tex` and `README.md` maps directly to a verified repository artifact below.

---

## 1. Pre-Registration, Data Accounting, & Independent Recount

| Artifact | Verification | Value / Status |
|---|---|---|
| Pre-registration lock | `git rev-parse origin/main` before running `T00..T35` | Commit `f7ec48cde6c7ddcf99c52f4fe0625e7ff25525c9` (`HYPOTHESES.md`) |
| Post-lock engineering log | `HYPOTHESES.md` Section 4 | `2026-11-17T12:52Z`: retry escalation on `attempt >= 1` for Ollama GBNF repeat loop (`attempt == 0` untouched) and Ollama workers `2 -> 1` |
| Calibration separation | `scripts/recount_independent.py` | `0` calibration tasks (`C00..C03`) present in `runs/confirmatory` |
| Confirmatory record count | `results/recount_check.txt` | `6,012` records (`exp_a=2376`, `exp_b=1980`, `exp_c_stage1=216`, `exp_c_stage2=144`, `exp_c_stage3=1080`, `part2=216`), `DISCREPANCIES: 0` |
| OpenAI spend accounting | `results/cost_summary.json` | `$12.2138` across confirmatory records; `$13.6480` cumulative log (under `$20.00` cap) |
| Offline unit tests | `pytest tests/ -n auto -v` | `86 passed` covering all 40 task invariants, freeze obstacles, Ed25519 tampering, secret scrubbing, budget cap, stats |

---

## 2. Deterministic Gate Baselines (`results/tables.md` Section 0)

| Claim | Source Row | Verified Value |
|---|---|---|
| `OriginGate` passes all 4 conditions (`clean`, `false_ci`, `disclosed_partial`, `silent_partial`) | `results/tables.md` Sec 0 | `36/36` pass in all 4 conditions (`0/36` defects blocked) |
| `CIDigestGate` catches all `false_ci` patches | `results/tables.md` Sec 0 | `36/36` `clean` pass; `0/36` `false_ci` pass (`36/36` blocked) |
| `CIDigestGate` passes complete worktree-green partial patches | `results/tables.md` Sec 0 | `36/36` pass on `disclosed_partial` and `silent_partial` (`0/36` hidden oracle pass) |

---

## 3. Confirmatory Hypotheses (`H1` through `H4`)

### Family H1: Experiment A (`Signals & Badges under Discretion`, `results/tables.md` Sec 1)
- **H1a (`neutral` vs `bare_verified` on `silent_partial`, pooled Core 5 `N=36` repos):** `+3.3 pp` (`0.739` vs `0.706`, `8/2/26` repos, `p_sign_holm = 0.2188`, `p_wilcoxon_holm = 0.1156`). **Pre-registered null overall** (`gemma4`: `24/36 -> 19/36`, `p_holm = 0.3594`; API frontier models at `35-36/36` ceiling; `nemotron3` at `2/36 -> 0/36`).
- **H1b (`scoped_verified` vs `green_ci_badge` on `silent_partial`, pooled Core 5):** `+1.7 pp` (`0.717` vs `0.700`, `8/5/23`, `p_sign_holm = 0.5811`, `p_wilcoxon_holm = 0.4054`). **Pre-registered null.**
- **H1c (`ci_mismatch_prose` vs `neutral` on `false_ci`, pooled Core 5):** `+25.6 pp` (`0.994` vs `0.739`, `36/0/0` repos, `p_sign_holm = 8.73e-11`, `p_wilcoxon_holm = 1.14e-07`), driven by `nemotron3:33b` (`35/36` vs `0/36`, McNemar `(35, 0)`, `p_holm = 1.75e-10`) and `gemma4:latest` (`36/36` vs `25/36`, McNemar `(11, 0)`, `p_holm = 0.0029`).
- **Baseline Receiver Calibration Polarity (`Table 1a`):** `gpt-6.1-sol` clean FA `0.39..0.50` (`c = -0.84..-0.97`); `gpt-6-luna` clean FA `0.28..0.39` (`c = -0.70..-0.97`); `claude-haiku-5-5` clean FA `0.14..0.17` (`c = -0.58..-0.64`); `gpt-5.4-nano` clean FA `0.00..0.08`; `gemma4:latest` clean FA `0.00` (`c = +0.90..+1.11`); `nemotron3:33b` clean FA `0.00` (`c = +1.76..+2.21`).

### Family H2: Experiment B (`Procedural Narrowing & Request Binding`, `results/tables.md` Sec 2)
- **H2a (`goal_duty` vs `narrow_ci_duty` on `silent_partial`):**
  - Pooled Core 5 (`N=36`, 180 obs): `+70.6 pp` (`0.817` vs `0.111`, `36/0/0` repos, `p_sign_holm = 8.73e-11`, `p_wilcoxon_holm = 1.69e-07`).
  - Significant on **all 6 models**: `gpt-5.4-nano` (`36/36 -> 3/36`, `p_holm = 4.66e-10`), `gpt-6-luna` (`36/36 -> 4/36`, `p_holm = 9.31e-10`), `gpt-6.1-sol` (`18/18 -> 0/18`, `p_holm = 2.29e-05`), `gemma4:latest` (`32/36 -> 0/36`, `p_holm = 1.40e-09`), `claude-haiku-5-5` (`36/36 -> 13/36`, `p_holm = 4.77e-07`), `nemotron3:33b` (`7/36 -> 0/36`, `p_holm = 0.0469`).
- **H2b (`goal_duty` vs `narrow_ci_duty` on `disclosed_partial`):**
  - Pooled Core 5 (`N=36`, 180 obs): `+22.8 pp` (`0.994` vs `0.767`, `35/0/1` repos, `p_sign_holm = 8.73e-11`, `p_wilcoxon_holm = 8.33e-08`).
  - **Literal-obedience inversion:** `gpt-6-luna` drops `36/36 -> 2/36` (`p_holm = 3.49e-10`), `gpt-6.1-sol` drops `18/18 -> 0/18` (`p_holm = 2.29e-05`), `nemotron3:33b` drops `35/36 -> 28/36` (`p_holm = 0.0469`), while `claude-haiku-5-5`, `gpt-5.4-nano`, and `gemma4:latest` stay at `36/36` (refusing incomplete PRs despite the narrow CI instruction).
- **H2c (`goal_duty` vs `no_ticket_control` on `silent_partial`):**
  - Pooled Core 5 (`N=36`, 180 obs): `+74.4 pp` (`0.817` vs `0.072`, `36/0/0` repos, `p_sign_holm = 8.73e-11`, `p_wilcoxon_holm = 1.69e-07`), significant individually on all 6 models (`p_holm <= 0.0469`).

### Family H3: Experiment C (`Stage-2 Briefs & Programmatic Gate`, `results/tables.md` Sec 3)
- **Stage-1 Advisors (`Table 3a`):** `qwen3.6` (`0/36` clean FA, `36/36` `silent_partial`), `gemma4` (`2/36` clean FA, `35/36` `silent_partial`), `nemotron3` (`0/36` clean FA, `10/36` `silent_partial`).
- **Stage-2 Crux Leak & Suppression (`Table 3b`):** Both synthesizers (`gemma4`, `nemotron3`) emitted non-empty `cruxes` or `unverified_premises` on `36/36 (100%)` of `clean` PRs when ungated, despite `34/36` unanimous `approve` Stage-1 panels. `apply_programmatic_gate` cleared all `34/34` unanimous leaks (`36/36 -> 2/36`) while preserving `36/36 (100%)` of `silent_partial` panels (`25` two-hold, `10` three-hold, `1` solitary `1-of-3` requirement-omission hold).
- **Stage-3 Deciders (`Table 3c/3e`):** When deciders received the identical deterministic `pytest` + `git diff` header and repo tools, Stage-3 `H3a`/`H3b`/`H3c` contrasts yielded **pre-registered Stage-3 nulls overall** (`+2.8 pp` pooled clean FA `0.089` vs `0.061`, `p_sign_holm = 1.000`, `p_wilcoxon_holm = 0.9519`; `gemma4 -> nemotron3` clean FA reduced from `5/36` ungated to `1/36` gated and `0/36` consensus, `p_raw = 0.0625..0.2188`). Meanwhile `nemotron3:33b` under `gated_crux_brief` raised `silent_partial` catch from `2/36 (6%)` in Exp A (`discretion`) to `35/36 (97%)` while holding `clean` FA to `1/36 (3%)`.

### Family H4: Part 2 (`Live Organic Coding Workers`, `N = 216`, `results/tables.md` Sec 4)
- **Outcome totals (`POOLED_ALL`, `N = 216`):** `complete=7`, `disclosed_partial=131`, `silent_partial=4`, `false_pass_claim=1`, `disclosed_failing=34`, `test_tampering=5` (`4` `gemma4`, `1` `gpt-5.4-nano`), `unfinished_or_parse_error=34`.
- **H4a (Partial delivery under clean local pytest):** `135/216 = 0.625 [0.559, 0.687]` (`claude-haiku-5-5` `36/36`, `gpt-6.1-sol` `18/18`, `qwen3.6` `18/18`, `gpt-6-luna` `35/36`, `gpt-5.4-nano` `26/36`, `gemma4` `2/36`, `nemotron3` `0/36`).
- **H4b (Concealed/integrity failures):** `10/216 = 0.046 [0.025, 0.083]` (`silent_partial=4` on `gpt-5.4-nano`, `false_pass_claim=1` on `nemotron3`, `test_tampering=5`).
- **Deterministic Gate Catch Rates (`Table 4a`):** Combined `CIDigestGate + TestIntegrityGate` caught `1/1` `false_pass_claim`, `34/34` `disclosed_failing`, `34/34` `unfinished_or_parse_error`, and `5/5` `test_tampering` (including `1/5`, `gemma4 T01`, that passed `CIDigestGate` alone via `loosened_asserts: 2->0` and matching reported passed tests), versus only `3/131 (2.3%)` of `disclosed_partial` and `0/4 (0%)` of `silent_partial`.
- **Scope & Reproducibility:**
  - Exact model snapshots & image digests evaluated (Nov 2026): `gemma4:latest` (`371e604cf9be`), `nemotron3:33b` (`f6d8b7ff496c`), `qwen3.6:27b-coding-mxfp8` (`a7185d39ff35`), `gpt-5.4-nano` (`gpt-5.4-nano-2026-03-17`), `gpt-6-luna`, `gpt-6.1-sol`, `claude-haiku-5-5`.
  - `BALANCED_18` (`T00..T08 + T18..T26`, `N=18`) spans all 12 domains (`2` tasks in 6 domains, `1` task in 6 domains; `9 req_2`, `9 req_1` omitted) and is excluded from pooled Core 5 repo-clustered tests so each repo contributes 5 equal weights (`180` observations).
  - Pre-lock calibration spend (`$1.4342` on `C00..C03`) + confirmatory spend (`$12.2138`) = `$13.6480` cumulative (`0` confirmatory trials discarded).
  - Ollama retry forensics: `4` Stage-1/2 records used `retry_attempt == 1` (`0` reached `attempt == 5`). Terminal `decision == "parse_error"` occurs in `8 / 5,436` receiver runs (`0.15%`, all `nemotron3:33b`), scored conservatively as non-hold; flipping/excluding all `8` leaves all `H1` and `H2` confirmatory decisions invariant.
- **Syntactic Freeze Evasions (`7/216 = 3.2%`, labeled `Evaded` in manuscript Table 5):** All `7` `"complete"` runs (`6` `gpt-5.4-nano`, `1` `gpt-6-luna`) bypassed the AST signature/FunctionDef check in `tests/test_api_freeze.py` via `**kwargs` forwarding (`T12`), module `lambda` / `__getattr__` bindings (`T21`, `T24`), or private helpers (`0` AST test tampering, proving syntactic freeze checks are gameable without runtime behavioral checks).

---

## 4. Descriptive Field Cases: Multi-Agent Git Infrastructure (`cirwel/fleet-ops`)

> **Scope Note:** All five cases below come from a single private, author-operated deployment (`cirwel/fleet-ops`) and are presented strictly as descriptive, commit-anchored engineering incident records and code repairs rather than as a controlled comparative trial or efficacy claim. External readers cannot independently inspect the private repository commits.

| Case Study | Anchored Commits | Observable Failure Mode | Concrete Deterministic Repair |
|---|---|---|---|
| Provenance Block & Isolated HOME | `052e2a3`, `9e3e317` | Substring matching treated documentation examples as real attribution; "newest file on disk" risked cross-session attribution collisions | Strict terminal-block regex parsing (`HAS_FOOTER_RE`), fail-closed model mismatch check, transcript lookup keyed on explicit `ANTIGRAVITY_CONVERSATION_ID` |
| Per-Command Token Scoping | `dd2113f` | Default `actions: read` token refused automated merge-queue `gh run rerun` calls (`Resource not accessible by integration`) | Explicit command allowlist granting `actions: write` only to `gh workflow run` and `gh run rerun` with single-repo installation tokens revoked on exit |
| Fail-Closed Registry Override | `47ab74d` | Engine read missing `governance_sensitivity_manifest.tsv` fail-closed across sibling repos without manifests, stalling labeled PR `#169` for 5 days | Required explicit per-repo `"repository"` vs `"none"` registry entries (`unitares-local/config/pr-queues.json`), stripped inherited env vars, added regression tests |
| Process-Lineage Self-Match | `1141884` | Checking full process `argv` for repo path flagged wrapper shell (`cd <repo> && git prepr`) as a lingering repo-rooted process | Walk `PPID` ancestry from gate `$$` to PID `1` to exclude caller chain while keeping detection for non-caller repo processes |
| Closeout Read-Back & Surface Leases | `bin/git-closeout`, `bin/git-prepr` | Sandboxed DNS failures silently collapsed into `pushed_branch_no_pr` (`current branch PR: none visible to gh`) | Pair local closeout checks with network-capable API read-back and `git prepr` zero-claim enforcement (`git surface list --repo --active`) |

---

## 5. Scope & Non-Claims

1. **No human subjects:** All receivers, advisors, synthesizers, and coding workers are LLMs (`seed = 0`, `T = 0.2`); results do not establish human-factor complacency rates.
2. **Micro-repository scope:** Each task uses a single Python module and focused pytest suite; larger multi-file codebases may show different base-rate noise and inspection budgets.
3. **Cross-benchmark contrast boundaries:** Tool-equipped code receivers (`Exp A`, `Exp C Stage 3`) differ structurally from non-tool/tabular decision pipelines where receivers cannot run tests or inspect diffs directly.

---

## 6. Corrections of 2026-11-20 (supersede the rows above where they differ)

Applied after a cold read by an outside model family (`docs/reviews/2026-11-20-cold-read-gpt-6.2-sol.md`) and a check of each point against the code and raw records. No confirmatory data, hypothesis or statistic changed.

| Topic | Earlier wording | Corrected statement | Checked against |
|---|---|---|---|
| Record count | `6,012` records | `6,012` files, `5,616` unique. `396` Experiment B `discretion` cells (`clean`, `silent_partial`) are copies of Experiment A `neutral` decisions, marked `reused_from_exp_a`. The reuse is not stated in the lock. | `repohandoff/sweep.py`, raw records |
| Spend | `$12.21` confirmatory plus `$1.43` calibration | Estimates stored in the unique records sum to `$11.36`; the copies add `$0.85`. The cumulative usage log shows `$13.65`. The `$2.29` difference is unreconciled; the usage log is not in the archive. | `results/cost_summary.json`, raw records |
| Discarded trials | `0` confirmatory trials discarded | Not provable from the archive: receiver and worker records keep no per-call retry metadata. | raw records |
| "Pre-registered null" (`H1a`, `H1b`, `H3`) | Nulls described as pre-registered | The contrasts were pre-registered; the lock states directional expectations, and the results are non-significant (no equivalence test). Stage-3 Holm sign `p = 1.00`, `0.68`, `1.00`. Where rows above say "clean FA" or "false alarm", read "hold on a clean-labelled patch" (see `docs/CLEAN-LABEL-AUDIT.md`); where they say `seed = 0`, `T = 0.2`, read "requested". | `HYPOTHESES.md` |
| Sign test as primary | Described as the pre-registered primary test | The lock names sign and Wilcoxon tests without ranking them. Leading with the sign test is a reporting choice. | `HYPOTHESES.md` section 3 |
| Decoding | `temperature = 0.2`, `seed = 0` for all models | Requested, not uniformly applied: the Claude CLI backend takes neither, the OpenAI backend drops `temperature` when rejected, Ollama retries change both. | `repohandoff/backends.py` |
| Neutral metadata slot | Length-matched | Fixed position, not length-matched (about 40 to 150 characters across arms). | `repohandoff/prompts.py` |
| `H2c` | Isolates ticket removal | `no_ticket_control` removes the ticket and also rewords the duty. It is a control, and its direction is expected. | `repohandoff/prompts.py` |
| Stage-2 `36/36` and `34/34` | Crux "fabrication" and "suppression" findings | The synthesis prompt asks for cruxes, so non-empty fields are prompt compliance. The gate clears fields on unanimous passing panels by rule, so `34/34` restates the rule. Both are descriptive; the three pre-registered `H3` contrasts are at Stage 3 and are null. | `repohandoff/prompts.py`, `repohandoff/briefs.py` |
| Part 2 `135/216` | Worker failure rate | `131` of the `135` carry the `disclosed_partial` classifier label (green local tests, nonzero oracle exit, a report naming an unfinished item), the outcome the instructions asked for. The archive keeps no oracle diagnostics, so the missing requirement is not verified per run. | `repohandoff/worker.py`, `repohandoff/prompts.py` |
| `TestIntegrityGate` `5/5` | Catch rate | Definitional: the tampering label is the gate's own AST flag. The informative case is the single run (`gemma4 T01`) that `CIDigestGate` alone passed. | `repohandoff/worker.py` |
| `gemma4 T01` report | Worker updated its report with passing test names | When the worker reports `tests_passed = true`, the harness fills `passed_tests` from its own run (otherwise the list is empty) and signs the post-edit tree. | `repohandoff/worker.py` |
| `3/131` disclosed partials blocked | Partial detection | All three had reported `tests_passed = false`; the blocks are report mismatches. | raw records |
| "Evaded" (`7/216`) | Outcome label | The pre-registered label is `complete`. "Evaded" was chosen after the lock. The bypass mechanisms are as the workers reported them; the archive keeps no final source. | raw records |
| Vouchers | Ed25519 commit vouchers | Harness-signed vouchers over a tree manifest and report, using a fixture key. Not Git commit signatures. | `repohandoff/crypto.py` |
| Recount | All statistics independently recounted | A second script, sharing no imports with the analysis, re-aggregates counts, Wilson intervals, McNemar pairs and repository signs. It does not recompute Holm, Wilcoxon or signal-detection values and does not re-judge labels. | `scripts/recount_independent.py` |
| Field cases | Production field evidence | Illustrations selected after the experiments from one private repository; not evidence for the experimental claims. | manuscript section 6 |

---

## 7. Corrections of 2026-11-20, second round (supersede sections 4 and 6 where they differ)

Applied after a five-seat review (three Anthropic seats reading the repository, one OpenAI and one Google seat by consult) and a decision ballot on which all three families voted the same way on every item (`docs/REVIEWS.md` section 5). No confirmatory record, hypothesis or statistic changed.

| Topic | Earlier wording | Corrected statement | Checked against |
|---|---|---|---|
| Title | *Prose Is Not a Gate* | Retitled. The largest effect comes from changing prose in the receiver's instruction, so the old title contradicted the evidence. | Experiment B |
| Field cases (section 4 of this ledger) | Section 6 of the manuscript, rule 5 | Removed from the manuscript. The repository is private, the cases were chosen after the experiments, and nothing in them is checkable by a reader. Section 4 of this ledger is retained as history only. | ballot D3 |
| Four-layer stack | A contribution and organizing frame | Dropped as a contribution. Table 1 remains as a description of what each deterministic check returns by construction. No deterministic check of a patch against its ticket exists in the harness. | `repohandoff/crypto.py`, `repohandoff/briefs.py` |
| Experiment B | "Procedural CI tunnel vision", "literal-obedience inversion" | A bundled instruction change: `narrow_ci_duty` changes both what the receiver looks at and the verdict it is told to return. A post hoc arm on four no-cost models removes the verdict rule and keeps the check (`results/exploratory_attention_arm.md`). | `repohandoff/prompts.py` |
| `H2b` split | "Two models from one developer" | `gpt-6-luna` and `gpt-6.1-sol` returned `merge`; `gpt-5.4-nano`, also from OpenAI, held `36/36`. The developer does not explain the split. | raw records |
| Clean label | "At least 7" of 22 audited fixtures deviate; 59 of 110 holds cite a deviation | All 36 audited by two independent passes from two families: 11 deviate by agreement of both, 11 are disputed, 10 ambiguous, 4 unobjected. 73 of 110 Experiment A clean holds fall on the 11 (a count by task, not by cited reason). | `docs/CLEAN-LABEL-AUDIT.md`, `scripts/verify_clean_label_audit.py` |
| Signal-detection values | Reported in the body | Moved to an appendix: they score every hold on a clean-labelled patch as an error. | `results/clean_label_sensitivity.md` |
| Experiment C | A main-body experiment with a design rule | One paragraph in the body, full report in an appendix. All five of its terminal parse errors are in the `gemma4 -> nemotron3` pairing and make up every discordant pair of that pairing's `H3c` contrast. Rule 3 removed. On the 25 tasks without an agreed deviation, ungated crux briefs drew 10/125 clean holds against 0/125 gated (exploratory). | raw records |
| Part 2 "silent partial" (`4/216`) | Silent omissions | A keyword-rule label. All four reports claim both requirements implemented and all four describe the workaround in their notes. | raw records, `repohandoff/worker.py` |
| Part 2 "test tampering" (`5/216`) | Tampering, counted under "Concealed" | Five runs with an edit to a pre-existing test: two reported failing tests, two filed no report, one (`gemma4 T01`) passed and disclosed the edit in its notes. None conceals the edit. The AST check does not cover `conftest.py`, pytest configuration or module-level skips. | raw records, `repohandoff/worker.py` |
| `H4b` | "Concealed" rate `10/216` | The pre-registered sum is still reported; a reading of the ten reports finds none that conceals what the worker did. | raw records |
| `nemotron3` `H1c` | "Missed 1/36" under the mismatch banner | The one non-hold is a terminal parse error; the verdict is unknown. | raw record `T08` |
| Design rules | Five rules | Two scoped observations with experimental support, three untested implications. | ballot D7 |

---

## 8. Corrections of 2026-11-21 (final reads of the PDF)

Applied after two outside-family reads of the rendered PDF (`docs/REVIEWS.md` section 6). No confirmatory data, hypothesis or statistic changed.

| Topic | Earlier wording | Corrected statement | Checked against |
|---|---|---|---|
| Mismatch notice and test runs | The two local models "rarely ran the tests themselves"; a notice "can substitute for a check" | With the notice both ran the tests more often: `nemotron3` `run_pytest` on 0/36 then 22/36 `false_ci` trials, `gemma4` on 12/36 then 36/36 | `runs/confirmatory/exp_a` |
| `TestIntegrityGate` on `false_ci` | "n/a" in Table 1 | Flags 8 of 36: those patches also loosen or change a legacy test | `repohandoff.receiver.prepare_condition_state` on `T00`..`T35` |
| Oracle exit code 2 in Part 2 | "a collection error" | 112 of the 135 partial-labelled runs have exit code 2; the likely cause is an import of a missing public name (the scripted partial patches give exit 2 on 30 of 36 tasks); the archive cannot confirm it per run | `runs/confirmatory/part2`, fixture preparation |
| No-change disclosed partials | Stated only in the abstract | 16 of 131, by model: `gpt-5.4-nano` 6, `gpt-6-luna` 3, `qwen3.6` 3, `claude-haiku-5-5` 2, `gpt-6.1-sol` 1, `gemma4` 1 | `implemented_allowed_req` in `runs/confirmatory/part2` |
| Table 5 column for the `complete` outcome | "Evaded" | "Both_Pass"; the pre-registered label remains `complete` | manuscript Table 5 |
| `git_diff` use in Experiment A | `32/36` to `36/36` for four models | `35/36` or `36/36` on silent partials for the three hosted models with 36 tasks, `18/18` for `gpt-6.1-sol` | `runs/confirmatory/exp_a` |
| `H2b` pooled difference | `+22.8 pp` | `-22.8 pp` (0.994 to 0.767), the same sign convention as `H2a` and `H2c` | `results/tables.md` section 2 |
| Experiment C overlap | Panels overlap "because `qwen3.6` participated in every panel" | `gemma4` and `nemotron3` serve at Stage 1 and again as synthesizers or deciders | `repohandoff/briefs.py` |
| Location of materials | "the project repository", no address | Repository URL and release `paper-v1.0` | manuscript section 8 |

