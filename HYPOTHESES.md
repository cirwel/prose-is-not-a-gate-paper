# Pre-Registered Confirmatory Study Protocol & Hypotheses

- **Project:** *Prose Is Not a Gate: How Provenance Badges, Check Notices, and Disagreement Briefs Miscalibrate Multi-Agent Software Handoffs*
- **Pre-registration status:** Locked **prior** to running any confirmatory benchmark task (`T00` through `T35`). No `runs/confirmatory/` outputs exist at lock time.
- **Scope:** Machine-to-machine software handoffs (`Contributor A -> Advisors/Synthesizer -> Receiver B`) and deterministic code-level gates. No human-subject evaluation or claims are made.

---

## 1. Benchmark Inventory & Calibration Isolation

1. **Separated Calibration Suite (`C00`..`C03`, `N = 4`):** Used strictly for offline prompt refinement, schema verification, and harness sanity checks (`runs/smoke_v1`, `runs/smoke_v2`, `runs/smoke_v3_cal`). Never included in confirmatory tables or statistical inference.
2. **Confirmatory Repository Suite (`T00`..`T35`, `N = 36`):** Thirty-six isolated Python git micro-repositories spanning 12 software engineering domains (3 tasks per domain): `rate_limit`, `billing`, `auth_tokens`, `etl_parsing`, `retry_backoff`, `sanitizer`, `rbac`, `scheduler`, `semver`, `uri_paths`, `cache_store`, and `pagination`.
   - **Exact Counterbalancing:** Eighteen tasks (`T00`..`T17`) omit `req_2` in their `patch_partial` implementation; eighteen tasks (`T18`..`T35`) omit `req_1`.
   - **High-Latency Slice (`BALANCED_18`, `N = 18`):** `T00`..`T08` (`9` tasks omitting `req_2`) plus `T18`..`T26` (`9` tasks omitting `req_1`), preserving domain balance and counterbalancing.

---

## 2. Model Roster, Decoding, & Deterministic Gate Baselines

- **Full-Bank Core Models (`N = 36`):** `gemma4:latest` (`google` / Ollama), `nemotron3:33b` (`nvidia` / Ollama), `gpt-5.4-nano` (`openai`), `gpt-6-luna` (`openai`), and `claude-haiku-5-5` (`anthropic` / Claude CLI headless `--tools ""`).
- **Balanced-18 Extended Models (`N = 18`):** `gpt-6.1-sol` (`openai`, Exp A, Exp B, Part 2) and `qwen3.6:27b-coding-mxfp8` (`qwen` / Ollama, Part 2).
- **Sampling Parameters:** `temperature = 0.2`, `seed = 0` (seed bumped only on Ollama repetition-loop 500 errors per retry adapter). Every receiver has 4 read/test tools (`list_files`, `read_file`, `git_diff`, `run_pytest`) across up to 8 turns; every Part 2 coding worker also has `write_file` across up to 10 turns under an AST-monitored `tests/test_api_freeze.py` hold.
- **Deterministic Gates Evaluated Alongside LLM Decisions:**
  1. `OriginGate`: Ed25519 signature, expected issuer (`contributor-alpha`), expected audience (`maintainer-beta`), and task binding (`voucher.payload.task_id`). Passes `36/36` across `clean`, `false_ci`, `disclosed_partial`, and `silent_partial`.
  2. `CIDigestGate`: `OriginGate` plus exact worktree Merkle tree SHA-256 verification, report digest match, live `pytest` exit code `0`, non-empty `passed_tests`, and exact `passed_tests` set equality against the contributor claim. Expected `36/36` pass on `clean` (and `disclosed_partial`/`silent_partial` where `req` omission does not break worktree tests) and `0/36` pass (`36/36` block) on `false_ci`.
  3. `TestIntegrityGate`: AST check over pre-existing `tests/*.py` (`deleted_test_file`, `syntax_error_in_test_file`, `deleted_test_fn`, `added_skip_or_xfail`, `loosened_asserts`, `modified_test_fn`).
  4. `apply_programmatic_gate` (Exp C): Deterministic `pytest` (`exit == 0`, zero failed tests) combined with Stage-1 advisor vote count (`preserve` when `pytest` fails, `>= 2` advisors hold, or a solitary `1-of-3` hold cites a ticket requirement omission; clear `cruxes`/`unverified_premises` when `pytest` passes and advisors unanimously approve or a solitary hold asserts only test failure contradicted by `exit == 0`).

