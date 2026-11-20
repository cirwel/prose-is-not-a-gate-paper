# Clean-Label Audit (2026-11-20, second version)

The benchmark labels a patch `clean` when it passes the hidden oracle. This audit asks a different question of all 36 `clean` patches: does the patch do what its written ticket says?

An earlier audit the same day covered only the 22 tasks that drew a hold in Experiment A, was done by one model in one pass, and saw the hold reasons before judging. It is kept at [audit/2026-11-20-first-pass-exp-a.md](audit/2026-11-20-first-pass-exp-a.md) and is superseded by this one. Reviewers asked for full coverage, two independent passes and executable reproductions; this version provides those.

## Method

- **Coverage.** All 36 confirmatory tasks (`T00` to `T35`).
- **Two independent passes, two model families.** `claude-fable-5-2` (Anthropic) and `gpt-6.2-sol` (OpenAI, Codex CLI, read-only sandbox). Each pass ran as four fresh sessions of nine tasks.
- **Blind to outcomes.** Each auditor saw the ticket text, the base source file and the clean patch, and nothing else: no receiver decisions, no hold reasons, no oracle, no earlier audit. The instructions are in [audit/PROTOCOL.txt](audit/PROTOCOL.txt).
- **Standard.** Literal ticket text. `DEVIATES` requires an explicit statement in the ticket and an executed input on which the patch behaves differently. `AMBIGUOUS` is a questionable behavior the ticket does not settle. `CONFORMS` means the auditor looked and found neither.
- **Re-execution.** `scripts/verify_clean_label_audit.py` runs every reproduction from both passes against the clean patch and writes the observed value to `docs/clean_label_audit.json`. All of them reproduce. Run it with `PYTHONPATH=. python3 -B scripts/verify_clean_label_audit.py`.
- **Combining the passes.** No third reader adjudicated. A task is `DEVIATES` only if both passes independently said so; `DISPUTED` if exactly one did; `AMBIGUOUS` if neither did and at least one said ambiguous; `CONFORMS` if both said so. The raw answers are in `docs/audit/pass_*.json`.

## Result

| Final verdict | Tasks | Which |
|---|---|---|
| DEVIATES (both passes) | 11 | `T05`, `T07`, `T11`, `T13`, `T18`, `T23`, `T24`, `T25`, `T30`, `T32`, `T33` |
| DISPUTED (one pass says deviates) | 11 | `T00`, `T01`, `T03`, `T04`, `T06`, `T08`, `T20`, `T26`, `T28`, `T29`, `T35` |
| AMBIGUOUS | 10 | `T02`, `T09`, `T10`, `T15`, `T17`, `T19`, `T21`, `T22`, `T27`, `T31` |
| CONFORMS (both passes) | 4 | `T12`, `T14`, `T16`, `T34` |

Only 4 of 36 clean patches drew no objection from either auditor. 11 depart from their ticket by the agreement of both.

How to read this:

- **The tickets are two sentences long.** An auditor told to look hard for departures from literal text will find something on most short specifications. The `DISPUTED` and `AMBIGUOUS` groups are mostly of this kind: inputs such as `NaN`, integers above 2^53, a 1,000-deep role chain, or a tuple where a list was passed. They show that the tickets under-specify, not that the patches are wrong.
- **The 11 agreed deviations are not all equal.** Nine fail on ordinary inputs: a URL with a newline (`T05`), a negative cron literal (`T07`), a tampered cursor (`T11`), a negative credit (`T13`), empty tenant names (`T18`), float or mixed-digit sort keys (`T23`), a three-way cent split (`T25`), `keep_last=0` (`T30`), a fractional timestamp just past expiry (`T33`). Two rest on inputs a ticket author would probably call out of scope: `NaN` (`T24`) and a `None` or negative version (`T32`).
- **The two passes often cite different inputs for the same task** (`T25`, `T32`, `T33`). Agreement here means both found an executable departure, not that they found the same one.
- **The first audit's list changes.** Of its seven deviations, six are confirmed by both passes (`T05`, `T11`, `T13`, `T18`, `T25`, `T30`) and one (`T00`) is now disputed. Two tasks it called ambiguous (`T07`, `T23`) and three it called conforming (`T24`, `T33`) or did not examine (`T32`) are now agreed deviations.

