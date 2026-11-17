# Claims Ledger

**Manuscript:** *Prose Is Not a Gate: Duty Narrowing, Verification Notices, and Programmatic Crux Gates in Multi-Agent Software Handoffs*

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