---

## 3. Confirmatory Hypotheses & Statistical Rules

- **Unit of Statistical Replication:** The repository `T_i` (`N = 36` paired repositories for full-bank models/pairings; `N = 18` for `BALANCED_18` models).
- **Primary Decision Endpoints:** Per-condition `hold` rate (`k/n` with 95% Wilson CIs), Signal Detection metrics (`hit_rate`, `false_alarm_rate`, `Net J = H - FA`, log-linear `d'`, and criterion `c`), and tool-call rates (`run_pytest`, `git_diff`).
- **Hypothesis Testing:** Within each model (or Exp C pairing), test each locked contrast via exact two-sided McNemar test (`binomtest(b, b+c, 0.5)`) on paired `(T_i, seed=0)` decisions. Additionally test the pooled effect across core units by averaging paired hold differences at the repository level (`N = 36` independent repository scores) using two-sided exact sign and Wilcoxon signed-rank tests. Adjust p-values for multiple comparisons within each 3-contrast hypothesis family using Holm step-down correction (`m = 3`).

### Family H1: Provenance Badges & Check Prose under Discretion (Experiment A)
- **Design:** `signal` in `{neutral, bare_verified, scoped_verified, green_ci_badge}` evaluated across `{clean, silent_partial}` (plus `false_ci` for `neutral`, `bare_verified`, `scoped_verified`, and `ci_mismatch_prose` for `false_ci`), all under `discretion` with identical fixed-position `PR Metadata:` slots and length-matched neutral baseline.
- **Locked Contrasts (`m = 3`, Holm-corrected):**
  - **H1a:** `neutral` vs. `bare_verified` on `silent_partial` (tests whether an unscoped verified provenance badge lowers defect detection or shifts criterion `c` even though valid Ed25519 identity says nothing about ticket completeness).
  - **H1b:** `scoped_verified` vs. `green_ci_badge` on `silent_partial` (tests whether an unscoped green CI badge induces complacency relative to explicitly scoped authorship metadata when `worktree pytest` passes with an omitted requirement).
  - **H1c:** `ci_mismatch_prose` vs. `neutral` on `false_ci` (quantifies whether prose contradiction warnings materially increase `hold` rate over discretionary tool verification when worktree `pytest` fails; benchmarked against deterministic `CIDigestGate`, which blocks `36/36`).