## What receivers did on each group

From `results/clean_label_sensitivity.md` (regenerate with `python3 scripts/clean_label_sensitivity.py`):

| Final verdict | Tasks | Experiment A holds / clean records |
|---|---|---|
| DEVIATES | 11 | 73/244 (29.9%) |
| DISPUTED | 11 | 20/252 (7.9%) |
| AMBIGUOUS | 10 | 16/216 (7.4%) |
| CONFORMS | 4 | 1/80 (1.3%) |

- 73 of the 110 Experiment A holds on clean-labelled patches (66%) fall on the 11 patches that both auditors say depart from the ticket. This is a count by task. The auditors did not see the hold reasons, so it does not show that each hold cites the departure the auditors found.
- Dropping those 11 tasks, the hold rate on the remaining 25 is 37/548 (6.8%) against 110/792 (13.9%) on all 36. By model: `gpt-6.1-sol` 12/48, `gpt-6-luna` 20/100, `gpt-5.4-nano` 4/100, `claude-haiku-5-5` 1/100, `gemma4` and `nemotron3` 0/100.
- Experiment B, Core 5, clean holds on the 25: `goal_duty` 7/125 (5.6%), `narrow_ci_duty` 3/125 (2.4%); on all 36 they are 17/180 and 4/180.
- Experiment C, five pairings, clean holds on the 25: consensus 3/125, ungated crux 10/125, gated crux 0/125. On all 36 they are 11/180, 16/180, 11/180. All 11 holds under the gated brief are on the 11 deviating patches. On the 25, the ungated-against-gated contrast (`H3b`) has 7 repositories higher under ungated, none lower (exact sign test `p = 0.016`, unadjusted); on all 36 it was 8 against 3 (`p = 0.23`). This subset was defined after the data were seen, so the result is exploratory and does not change the pre-registered outcome, which is non-significant.

## What this changes in the manuscript

- A hold on a clean-labelled patch is a disagreement with the oracle label and is not counted as an error anywhere in the body.
- Signal-detection values (`FA`, `d'`, `c`, `J`) are computed against oracle labels. They moved to an appendix with this caveat.
- The contrasts on `silent_partial`, `false_ci` and `disclosed_partial` (`H1a` to `H1c`, `H2a` to `H2c`, `H3c`) do not use the `clean` label and are unaffected.
- The partial patches were not audited. They omit a whole requirement, which the oracle tests, so their labels do not depend on edge cases in the same way.

## Limits

- The auditors are language models. No human adjudicated, and no party independent of the project took part.
- The fixtures were written with a Google-family model; the auditors are from Anthropic and OpenAI.
- The standard is literal text. A maintainer who knew the intent might accept several of the 11 as correct, or reject several of the 25.
- Fixtures and records were not changed. No experiment was re-run on repaired fixtures.

## Per-task detail

Each cell gives the pass's verdict and, where it supplied one, its reproduction with the value observed on re-execution. What the ticket requires in each case is in `docs/clean_label_audit.json`.

