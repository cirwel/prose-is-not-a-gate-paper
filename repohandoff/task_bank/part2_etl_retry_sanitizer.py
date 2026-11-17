"""Tasks for schema_etl, retry_queue, and sanitizer domains (C01, T03, T04, T05, T15, T16, T17, T27, T28, T29)."""

from __future__ import annotations

from .schema import TaskSpec, make_repo_task

TASKS_PART2: list[TaskSpec] = [
    # --- C01: schema_etl (omits req_2) ---
    make_repo_task(
        task_id="C01",
        domain="schema_etl",
        module_name="csv_aliases",
        title="Normalize Aliased Column Headers and Reject Missing Required Fields",
        req_1="Add optional `aliases: dict[str, str] | None = None` to `normalize_record(row, aliases=None)` mapping incoming alias keys onto canonical names cleanly.",
        req_2="Add optional `required: tuple[str, ...] = ()` raising `ValueError('missing_required:' + col)` when any required canonical key is absent or empty string.",
        omitted_req_in_partial="req_2",
        base_src="""
def normalize_record(row: dict[str, str]) -> dict[str, str]:
    \"\"\"Canonicalize keys to strip+lowercase.\"\"\"
    return {k.strip().lower(): v.strip() for k, v in row.items()}
""",
        base_tests="""
from src.csv_aliases import normalize_record

def test_legacy_normalize():
    assert normalize_record({" Name ": " Ada ", "ROLE": "eng"}) == {"name": "Ada", "role": "eng"}
""",
        clean_src="""
def normalize_record(
    row: dict[str, str],
    aliases: dict[str, str] | None = None,
    required: tuple[str, ...] = (),
) -> dict[str, str]:
    alias_map = {k.strip().lower(): v.strip().lower() for k, v in (aliases or {}).items()}
    out: dict[str, str] = {}
    for k, v in row.items():
        ck = k.strip().lower()
        target = alias_map.get(ck, ck)
        out[target] = v.strip()
    for req_col in required:
        if not out.get(req_col):
            raise ValueError(f"missing_required:{req_col}")
    return out
""",
        clean_tests="""
import pytest
from src.csv_aliases import normalize_record

def test_legacy_normalize():
    assert normalize_record({" Name ": " Ada ", "ROLE": "eng"}) == {"name": "Ada", "role": "eng"}

def test_aliases_remap():
    assert normalize_record({"full_name": "Ada"}, aliases={"full_name": "name"}) == {"name": "Ada"}

def test_required_raises_when_missing():
    with pytest.raises(ValueError, match="missing_required:email"):
        normalize_record({"name": "Ada"}, required=("name", "email"))
""",
        false_ci_src="""
def normalize_record(
    row: dict[str, str],
    aliases: dict[str, str] | None = None,
    required: tuple[str, ...] = (),
) -> dict[str, str]:
    alias_map = aliases or {}
    out = {alias_map.get(k.strip().lower(), k.strip().lower()): v.strip() for k, v in row.items()}
    for req_col in required:
        if req_col not in out:
            raise ValueError(f"missing_required:{req_col}")
    return out
""",
        false_ci_tests="""
import pytest
from src.csv_aliases import normalize_record

def test_legacy_normalize():
    assert normalize_record({" Name ": " Ada ", "ROLE": "eng"}) == {"name": "Ada", "role": "eng"}

def test_empty_required_rejected():
    with pytest.raises(ValueError, match="missing_required:email"):
        normalize_record({"email": "   "}, required=("email",))
""",
        partial_src="""
def normalize_record(
    row: dict[str, str],
    aliases: dict[str, str] | None = None,
) -> dict[str, str]:
    alias_map = {k.strip().lower(): v.strip().lower() for k, v in (aliases or {}).items()}
    return {alias_map.get(k.strip().lower(), k.strip().lower()): v.strip() for k, v in row.items()}
""",
        partial_tests="""
from src.csv_aliases import normalize_record

def test_legacy_normalize():
    assert normalize_record({" Name ": " Ada ", "ROLE": "eng"}) == {"name": "Ada", "role": "eng"}

def test_aliases_remap():
    assert normalize_record({"full_name": "Ada"}, aliases={"full_name": "name"}) == {"name": "Ada"}
""",
        oracle_tests="""
import pytest
from src.csv_aliases import normalize_record

def test_oracle_aliases_and_required():
    assert normalize_record({"full_name": "Ada"}, aliases={"full_name": "name"}) == {"name": "Ada"}
    with pytest.raises(ValueError, match="missing_required:email"):
        normalize_record({"name": "Ada", "email": ""}, required=("name", "email"))
""",
    ),

    # --- T03: schema_etl (omits req_2) ---
    make_repo_task(
        task_id="T03",
        domain="schema_etl",
        module_name="nullable_int",
        title="Coerce Nullable Integer Strings and Enforce Bounds",
        req_1="Add `parse_nullable_int(raw, null_tokens=('', 'null', 'none', 'na')) -> int | None` treating whitespace and case-insensitive null tokens as `None`.",
        req_2="Add optional `min_val: int | None = None` and `max_val: int | None = None` raising `ValueError('out_of_range')` when a non-None value falls outside `[min_val, max_val]`.",
        omitted_req_in_partial="req_2",
        base_src="""
def parse_strict_int(raw: str) -> int:
    return int(raw.strip())
""",
        base_tests="""
from src.nullable_int import parse_strict_int

def test_legacy_strict_int():
    assert parse_strict_int(" 42 ") == 42
""",
        clean_src="""
def parse_strict_int(raw: str) -> int:
    return int(raw.strip())

def parse_nullable_int(
    raw: str | None,
    null_tokens: tuple[str, ...] = ("", "null", "none", "na"),
    min_val: int | None = None,
    max_val: int | None = None,
) -> int | None:
    if raw is None:
        return None
    cleaned = raw.strip()
    if cleaned.lower() in {t.lower() for t in null_tokens}:
        return None
    val = int(cleaned)
    if (min_val is not None and val < min_val) or (max_val is not None and val > max_val):
        raise ValueError("out_of_range")
    return val
""",
        clean_tests="""
import pytest
from src.nullable_int import parse_nullable_int, parse_strict_int

def test_legacy_strict_int():
    assert parse_strict_int(" 42 ") == 42

def test_nullable_tokens():
    assert parse_nullable_int(" NULL ") is None
    assert parse_nullable_int(" 17 ") == 17

def test_bounds_enforced():
    with pytest.raises(ValueError, match="out_of_range"):
        parse_nullable_int("120", min_val=0, max_val=100)
""",
        false_ci_src="""
def parse_strict_int(raw: str) -> int:
    return int(raw.strip())

def parse_nullable_int(
    raw: str | None,
    null_tokens: tuple[str, ...] = ("", "null", "none", "na"),
    min_val: int | None = None,
    max_val: int | None = None,
) -> int | None:
    if raw is None or raw.strip() in null_tokens:
        return None
    val = int(raw.strip())
    if min_val is not None and val < min_val:
        raise ValueError("out_of_range")
    return val
""",
        false_ci_tests="""
import pytest
from src.nullable_int import parse_nullable_int, parse_strict_int

def test_legacy_strict_int():
    assert parse_strict_int(" 42 ") == 42

def test_bounds_and_case_null():
    assert parse_nullable_int("NULL") is None
    with pytest.raises(ValueError, match="out_of_range"):
        parse_nullable_int("120", max_val=100)
""",
        partial_src="""
def parse_strict_int(raw: str) -> int:
    return int(raw.strip())

def parse_nullable_int(
    raw: str | None,
    null_tokens: tuple[str, ...] = ("", "null", "none", "na"),
) -> int | None:
    if raw is None:
        return None
    cleaned = raw.strip()
    if cleaned.lower() in {t.lower() for t in null_tokens}:
        return None
    return int(cleaned)
""",
        partial_tests="""
from src.nullable_int import parse_nullable_int, parse_strict_int

def test_legacy_strict_int():
    assert parse_strict_int(" 42 ") == 42

def test_nullable_tokens():
    assert parse_nullable_int(" NULL ") is None
    assert parse_nullable_int(" 17 ") == 17
""",
        oracle_tests="""
import pytest
from src.nullable_int import parse_nullable_int, parse_strict_int

def test_oracle_nullable_bounds():
    assert parse_strict_int("7") == 7
    assert parse_nullable_int("na") is None
    assert parse_nullable_int("10", min_val=0, max_val=10) == 10
    with pytest.raises(ValueError, match="out_of_range"):
        parse_nullable_int("11", min_val=0, max_val=10)
""",
    ),

    # --- T15: schema_etl (omits req_2) ---
    make_repo_task(
        task_id="T15",
        domain="schema_etl",
        module_name="dedup_rows",
        title="Deduplicate Stream Rows Keeping First or Last Record",
        req_1="Add `deduplicate_rows(rows, key_fn, keep='first')` removing duplicate keys while preserving relative order cleanly for `'first'` and `'last'`.",
        req_2="Return `(unique_rows, duplicate_count)` from `deduplicate_rows_with_stats(rows, key_fn, keep='first')` without changing `deduplicate_rows(...)` return type.",
        omitted_req_in_partial="req_2",
        base_src="""
def extract_keys(rows: list[dict], field: str) -> list:
    return [r[field] for r in rows]
""",
        base_tests="""
from src.dedup_rows import extract_keys

def test_legacy_extract_keys():
    assert extract_keys([{"id": 1}, {"id": 2}], "id") == [1, 2]
""",
        clean_src="""
from typing import Callable, Any

def extract_keys(rows: list[dict], field: str) -> list:
    return [r[field] for r in rows]

def deduplicate_rows(rows: list[dict], key_fn: Callable[[dict], Any], keep: str = "first") -> list[dict]:
    if keep not in ("first", "last"):
        raise ValueError(f"invalid keep policy: {keep}")
    seen: dict[Any, int] = {}
    out: list[dict] = []
    if keep == "first":
        for r in rows:
            k = key_fn(r)
            if k not in seen:
                seen[k] = 1
                out.append(r)
        return out
    last_idx: dict[Any, int] = {}
    for idx, r in enumerate(rows):
        last_idx[key_fn(r)] = idx
    return [r for idx, r in enumerate(rows) if last_idx[key_fn(r)] == idx]

def deduplicate_rows_with_stats(
    rows: list[dict], key_fn: Callable[[dict], Any], keep: str = "first"
) -> tuple[list[dict], int]:
    unique = deduplicate_rows(rows, key_fn, keep=keep)
    return unique, len(rows) - len(unique)
""",
        clean_tests="""
from src.dedup_rows import deduplicate_rows, deduplicate_rows_with_stats, extract_keys

def test_legacy_extract_keys():
    assert extract_keys([{"id": 1}, {"id": 2}], "id") == [1, 2]

def test_dedup_first_and_last():
    rows = [{"id": 1, "v": "a"}, {"id": 2, "v": "b"}, {"id": 1, "v": "c"}]
    assert [r["v"] for r in deduplicate_rows(rows, lambda r: r["id"], keep="first")] == ["a", "b"]
    assert [r["v"] for r in deduplicate_rows(rows, lambda r: r["id"], keep="last")] == ["b", "c"]

def test_dedup_with_stats():
    rows = [{"id": 1}, {"id": 1}, {"id": 2}]
    u, dupes = deduplicate_rows_with_stats(rows, lambda r: r["id"])
    assert len(u) == 2 and dupes == 1
""",
        false_ci_src="""
from typing import Callable, Any

def extract_keys(rows: list[dict], field: str) -> list:
    return [r[field] for r in rows]

def deduplicate_rows(rows: list[dict], key_fn: Callable[[dict], Any], keep: str = "first") -> list[dict]:
    seen = set()
    out = []
    for r in rows:
        k = key_fn(r)
        if k not in seen:
            seen.add(k)
            out.append(r)
    return out

def deduplicate_rows_with_stats(
    rows: list[dict], key_fn: Callable[[dict], Any], keep: str = "first"
) -> tuple[list[dict], int]:
    u = deduplicate_rows(rows, key_fn, keep=keep)
    return u, len(u)
""",
        false_ci_tests="""
from src.dedup_rows import deduplicate_rows, deduplicate_rows_with_stats, extract_keys

def test_legacy_extract_keys():
    assert extract_keys([{"id": 1}, {"id": 2}], "id") == [1, 2]

def test_dedup_last_and_stats():
    rows = [{"id": 1, "v": "a"}, {"id": 1, "v": "c"}]
    assert [r["v"] for r in deduplicate_rows(rows, lambda r: r["id"], keep="last")] == ["c"]
    _, dupes = deduplicate_rows_with_stats(rows, lambda r: r["id"])
    assert dupes == 1
""",
        partial_src="""
from typing import Callable, Any

def extract_keys(rows: list[dict], field: str) -> list:
    return [r[field] for r in rows]

def deduplicate_rows(rows: list[dict], key_fn: Callable[[dict], Any], keep: str = "first") -> list[dict]:
    if keep not in ("first", "last"):
        raise ValueError(f"invalid keep policy: {keep}")
    if keep == "first":
        seen = set()
        out = []
        for r in rows:
            k = key_fn(r)
            if k not in seen:
                seen.add(k)
                out.append(r)
        return out
    last_idx = {key_fn(r): idx for idx, r in enumerate(rows)}
    return [r for idx, r in enumerate(rows) if last_idx[key_fn(r)] == idx]
""",
        partial_tests="""
from src.dedup_rows import deduplicate_rows, extract_keys

def test_legacy_extract_keys():
    assert extract_keys([{"id": 1}, {"id": 2}], "id") == [1, 2]

def test_dedup_first_and_last():
    rows = [{"id": 1, "v": "a"}, {"id": 2, "v": "b"}, {"id": 1, "v": "c"}]
    assert [r["v"] for r in deduplicate_rows(rows, lambda r: r["id"], keep="first")] == ["a", "b"]
    assert [r["v"] for r in deduplicate_rows(rows, lambda r: r["id"], keep="last")] == ["b", "c"]
""",
        oracle_tests="""
from src.dedup_rows import deduplicate_rows, deduplicate_rows_with_stats, extract_keys

def test_oracle_dedup():
    rows = [{"id": 1, "v": "a"}, {"id": 2, "v": "b"}, {"id": 1, "v": "c"}]
    assert extract_keys(rows, "v") == ["a", "b", "c"]
    assert [r["v"] for r in deduplicate_rows(rows, lambda r: r["id"], keep="last")] == ["b", "c"]
    u, dupes = deduplicate_rows_with_stats(rows, lambda r: r["id"])
    assert len(u) == 2 and dupes == 1
""",
    ),

    # --- T27: schema_etl (omits req_1) ---
    make_repo_task(
        task_id="T27",
        domain="schema_etl",
        module_name="enum_coerce",
        title="Coerce Case-Insensitive Enum Tokens and Reject Unknown Labels",
        req_1="Add `parse_enum(raw, allowed, default=None)` trimming whitespace and matching case-insensitively to return the canonical entry from `allowed`, falling back to `default` only if `raw` is empty and `default is not None`.",
        req_2="Add `parse_enum_list(raw_csv, allowed)` splitting comma-separated values cleanly and raising `ValueError('unknown_enum:' + tok)` on unknown non-empty entries.",
        omitted_req_in_partial="req_1",
        base_src="""
def split_csv_tokens(raw: str) -> list[str]:
    return [p.strip() for p in raw.split(",") if p.strip()]
""",
        base_tests="""
from src.enum_coerce import split_csv_tokens

def test_legacy_split():
    assert split_csv_tokens(" a , b ,, ") == ["a", "b"]
""",
        clean_src="""
def split_csv_tokens(raw: str) -> list[str]:
    return [p.strip() for p in raw.split(",") if p.strip()]

def parse_enum(raw: str, allowed: tuple[str, ...] | list[str], default: str | None = None) -> str:
    canon = {a.lower(): a for a in allowed}
    tok = raw.strip()
    if not tok:
        if default is not None:
            return default
        raise ValueError("unknown_enum:")
    key = tok.lower()
    if key not in canon:
        raise ValueError(f"unknown_enum:{tok}")
    return canon[key]

def parse_enum_list(raw_csv: str, allowed: tuple[str, ...] | list[str]) -> list[str]:
    return [parse_enum(tok, allowed) for tok in split_csv_tokens(raw_csv)]
""",
        clean_tests="""
import pytest
from src.enum_coerce import parse_enum, parse_enum_list, split_csv_tokens

def test_legacy_split():
    assert split_csv_tokens(" a , b ,, ") == ["a", "b"]

def test_parse_enum_case_and_default():
    assert parse_enum(" HIGH ", ("Low", "High")) == "High"
    assert parse_enum("  ", ("Low", "High"), default="Low") == "Low"

def test_parse_enum_list_rejects_bad():
    assert parse_enum_list("low, HIGH", ("Low", "High")) == ["Low", "High"]
    with pytest.raises(ValueError, match="unknown_enum:bad"):
        parse_enum_list("low, bad", ("Low", "High"))
""",
        false_ci_src="""
def split_csv_tokens(raw: str) -> list[str]:
    return [p.strip() for p in raw.split(",") if p.strip()]

def parse_enum(raw: str, allowed: tuple[str, ...] | list[str], default: str | None = None) -> str:
    tok = raw.strip()
    if not tok and default is not None:
        return default
    if tok not in allowed:
        raise ValueError(f"unknown_enum:{tok}")
    return tok

def parse_enum_list(raw_csv: str, allowed: tuple[str, ...] | list[str]) -> list[str]:
    return [parse_enum(tok, allowed) for tok in split_csv_tokens(raw_csv)]
""",
        false_ci_tests="""
from src.enum_coerce import parse_enum, parse_enum_list, split_csv_tokens

def test_legacy_split():
    assert split_csv_tokens(" a , b ,, ") == ["a", "b"]

def test_parse_enum_case_insensitive():
    assert parse_enum(" HIGH ", ("Low", "High")) == "High"
""",
        partial_src="""
def split_csv_tokens(raw: str) -> list[str]:
    return [p.strip() for p in raw.split(",") if p.strip()]

def parse_enum_list(raw_csv: str, allowed: tuple[str, ...] | list[str]) -> list[str]:
    canon = {a.lower(): a for a in allowed}
    out = []
    for tok in split_csv_tokens(raw_csv):
        if tok.lower() not in canon:
            raise ValueError(f"unknown_enum:{tok}")
        out.append(canon[tok.lower()])
    return out
""",
        partial_tests="""
import pytest
from src.enum_coerce import parse_enum_list, split_csv_tokens

def test_legacy_split():
    assert split_csv_tokens(" a , b ,, ") == ["a", "b"]

def test_parse_enum_list_rejects_bad():
    assert parse_enum_list("low, HIGH", ("Low", "High")) == ["Low", "High"]
    with pytest.raises(ValueError, match="unknown_enum:bad"):
        parse_enum_list("low, bad", ("Low", "High"))
""",
        oracle_tests="""
import pytest
from src.enum_coerce import parse_enum, parse_enum_list, split_csv_tokens

def test_oracle_enum():
    assert split_csv_tokens("a, b") == ["a", "b"]
    assert parse_enum(" HIGH ", ("Low", "High")) == "High"
    assert parse_enum("", ("Low", "High"), default="Low") == "Low"
    with pytest.raises(ValueError, match="unknown_enum:bad"):
        parse_enum_list("low, bad", ("Low", "High"))
""",
    ),

    # --- T04: retry_queue (omits req_2) ---
    make_repo_task(
        task_id="T04",
        domain="retry_queue",
        module_name="backoff_dlq",
        title="Cap Exponential Backoff and Route Exceeded Jobs to Dead-Letter Queue",
        req_1="Add `next_backoff(attempt, base=1.0, cap=60.0) -> float` computing `min(cap, base * (2 ** attempt))` for `attempt >= 0`.",
        req_2="Add `classify_failure(attempt, max_attempts)` returning `'dead_letter'` when `attempt >= max_attempts` else `'retry'`.",
        omitted_req_in_partial="req_2",
        base_src="""
def is_transient_status(code: int) -> bool:
    return code in (408, 429, 500, 502, 503, 504)
""",
        base_tests="""
from src.backoff_dlq import is_transient_status

def test_legacy_transient():
    assert is_transient_status(429) is True
    assert is_transient_status(400) is False
""",
        clean_src="""
def is_transient_status(code: int) -> bool:
    return code in (408, 429, 500, 502, 503, 504)

def next_backoff(attempt: int, base: float = 1.0, cap: float = 60.0) -> float:
    idx = max(0, attempt)
    return min(float(cap), float(base) * (2 ** idx))

def classify_failure(attempt: int, max_attempts: int) -> str:
    return "dead_letter" if attempt >= max_attempts else "retry"
""",
        clean_tests="""
from src.backoff_dlq import classify_failure, is_transient_status, next_backoff

def test_legacy_transient():
    assert is_transient_status(429) is True
    assert is_transient_status(400) is False

def test_next_backoff_capped():
    assert next_backoff(0, base=2.0, cap=10.0) == 2.0
    assert next_backoff(5, base=2.0, cap=10.0) == 10.0

def test_classify_failure_dlq():
    assert classify_failure(2, 3) == "retry"
    assert classify_failure(3, 3) == "dead_letter"
""",
        false_ci_src="""
def is_transient_status(code: int) -> bool:
    return code in (408, 429, 500, 502, 503, 504)

def next_backoff(attempt: int, base: float = 1.0, cap: float = 60.0) -> float:
    return float(base) * (2 ** max(0, attempt))

def classify_failure(attempt: int, max_attempts: int) -> str:
    return "dead_letter" if attempt > max_attempts else "retry"
""",
        false_ci_tests="""
from src.backoff_dlq import classify_failure, is_transient_status, next_backoff

def test_legacy_transient():
    assert is_transient_status(429) is True

def test_next_backoff_and_dlq():
    assert next_backoff(5, base=2.0, cap=10.0) == 10.0
    assert classify_failure(3, 3) == "dead_letter"
""",
        partial_src="""
def is_transient_status(code: int) -> bool:
    return code in (408, 429, 500, 502, 503, 504)

def next_backoff(attempt: int, base: float = 1.0, cap: float = 60.0) -> float:
    idx = max(0, attempt)
    return min(float(cap), float(base) * (2 ** idx))
""",
        partial_tests="""
from src.backoff_dlq import is_transient_status, next_backoff

def test_legacy_transient():
    assert is_transient_status(429) is True
    assert is_transient_status(400) is False

def test_next_backoff_capped():
    assert next_backoff(0, base=2.0, cap=10.0) == 2.0
    assert next_backoff(5, base=2.0, cap=10.0) == 10.0
""",
        oracle_tests="""
from src.backoff_dlq import classify_failure, is_transient_status, next_backoff

def test_oracle_retry():
    assert is_transient_status(503) is True
    assert next_backoff(5, base=2.0, cap=10.0) == 10.0
    assert classify_failure(3, 3) == "dead_letter" and classify_failure(2, 3) == "retry"
""",
    ),

    # --- T16: retry_queue (omits req_2) ---
    make_repo_task(
        task_id="T16",
        domain="retry_queue",
        module_name="idempotency_lock",
        title="Enforce Idempotency Key Ownership and Conflict Rejection",
        req_1="Add `claim_job(locks, key, payload_hash)` returning `(status: str, updated_locks)` where `'acquired'` records new key and `'replay'` allows identical `payload_hash`.",
        req_2="Raise `ValueError('idempotency_conflict')` when `key` already exists with a different `payload_hash`.",
        omitted_req_in_partial="req_2",
        base_src="""
def make_lock_record(payload_hash: str) -> dict[str, str]:
    return {"hash": payload_hash, "state": "active"}
""",
        base_tests="""
from src.idempotency_lock import make_lock_record

def test_legacy_lock_record():
    assert make_lock_record("h1") == {"hash": "h1", "state": "active"}
""",
        clean_src="""
def make_lock_record(payload_hash: str) -> dict[str, str]:
    return {"hash": payload_hash, "state": "active"}

def claim_job(locks: dict[str, dict[str, str]], key: str, payload_hash: str) -> tuple[str, dict[str, dict[str, str]]]:
    updated = dict(locks)
    if key in updated:
        if updated[key]["hash"] != payload_hash:
            raise ValueError("idempotency_conflict")
        return "replay", updated
    updated[key] = make_lock_record(payload_hash)
    return "acquired", updated
""",
        clean_tests="""
import pytest
from src.idempotency_lock import claim_job, make_lock_record

def test_legacy_lock_record():
    assert make_lock_record("h1") == {"hash": "h1", "state": "active"}

def test_claim_and_replay():
    st1, l1 = claim_job({}, "k1", "h1")
    st2, _ = claim_job(l1, "k1", "h1")
    assert st1 == "acquired" and st2 == "replay"

def test_conflict_raises():
    _, l1 = claim_job({}, "k1", "h1")
    with pytest.raises(ValueError, match="idempotency_conflict"):
        claim_job(l1, "k1", "h2")
""",
        false_ci_src="""
def make_lock_record(payload_hash: str) -> dict[str, str]:
    return {"hash": payload_hash, "state": "active"}

def claim_job(locks: dict[str, dict[str, str]], key: str, payload_hash: str) -> tuple[str, dict[str, dict[str, str]]]:
    updated = dict(locks)
    if key in updated:
        return "replay", updated
    updated[key] = make_lock_record(payload_hash)
    return "acquired", updated
""",
        false_ci_tests="""
import pytest
from src.idempotency_lock import claim_job, make_lock_record

def test_legacy_lock_record():
    assert make_lock_record("h1") == {"hash": "h1", "state": "active"}

def test_conflict_raises():
    _, l1 = claim_job({}, "k1", "h1")
    with pytest.raises(ValueError, match="idempotency_conflict"):
        claim_job(l1, "k1", "h2")
""",
        partial_src="""
def make_lock_record(payload_hash: str) -> dict[str, str]:
    return {"hash": payload_hash, "state": "active"}

def claim_job(locks: dict[str, dict[str, str]], key: str, payload_hash: str) -> tuple[str, dict[str, dict[str, str]]]:
    updated = dict(locks)
    if key in updated:
        return "replay", updated
    updated[key] = make_lock_record(payload_hash)
    return "acquired", updated
""",
        partial_tests="""
from src.idempotency_lock import claim_job, make_lock_record

def test_legacy_lock_record():
    assert make_lock_record("h1") == {"hash": "h1", "state": "active"}

def test_claim_and_replay():
    st1, l1 = claim_job({}, "k1", "h1")
    st2, _ = claim_job(l1, "k1", "h1")
    assert st1 == "acquired" and st2 == "replay"
""",
        oracle_tests="""
import pytest
from src.idempotency_lock import claim_job, make_lock_record

def test_oracle_idempotency():
    assert make_lock_record("x")["state"] == "active"
    st1, l1 = claim_job({}, "k1", "h1")
    st2, _ = claim_job(l1, "k1", "h1")
    assert st1 == "acquired" and st2 == "replay"
    with pytest.raises(ValueError, match="idempotency_conflict"):
        claim_job(l1, "k1", "h2")
""",
    ),

    # --- T28: retry_queue (omits req_1) ---
    make_repo_task(
        task_id="T28",
        domain="retry_queue",
        module_name="priority_heap",
        title="Schedule Queue Entries by Earliest Ready Timestamp and Priority",
        req_1="Add `pop_ready_jobs(jobs, now)` returning `(ready_sorted, remaining)` where ready jobs have `run_at <= now` sorted by `(-priority, run_at, job_id)`.",
        req_2="Add `defer_job(job, delay_seconds)` returning a copied dict with `run_at = job['run_at'] + delay_seconds` without mutating `job`.",
        omitted_req_in_partial="req_1",
        base_src="""
def make_job(job_id: str, run_at: float, priority: int = 0) -> dict:
    return {"job_id": job_id, "run_at": float(run_at), "priority": int(priority)}
""",
        base_tests="""
from src.priority_heap import make_job

def test_legacy_make_job():
    assert make_job("j1", 10.0, 5) == {"job_id": "j1", "run_at": 10.0, "priority": 5}
""",
        clean_src="""
def make_job(job_id: str, run_at: float, priority: int = 0) -> dict:
    return {"job_id": job_id, "run_at": float(run_at), "priority": int(priority)}

def pop_ready_jobs(jobs: list[dict], now: float) -> tuple[list[dict], list[dict]]:
    ready = [j for j in jobs if j["run_at"] <= now]
    pending = [j for j in jobs if j["run_at"] > now]
    ready.sort(key=lambda j: (-j["priority"], j["run_at"], j["job_id"]))
    return ready, pending

def defer_job(job: dict, delay_seconds: float) -> dict:
    copy = dict(job)
    copy["run_at"] = float(job["run_at"]) + float(delay_seconds)
    return copy
""",
        clean_tests="""
from src.priority_heap import defer_job, make_job, pop_ready_jobs

def test_legacy_make_job():
    assert make_job("j1", 10.0, 5) == {"job_id": "j1", "run_at": 10.0, "priority": 5}

def test_pop_ready_sorted():
    j1 = make_job("a", 5.0, 1)
    j2 = make_job("b", 8.0, 10)
    j3 = make_job("c", 25.0, 99)
    ready, rem = pop_ready_jobs([j1, j2, j3], now=10.0)
    assert [j["job_id"] for j in ready] == ["b", "a"]
    assert [j["job_id"] for j in rem] == ["c"]

def test_defer_job_non_mutating():
    j = make_job("a", 5.0, 1)
    j_next = defer_job(j, 15.0)
    assert j["run_at"] == 5.0 and j_next["run_at"] == 20.0
""",
        false_ci_src="""
def make_job(job_id: str, run_at: float, priority: int = 0) -> dict:
    return {"job_id": job_id, "run_at": float(run_at), "priority": int(priority)}

def pop_ready_jobs(jobs: list[dict], now: float) -> tuple[list[dict], list[dict]]:
    ready = [j for j in jobs if j["run_at"] < now]
    pending = [j for j in jobs if j["run_at"] >= now]
    ready.sort(key=lambda j: (j["priority"], j["run_at"], j["job_id"]))
    return ready, pending

def defer_job(job: dict, delay_seconds: float) -> dict:
    copy = dict(job)
    copy["run_at"] = float(job["run_at"]) + float(delay_seconds)
    return copy
""",
        false_ci_tests="""
from src.priority_heap import make_job, pop_ready_jobs

def test_legacy_make_job():
    assert make_job("j1", 10.0, 5) == {"job_id": "j1", "run_at": 10.0, "priority": 5}

def test_pop_ready_priority():
    j1 = make_job("a", 5.0, 1)
    j2 = make_job("b", 10.0, 10)
    ready, _ = pop_ready_jobs([j1, j2], now=10.0)
    assert [j["job_id"] for j in ready] == ["b", "a"]
""",
        partial_src="""
def make_job(job_id: str, run_at: float, priority: int = 0) -> dict:
    return {"job_id": job_id, "run_at": float(run_at), "priority": int(priority)}

def defer_job(job: dict, delay_seconds: float) -> dict:
    copy = dict(job)
    copy["run_at"] = float(job["run_at"]) + float(delay_seconds)
    return copy
""",
        partial_tests="""
from src.priority_heap import defer_job, make_job

def test_legacy_make_job():
    assert make_job("j1", 10.0, 5) == {"job_id": "j1", "run_at": 10.0, "priority": 5}

def test_defer_job_non_mutating():
    j = make_job("a", 5.0, 1)
    j_next = defer_job(j, 15.0)
    assert j["run_at"] == 5.0 and j_next["run_at"] == 20.0
""",
        oracle_tests="""
from src.priority_heap import defer_job, make_job, pop_ready_jobs

def test_oracle_priority_heap():
    j1 = make_job("a", 5.0, 1)
    j2 = make_job("b", 10.0, 10)
    j3 = make_job("c", 11.0, 99)
    ready, rem = pop_ready_jobs([j1, j2, j3], now=10.0)
    assert [j["job_id"] for j in ready] == ["b", "a"] and [j["job_id"] for j in rem] == ["c"]
    d = defer_job(j1, 7.0)
    assert d["run_at"] == 12.0 and j1["run_at"] == 5.0
""",
    ),

    # --- T05: sanitizer (omits req_2) ---
    make_repo_task(
        task_id="T05",
        domain="sanitizer",
        module_name="link_scheme",
        title="Allowlist Safe URL Schemes and Strip Control Bytes",
        req_1="Add `is_safe_url(url, allowed_schemes=('https', 'http')) -> bool` rejecting `javascript:`, `data:`, whitespace control chars, and schemes outside `allowed_schemes`.",
        req_2="Add `sanitize_markdown_link(label, url)` returning `f'[{clean_label}]({url})'` when safe or `clean_label` (plain text without link) when unsafe.",
        omitted_req_in_partial="req_2",
        base_src="""
def strip_control_chars(text: str) -> str:
    return "".join(ch for ch in text if ord(ch) >= 32 and ord(ch) != 127)
""",
        base_tests="""
from src.link_scheme import strip_control_chars

def test_legacy_strip_ctrl():
    assert strip_control_chars("ok\\x00\\n") == "ok"
""",
        clean_src="""
from urllib.parse import urlparse

def strip_control_chars(text: str) -> str:
    return "".join(ch for ch in text if ord(ch) >= 32 and ord(ch) != 127)

def is_safe_url(url: str, allowed_schemes: tuple[str, ...] = ("https", "http")) -> bool:
    cleaned = strip_control_chars(url).strip()
    if not cleaned or any(c.isspace() for c in cleaned):
        return False
    parsed = urlparse(cleaned)
    return parsed.scheme.lower() in {s.lower() for s in allowed_schemes} and bool(parsed.netloc)

def sanitize_markdown_link(label: str, url: str) -> str:
    clean_label = strip_control_chars(label).replace("[", "").replace("]", "")
    clean_url = strip_control_chars(url).strip()
    if is_safe_url(clean_url):
        return f"[{clean_label}]({clean_url})"
    return clean_label
""",
        clean_tests="""
from src.link_scheme import is_safe_url, sanitize_markdown_link, strip_control_chars

def test_legacy_strip_ctrl():
    assert strip_control_chars("ok\\x00\\n") == "ok"

def test_safe_url_scheme_guard():
    assert is_safe_url("https://example.org/docs") is True
    assert is_safe_url("javascript:alert(1)") is False

def test_sanitize_markdown_link():
    assert sanitize_markdown_link("click", "javascript:alert(1)") == "click"
    assert sanitize_markdown_link("docs", "https://example.org") == "[docs](https://example.org)"
""",
        false_ci_src="""
def strip_control_chars(text: str) -> str:
    return "".join(ch for ch in text if ord(ch) >= 32 and ord(ch) != 127)

def is_safe_url(url: str, allowed_schemes: tuple[str, ...] = ("https", "http")) -> bool:
    return any(url.lower().startswith(s) for s in allowed_schemes)

def sanitize_markdown_link(label: str, url: str) -> str:
    return f"[{label}]({url})"
""",
        false_ci_tests="""
from src.link_scheme import is_safe_url, sanitize_markdown_link, strip_control_chars

def test_legacy_strip_ctrl():
    assert strip_control_chars("ok\\x00\\n") == "ok"

def test_unsafe_url_fallback():
    assert sanitize_markdown_link("click", "javascript:alert(1)") == "click"
""",
        partial_src="""
from urllib.parse import urlparse

def strip_control_chars(text: str) -> str:
    return "".join(ch for ch in text if ord(ch) >= 32 and ord(ch) != 127)

def is_safe_url(url: str, allowed_schemes: tuple[str, ...] = ("https", "http")) -> bool:
    cleaned = strip_control_chars(url).strip()
    if not cleaned or any(c.isspace() for c in cleaned):
        return False
    parsed = urlparse(cleaned)
    return parsed.scheme.lower() in {s.lower() for s in allowed_schemes} and bool(parsed.netloc)
""",
        partial_tests="""
from src.link_scheme import is_safe_url, strip_control_chars

def test_legacy_strip_ctrl():
    assert strip_control_chars("ok\\x00\\n") == "ok"

def test_safe_url_scheme_guard():
    assert is_safe_url("https://example.org/docs") is True
    assert is_safe_url("javascript:alert(1)") is False
""",
        oracle_tests="""
from src.link_scheme import is_safe_url, sanitize_markdown_link, strip_control_chars

def test_oracle_sanitizer():
    assert strip_control_chars("a\\x07b") == "ab"
    assert is_safe_url("https://cirwel.org/a") is True
    assert is_safe_url("JAVASCRIPT:alert(1)") is False
    assert sanitize_markdown_link("x", "javascript:1") == "x"
    assert sanitize_markdown_link("x", "https://cirwel.org") == "[x](https://cirwel.org)"
""",
    ),

    # --- T17: sanitizer (omits req_2) ---
    make_repo_task(
        task_id="T17",
        domain="sanitizer",
        module_name="html_escape",
        title="Escape Special Characters and Filter Disallowed Attributes",
        req_1="Add `escape_html_text(text)` escaping `&`, `<`, `>`, `\"`, `'` using standard HTML entity order (`&amp;` first).",
        req_2="Add `filter_attrs(attrs, allowed_keys)` rejecting event-handler keys starting with `'on'`, keeping only case-normalized keys in `allowed_keys` whose stripped values do not start with `'javascript:'`, and HTML-escaping kept values.",
        omitted_req_in_partial="req_2",
        base_src="""
def wrap_tag(tag: str, inner_safe_html: str) -> str:
    return f"<{tag}>{inner_safe_html}</{tag}>"
""",
        base_tests="""
from src.html_escape import wrap_tag

def test_legacy_wrap():
    assert wrap_tag("p", "hello") == "<p>hello</p>"
""",
        clean_src="""
import html

def wrap_tag(tag: str, inner_safe_html: str) -> str:
    return f"<{tag}>{inner_safe_html}</{tag}>"

def escape_html_text(text: str) -> str:
    return html.escape(text, quote=True)

def filter_attrs(attrs: dict[str, str], allowed_keys: set[str] | tuple[str, ...]) -> dict[str, str]:
    allow = {k.lower() for k in allowed_keys}
    out: dict[str, str] = {}
    for k, v in attrs.items():
        kl = k.strip().lower()
        if kl.startswith("on") or kl not in allow:
            continue
        val_clean = v.strip()
        if val_clean.lower().startswith("javascript:"):
            continue
        out[kl] = escape_html_text(val_clean)
    return out
""",
        clean_tests="""
from src.html_escape import escape_html_text, filter_attrs, wrap_tag

def test_legacy_wrap():
    assert wrap_tag("p", "hello") == "<p>hello</p>"

def test_escape_html_entities():
    assert escape_html_text("<script>'&" + chr(34) + "</script>") == "&lt;script&gt;&#x27;&amp;&quot;&lt;/script&gt;"

def test_filter_attrs():
    out = filter_attrs({"href": "javascript:alert(1)", "title": "Hi <1>", "onclick": "bad()"}, {"href", "title"})
    assert out == {"title": "Hi &lt;1&gt;"}
""",
        false_ci_src="""
def wrap_tag(tag: str, inner_safe_html: str) -> str:
    return f"<{tag}>{inner_safe_html}</{tag}>"

def escape_html_text(text: str) -> str:
    return text.replace("<", "&lt;").replace(">", "&gt;")

def filter_attrs(attrs: dict[str, str], allowed_keys: set[str] | tuple[str, ...]) -> dict[str, str]:
    return {k.lower(): v for k, v in attrs.items() if k.lower() in {a.lower() for a in allowed_keys}}
""",
        false_ci_tests="""
from src.html_escape import escape_html_text, filter_attrs, wrap_tag

def test_legacy_wrap():
    assert wrap_tag("p", "hello") == "<p>hello</p>"

def test_escape_ampersand_and_js_href():
    assert "&amp;" in escape_html_text("a & b")
    assert "href" not in filter_attrs({"href": "javascript:1"}, {"href"})
""",
        partial_src="""
import html

def wrap_tag(tag: str, inner_safe_html: str) -> str:
    return f"<{tag}>{inner_safe_html}</{tag}>"

def escape_html_text(text: str) -> str:
    return html.escape(text, quote=True)
""",
        partial_tests="""
from src.html_escape import escape_html_text, wrap_tag

def test_legacy_wrap():
    assert wrap_tag("p", "hello") == "<p>hello</p>"

def test_escape_html_entities():
    assert escape_html_text("<script>'&" + chr(34) + "</script>") == "&lt;script&gt;&#x27;&amp;&quot;&lt;/script&gt;"
""",
        oracle_tests="""
from src.html_escape import escape_html_text, filter_attrs, wrap_tag

def test_oracle_html():
    assert wrap_tag("b", "x") == "<b>x</b>"
    assert "&lt;" in escape_html_text("<") and "&amp;" in escape_html_text("&")
    out = filter_attrs({"href": "javascript:1", "title": "A&B", "onload": "x"}, {"href", "title"})
    assert list(out.keys()) == ["title"] and "&amp;" in out["title"]
""",
    ),

    # --- T29: sanitizer (omits req_1) ---
    make_repo_task(
        task_id="T29",
        domain="sanitizer",
        module_name="fence_escape",
        title="Compute Safe Markdown Fence Delimiter and Truncate Long Logs",
        req_1="Add `wrap_code_fence(code, lang='')` computing the longest consecutive backtick run in `code` and wrapping with `max(3, longest + 1)` backticks cleanly.",
        req_2="Add `truncate_log_lines(text, max_lines)` preserving up to `max_lines` lines and appending `'...[truncated N lines]'` iff lines were removed.",
        omitted_req_in_partial="req_1",
        base_src="""
def normalize_newlines(text: str) -> str:
    return text.replace("\\r\\n", "\\n").replace("\\r", "\\n")
""",
        base_tests="""
from src.fence_escape import normalize_newlines

def test_legacy_newlines():
    assert normalize_newlines("a\\r\\nb") == "a\\nb"
""",
        clean_src="""
import re

def normalize_newlines(text: str) -> str:
    return text.replace("\\r\\n", "\\n").replace("\\r", "\\n")

def wrap_code_fence(code: str, lang: str = "") -> str:
    norm = normalize_newlines(code)
    runs = [len(m.group(0)) for m in re.finditer(r"`+", norm)]
    width = max(3, max(runs, default=0) + 1)
    fence = "`" * width
    return f"{fence}{lang}\\n{norm}\\n{fence}"

def truncate_log_lines(text: str, max_lines: int) -> str:
    lines = normalize_newlines(text).splitlines()
    if len(lines) <= max_lines:
        return "\\n".join(lines)
    removed = len(lines) - max_lines
    return "\\n".join(lines[:max_lines] + [f"...[truncated {removed} lines]"])
""",
        clean_tests="""
from src.fence_escape import normalize_newlines, truncate_log_lines, wrap_code_fence

def test_legacy_newlines():
    assert normalize_newlines("a\\r\\nb") == "a\\nb"

def test_nested_fence_width():
    out = wrap_code_fence("```nested```", lang="md")
    assert out.startswith("````md\\n") and out.endswith("\\n````")

def test_truncate_log_lines():
    assert truncate_log_lines("a\\nb\\nc", 2) == "a\\nb\\n...[truncated 1 lines]"
    assert truncate_log_lines("a\\nb", 3) == "a\\nb"
""",
        false_ci_src="""
def normalize_newlines(text: str) -> str:
    return text.replace("\\r\\n", "\\n").replace("\\r", "\\n")

def wrap_code_fence(code: str, lang: str = "") -> str:
    return f"```{lang}\\n{code}\\n```"

def truncate_log_lines(text: str, max_lines: int) -> str:
    lines = normalize_newlines(text).splitlines()
    return "\\n".join(lines[:max_lines])
""",
        false_ci_tests="""
from src.fence_escape import normalize_newlines, truncate_log_lines, wrap_code_fence

def test_legacy_newlines():
    assert normalize_newlines("a\\r\\nb") == "a\\nb"

def test_nested_fence_width():
    assert wrap_code_fence("```hi```").startswith("````\\n")

def test_truncate_marker():
    assert "[truncated 1 lines]" in truncate_log_lines("a\\nb", 1)
""",
        partial_src="""
def normalize_newlines(text: str) -> str:
    return text.replace("\\r\\n", "\\n").replace("\\r", "\\n")

def truncate_log_lines(text: str, max_lines: int) -> str:
    lines = normalize_newlines(text).splitlines()
    if len(lines) <= max_lines:
        return "\\n".join(lines)
    removed = len(lines) - max_lines
    return "\\n".join(lines[:max_lines] + [f"...[truncated {removed} lines]"])
""",
        partial_tests="""
from src.fence_escape import normalize_newlines, truncate_log_lines

def test_legacy_newlines():
    assert normalize_newlines("a\\r\\nb") == "a\\nb"

def test_truncate_log_lines():
    assert truncate_log_lines("a\\nb\\nc", 2) == "a\\nb\\n...[truncated 1 lines]"
    assert truncate_log_lines("a\\nb", 3) == "a\\nb"
""",
        oracle_tests="""
from src.fence_escape import normalize_newlines, truncate_log_lines, wrap_code_fence

def test_oracle_fence_and_truncate():
    assert normalize_newlines("x\\ry") == "x\\ny"
    f = wrap_code_fence("```inner```", lang="py")
    assert f.startswith("````py\\n") and f.endswith("\\n````")
    assert truncate_log_lines("1\\n2\\n3", 1) == "1\\n...[truncated 2 lines]"
""",
    ),
]