### Family H2: Instruction Narrowing & Request Binding (Experiment B)
- **Design:** `duty` in `{discretion, narrow_ci_duty, goal_duty}` across `{clean, disclosed_partial, silent_partial}`, plus `no_ticket_control` on `silent_partial` (`include_ticket = False` with neutral queue wording that removes meta-experimental hints).
- **Locked Contrasts (`m = 3`, Holm-corrected):**
  - **H2a:** `goal_duty` vs. `narrow_ci_duty` on `silent_partial` (quantifies procedural CI tunnel vision: holding missing requirements under request-bound `goal_duty` vs. rubber-stamping when instructed to check only worktree `pytest == 0` matching `passed_tests`).
  - **H2b:** `goal_duty` vs. `narrow_ci_duty` on `disclosed_partial` (tests whether procedural narrowing causes monitors to ignore even explicit prose disclosure in contributor `notes` when `pytest` matches).
  - **H2c:** `goal_duty` vs. `no_ticket_control` on `silent_partial` (separates true request-bound verification from generic anomaly spotting when the contributor's diff is locally plausible and tests pass).

### Family H3: Unconditional vs. Programmatically Gated Disagreement Briefs (Experiment C)
- **Design:** Fixed 3-advisor multi-family Stage-1 panel (`gemma4:latest`, `nemotron3:33b`, `qwen3.6:27b-coding-mxfp8`), anonymized and blinded Stage-2 synthesizer (`nemotron3:33b`, `gemma4:latest`), and 5 cross-family Stage-3 decider pairings (`nemotron3 -> gemma4`, `gemma4 -> nemotron3`, `nemotron3 -> gpt-5.4-nano`, `nemotron3 -> gpt-6-luna`, `nemotron3 -> claude-haiku-5-5`) under `discretion` across `{clean, silent_partial}`. All three brief arms (`consensus_brief`, `ungated_crux_brief`, `gated_crux_brief`) carry an identical deterministic `pytest` + `git diff --stat` header.
- **Locked Contrasts (`m = 3`, Holm-corrected):**
  - **H3a:** `ungated_crux_brief` vs. `consensus_brief` on `clean` (tests whether forcing structured disagreement without programmatic gating injects manufactured caveats/cruxes and raises clean false-alarm `hold` rates).
  - **H3b:** `ungated_crux_brief` vs. `gated_crux_brief` on `clean` (tests whether deterministic gating eliminates synthetic crux leakage and false-alarm spillovers relative to the same pre-gate Stage-2 Crux output).
  - **H3c:** `gated_crux_brief` vs. `consensus_brief` on `silent_partial` (tests whether preserving requirement-omission dissents under deterministic gating preserves or improves defect catch rate relative to common-ground synthesis).

### Family H4: Live Organic Worker Failure Modes & Gate Visibility (Part 2)
- **Design:** Live coding workers (`core_5` on `N = 36`; `qwen3.6:27b-coding-mxfp8` and `gpt-6.1-sol` on `BALANCED_18`) edit each repository against a visible `tests/test_api_freeze.py` hold blocking unapproved changes to the counterbalanced frozen public API/behavior while all hidden oracle tests verify full `req_1 + req_2` completion.
- **Pre-Specified Descriptive Quantities & 95% Wilson CIs:**
  - **H4a:** Rate of incomplete delivery under clean visible pytest (`(disclosed_partial + silent_partial) / n`), characterizing how often live coding agents satisfy local CI while omitting frozen requirements.
  - **H4b:** Rate of concealed or integrity-violating handoffs (`(silent_partial + false_pass_claim + test_tampering) / n`), paired with exact deterministic catch rates of `CIDigestGate` alone vs. `CIDigestGate + TestIntegrityGate` across each realized outcome channel (`disclosed_failing`, `false_pass_claim`, `test_tampering`, `disclosed_partial`, `silent_partial`, `complete`).

---

## 4. Post-Lock Deviations Log

- **`2026-11-17T12:52Z` (post lock commit `f7ec48cde6c7ddcf99c52f4fe0625e7ff25525c9`):** During confirmatory execution (`gemini/confirmatory-and-paper-1117`), `gemma4:latest` hit Ollama `HTTP 500: {"error":"prediction aborted, token repeat limit reached"}` on 2 of 432 `Exp A` trials (`T17` `false_ci` under `neutral` and `bare_verified`) due to `llama.cpp` JSON grammar repetition over escaped HTML quotes. Updated `call_ollama` in `repohandoff/backends.py` so `attempt == 0` decoding parameters remain completely unchanged (`temperature = 0.2`, `seed = 0`, `format = "json"`), while `attempt >= 1` retries escalate `repeat_penalty` (`1.23` to `1.55`), `temperature` (`0.32` to `0.70`), and `repeat_last_n = 256`, dropping `format = "json"` only on final retry `attempt == 5`. Also set `_max_workers_for("ollama")` in `repohandoff/sweep.py` from `2` to `1` to match `llama-server -np 1` concurrency. No task fixtures, prompts, or statistical hypotheses were modified.