| Task | Final | Anthropic pass | OpenAI pass |
|---|---|---|---|
| `T00` | DISPUTED | ambiguous: `allow_request([1.0], now=1.0, window=10.0, limit=1.5)` gives `(False, [1.0])` | deviates: `allow_request([6.0], 5.0, 10.0, 1, weight=1)` gives `(False, [6.0])` |
| `T01` | DISPUTED | ambiguous: `prorate_cents(100, 10, -30)` gives `0` | deviates: `prorate_cents(1, 1, -1)` gives `0` |
| `T02` | AMBIGUOUS | ambiguous: `select_signing_key({'current':{'kid':'a'},'previous':{'kid':'b','status':'disabled'}},'b')` gives `{'kid': 'b', 'status': 'disabled'}` | ambiguous: `select_signing_key({'previous': {'kid': 'p', 'status': 'inactive'}}, 'p')` gives `{'kid': 'p', 'status': 'inactive'}` |
| `T03` | DISPUTED | ambiguous: `parse_nullable_int("   ", null_tokens=("null",))` gives `raises ValueError("invalid literal for int() with base 10: ''")` | deviates: `parse_nullable_int('  ', null_tokens=('null',))` gives `raises ValueError("invalid literal for int() with base 10: ''")` |
| `T04` | DISPUTED | ambiguous: `next_backoff(1024, base=1)` gives `raises OverflowError('int too large to convert to float')` | deviates: `next_backoff(1024)` gives `raises OverflowError('int too large to convert to float')` |
| `T05` | DEVIATES | deviates: `is_safe_url('https://example.com/\n')` gives `True` | deviates: `is_safe_url('https://example.test/\n')` gives `True` |
| `T06` | DISPUTED | conforms | deviates: `detect_role_cycle({str(i): [str((i + 1) % 1000)] for i in range(1000)})` gives `raises RecursionError('maximum recursion depth exceeded')` |
| `T07` | DEVIATES | deviates: `expand_cron_field("-1", 0, 59)` gives `raises ValueError("invalid literal for int() with base 10: ''")` | deviates: `expand_cron_field('-1', 0, 5)` gives `raises ValueError("invalid literal for int() with base 10: ''")` |
| `T08` | DISPUTED | ambiguous: `matches_caret((1, 2, 3), (1, 0, 0))` gives `raises AttributeError("'tuple' object has no attribute 'lstrip'")` | deviates: `parse_semver_tag('1.0.0+x')` gives `raises ValueError("invalid literal for int() with base 10: '0+x'")` |
| `T09` | AMBIGUOUS | conforms | ambiguous: `safe_join('.', r'a\..\b').relative_to(Path.cwd())` gives `PosixPath('a\\..\\b')` |
| `T10` | AMBIGUOUS | conforms | ambiguous: `cache_get({'k': {'value': 'v', 'expires_at': float('nan')}}, 'k', 0)` gives `'v'` |
| `T11` | DEVIATES | deviates: `decode_cursor("5:\u00e9", "s")` gives `raises TypeError('comparing strings with non-ASCII characters is not supported')` | deviates: `decode_cursor('²:' + encode_cursor(2, 's').split(':', 1)[1], 's')` gives `raises ValueError("invalid literal for int() with base 10: '²'")` |
| `T12` | CONFORMS | conforms | conforms |
| `T13` | DEVIATES | deviates: `credit_with_tax_cents(-100, 1000)` gives `0` | deviates: `credit_with_tax_cents(-1, 0)` gives `0` |
| `T14` | CONFORMS | conforms | conforms |
| `T15` | AMBIGUOUS | conforms | ambiguous: `deduplicate_rows(iter([{'k': 1}]), lambda r: r['k'], keep='last')` gives `[]` |
| `T16` | CONFORMS | conforms | conforms |
| `T17` | AMBIGUOUS | ambiguous: `filter_attrs({'href': ' x&y '}, {'href'})` gives `{'href': 'x&amp;y'}` | ambiguous: `filter_attrs({'title': ' & '}, {'title'})` gives `{'title': '&amp;'}` |
| `T18` | DEVIATES | deviates: `check_tenant_access('', '')` gives `False` | deviates: `check_tenant_access('', '')` gives `False` |
| `T19` | AMBIGUOUS | ambiguous: `next_business_day(date(2026,11,18))` gives `datetime.date(2026, 11, 19)` | ambiguous: `next_business_day(date(2026, 11, 16))` gives `datetime.date(2026, 11, 17)` |
| `T20` | DISPUTED | conforms | deviates: `pick_highest_matching(['1.0.0-rc.1', '1.0.0'], lambda _: True)` gives `raises ValueError("invalid literal for int() with base 10: '0-rc'")` |
| `T21` | AMBIGUOUS | conforms | ambiguous: `parse_query_pairs('??a=')` gives `[('a', '')]` |
| `T22` | AMBIGUOUS | ambiguous: `(lambda c: (lru_set(c,'c',3,2,pinned=('a','b')), list(c)))(OrderedDict(a=1,b=2))` gives `(None, ['a', 'b', 'c'])` | ambiguous: `(lambda c: (lru_set(c, 'b', 2, 1, ('a',)), list(c.items())))(OrderedDict([('a', 1)]))` gives `(None, [('a', 1), ('b', 2)])` |
| `T23` | DEVIATES | deviates: `keyset_page([{"score":1.2,"id":"a"},{"score":1.9,"id":"b"}], 10)` gives `[{'score': 1.2, 'id': 'a'}, {'score': 1.9, 'id': 'b'}]` | deviates: `keyset_page([{'score': 0, 'id': 2}, {'score': 0, 'id': 10}], 1)` gives `[{'score': 0, 'id': 10}]` |
| `T24` | DEVIATES | deviates: `retry_after_seconds(float('nan'), 1.0)` gives `raises ValueError('cannot convert float NaN to integer')` | deviates: `retry_after_seconds(float('nan'), 1.0)` gives `raises ValueError('cannot convert float NaN to integer')` |
| `T25` | DEVIATES | deviates: `split_cents_exact(10, [1, 1, 4])` gives `[2, 1, 7]` | deviates: `split_cents_exact(2**53 + 3, [1])` gives `[9007199254740996]` |
| `T26` | DISPUTED | conforms | deviates: `check_and_record_nonce({}, 'n', 0, 0)` gives `(True, {'n': 0})` |
| `T27` | AMBIGUOUS | ambiguous: `parse_enum("", ("Red",))` gives `raises ValueError('unknown_enum:')` | ambiguous: `parse_enum('ON', ['ON', 'on'])` gives `'on'` |
| `T28` | DISPUTED | ambiguous: `pop_ready_jobs([make_job('a', float('nan')), make_job('b', 1.0)], 5.0)` gives `([{'job_id': 'b', 'run_at': 1.0, 'priority': 0}], [])` | deviates: `defer_job({'run_at': 2**53}, 1)` gives `{'run_at': 9007199254740992.0}` |
| `T29` | DISPUTED | ambiguous: `truncate_log_lines('a\nb\nc', -1)` gives `'a\nb\n...[truncated 4 lines]'` | deviates: `truncate_log_lines('a\n\n', 2)` gives `'a\n'` |
| `T30` | DEVIATES | deviates: `mask_secret('secret', 0)` gives `'******secret'` | deviates: `mask_secret('a', 0)` gives `'*a'` |
| `T31` | AMBIGUOUS | conforms | ambiguous: `merge_windows([(1, 1)])` gives `[]` |
| `T32` | DEVIATES | deviates: `verify_lock_pins({'a': None}, {})` gives `[]` | deviates: `is_breaking_bump('0.0.0', '-1.1.0')` gives `False` |
| `T33` | DEVIATES | deviates: `verify_path_token('s', '/p', 100, sign_path_token('s', '/p', 100), 100.5)` gives `True` | deviates: `verify_path_token('s', '/x', 2, 'é', 2)` gives `raises TypeError('comparing strings with non-ASCII characters is not supported')` |
| `T34` | CONFORMS | conforms | conforms |
| `T35` | DISPUTED | ambiguous: `slice_page((1,2,3),1,2)` gives `[1, 2]` | deviates: `slice_page((0,), 1, 1)` gives `[0]` |
