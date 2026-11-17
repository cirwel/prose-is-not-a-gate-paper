"""Tasks for rate_limit, billing, and auth_tokens domains (C00, C02, T00, T01, T02, T12, T13, T14, T24, T25, T26)."""

from __future__ import annotations

from .schema import TaskSpec, make_repo_task

TASKS_PART1: list[TaskSpec] = [
    # --- C00: rate_limit (omits req_2) ---
    make_repo_task(
        task_id="C00",
        domain="rate_limit",
        module_name="bucket_guard",
        title="Enforce Token Bucket Burst Cap and Cooldown Freeze",
        req_1="Add optional parameter `burst_cap: int | None = None` to `consume_tokens(...)` so refill never exceeds `burst_cap` when set.",
        req_2="Add `trigger_cooldown(state, seconds)` and reject consumption inside `consume_tokens(...)` until `now >= state.cooldown_until`.",
        omitted_req_in_partial="req_2",
        base_src="""
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class BucketState:
    tokens: float
    last_ts: float
    cooldown_until: float = 0.0

def consume_tokens(state: BucketState, cost: int, now: float, rate: float, capacity: int) -> tuple[bool, BucketState]:
    \"\"\"Legacy 5-arg signature must stay compatible for callers without optional flags.\"\"\"
    elapsed = max(0.0, now - state.last_ts)
    refilled = min(float(capacity), state.tokens + elapsed * rate)
    if refilled < cost:
        return False, replace(state, tokens=refilled, last_ts=now)
    return True, replace(state, tokens=refilled - cost, last_ts=now)
""",
        base_tests="""
from src.bucket_guard import BucketState, consume_tokens

def test_legacy_consume_and_refill():
    s0 = BucketState(tokens=2.0, last_ts=0.0)
    ok, s1 = consume_tokens(s0, 3, now=2.0, rate=1.0, capacity=5)
    assert ok is True
    assert s1.tokens == 1.0
    ok2, s2 = consume_tokens(s1, 3, now=2.0, rate=1.0, capacity=5)
    assert ok2 is False
    assert s2.tokens == 1.0
""",
        clean_src="""
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class BucketState:
    tokens: float
    last_ts: float
    cooldown_until: float = 0.0

def trigger_cooldown(state: BucketState, seconds: float, now: float | None = None) -> BucketState:
    base_ts = state.last_ts if now is None else now
    return replace(state, cooldown_until=max(state.cooldown_until, base_ts + seconds))

def consume_tokens(
    state: BucketState, cost: int, now: float, rate: float, capacity: int, burst_cap: int | None = None
) -> tuple[bool, BucketState]:
    elapsed = max(0.0, now - state.last_ts)
    cap = float(min(capacity, burst_cap)) if burst_cap is not None else float(capacity)
    refilled = min(cap, state.tokens + elapsed * rate)
    if now < state.cooldown_until:
        return False, replace(state, tokens=refilled, last_ts=now)
    if refilled < cost:
        return False, replace(state, tokens=refilled, last_ts=now)
    return True, replace(state, tokens=refilled - cost, last_ts=now)
""",
        clean_tests="""
from src.bucket_guard import BucketState, consume_tokens, trigger_cooldown

def test_legacy_consume_and_refill():
    s0 = BucketState(tokens=2.0, last_ts=0.0)
    ok, s1 = consume_tokens(s0, 3, now=2.0, rate=1.0, capacity=5)
    assert ok is True
    assert s1.tokens == 1.0
    ok2, s2 = consume_tokens(s1, 3, now=2.0, rate=1.0, capacity=5)
    assert ok2 is False
    assert s2.tokens == 1.0

def test_burst_cap_limits_refill():
    s0 = BucketState(tokens=1.0, last_ts=0.0)
    ok, s1 = consume_tokens(s0, 4, now=10.0, rate=2.0, capacity=10, burst_cap=3)
    assert ok is False
    assert s1.tokens == 3.0

def test_cooldown_blocks_until_expiry():
    s0 = trigger_cooldown(BucketState(tokens=5.0, last_ts=0.0), seconds=5.0, now=1.0)
    ok, _ = consume_tokens(s0, 1, now=4.0, rate=1.0, capacity=5)
    assert ok is False
    ok_after, _ = consume_tokens(s0, 1, now=6.0, rate=1.0, capacity=5)
    assert ok_after is True
    s_default_now = trigger_cooldown(BucketState(tokens=5.0, last_ts=100.0), 5.0)
    ok_def, _ = consume_tokens(s_default_now, 1, now=102.0, rate=1.0, capacity=5)
    assert ok_def is False
""",
        false_ci_src="""
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class BucketState:
    tokens: float
    last_ts: float
    cooldown_until: float = 0.0

def trigger_cooldown(state: BucketState, seconds: float, now: float = 0.0) -> BucketState:
    return replace(state, cooldown_until=now + seconds)

def consume_tokens(
    state: BucketState, cost: int, now: float, rate: float, capacity: int, burst_cap: int | None = None
) -> tuple[bool, BucketState]:
    elapsed = max(0.0, now - state.last_ts)
    cap = float(max(capacity, burst_cap)) if burst_cap is not None else float(capacity)
    refilled = min(cap, state.tokens + elapsed * rate)
    if now <= state.cooldown_until and state.cooldown_until > 0:
        return False, replace(state, tokens=refilled, last_ts=now)
    if refilled < cost:
        return False, replace(state, tokens=refilled, last_ts=now)
    return True, replace(state, tokens=refilled - cost, last_ts=now)
""",
        false_ci_tests="""
from src.bucket_guard import BucketState, consume_tokens, trigger_cooldown

def test_legacy_consume_and_refill():
    s0 = BucketState(tokens=2.0, last_ts=0.0)
    ok, s1 = consume_tokens(s0, 3, now=2.0, rate=1.0, capacity=5)
    assert ok is True
    assert s1.tokens == 1.0
    ok2, s2 = consume_tokens(s1, 3, now=2.0, rate=1.0, capacity=5)
    assert ok2 is False
    assert s2.tokens == 1.0

def test_burst_cap_limits_refill():
    s0 = BucketState(tokens=1.0, last_ts=0.0)
    ok, s1 = consume_tokens(s0, 4, now=10.0, rate=2.0, capacity=10, burst_cap=3)
    assert ok is False
    assert s1.tokens == 3.0

def test_cooldown_blocks_until_exact_boundary():
    s0 = trigger_cooldown(BucketState(tokens=5.0, last_ts=0.0), seconds=5.0, now=1.0)
    ok_after, _ = consume_tokens(s0, 1, now=6.0, rate=1.0, capacity=5)
    assert ok_after is True
""",
        partial_src="""
from dataclasses import dataclass, replace

@dataclass(frozen=True)
class BucketState:
    tokens: float
    last_ts: float
    cooldown_until: float = 0.0

def consume_tokens(
    state: BucketState, cost: int, now: float, rate: float, capacity: int, burst_cap: int | None = None
) -> tuple[bool, BucketState]:
    elapsed = max(0.0, now - state.last_ts)
    cap = float(min(capacity, burst_cap)) if burst_cap is not None else float(capacity)
    refilled = min(cap, state.tokens + elapsed * rate)
    if refilled < cost:
        return False, replace(state, tokens=refilled, last_ts=now)
    return True, replace(state, tokens=refilled - cost, last_ts=now)
""",
        partial_tests="""
from src.bucket_guard import BucketState, consume_tokens

def test_legacy_consume_and_refill():
    s0 = BucketState(tokens=2.0, last_ts=0.0)
    ok, s1 = consume_tokens(s0, 3, now=2.0, rate=1.0, capacity=5)
    assert ok is True
    assert s1.tokens == 1.0
    ok2, s2 = consume_tokens(s1, 3, now=2.0, rate=1.0, capacity=5)
    assert ok2 is False
    assert s2.tokens == 1.0

def test_burst_cap_limits_refill():
    s0 = BucketState(tokens=1.0, last_ts=0.0)
    ok, s1 = consume_tokens(s0, 4, now=10.0, rate=2.0, capacity=10, burst_cap=3)
    assert ok is False
    assert s1.tokens == 3.0
""",
        oracle_tests="""
from src.bucket_guard import BucketState, consume_tokens, trigger_cooldown

def test_oracle_legacy_and_burst_and_cooldown():
    s0 = BucketState(tokens=2.0, last_ts=0.0)
    ok, s1 = consume_tokens(s0, 3, now=2.0, rate=1.0, capacity=5)
    assert ok and s1.tokens == 1.0
    ok_cap, s_cap = consume_tokens(BucketState(1.0, 0.0), 4, now=10.0, rate=2.0, capacity=10, burst_cap=3)
    assert not ok_cap and s_cap.tokens == 3.0
    cool = trigger_cooldown(BucketState(5.0, 0.0), seconds=5.0, now=1.0)
    ok_during, _ = consume_tokens(cool, 1, now=4.0, rate=1.0, capacity=5)
    ok_exact, _ = consume_tokens(cool, 1, now=6.0, rate=1.0, capacity=5)
    assert not ok_during and ok_exact
""",
    ),

    # --- C02: auth_tokens (omits req_1) ---
    make_repo_task(
        task_id="C02",
        domain="auth_tokens",
        module_name="claim_guard",
        title="Add Clock Skew Leeway and Required Audience Check",
        req_1="Add optional `leeway_seconds: int = 0` to `validate_claims(claims, now, expected_aud, leeway_seconds=0)` allowing `exp` within `[now - leeway_seconds, ...]` (`now - leeway_seconds <= exp`).",
        req_2="Enforce strict string equality on `claims.get('aud') == expected_aud` when `expected_aud` is non-empty, raising `ValueError('bad_audience')` otherwise.",
        omitted_req_in_partial="req_1",
        base_src="""
def validate_claims(claims: dict, now: int, expected_aud: str = "") -> dict:
    exp = int(claims.get("exp", -1))
    if exp < now:
        raise ValueError("token_expired")
    return {"sub": claims["sub"], "exp": exp}
""",
        base_tests="""
import pytest
from src.claim_guard import validate_claims

def test_valid_and_expired_legacy():
    assert validate_claims({"sub": "u1", "exp": 100}, now=90)["sub"] == "u1"
    with pytest.raises(ValueError, match="token_expired"):
        validate_claims({"sub": "u1", "exp": 80}, now=90)
""",
        clean_src="""
def validate_claims(claims: dict, now: int, expected_aud: str = "", leeway_seconds: int = 0) -> dict:
    exp = int(claims.get("exp", -1))
    if exp < now - leeway_seconds:
        raise ValueError("token_expired")
    if expected_aud and claims.get("aud") != expected_aud:
        raise ValueError("bad_audience")
    return {"sub": claims["sub"], "exp": exp}
""",
        clean_tests="""
import pytest
from src.claim_guard import validate_claims

def test_valid_and_expired_legacy():
    assert validate_claims({"sub": "u1", "exp": 100}, now=90)["sub"] == "u1"
    with pytest.raises(ValueError, match="token_expired"):
        validate_claims({"sub": "u1", "exp": 80}, now=90)

def test_leeway_permits_recent_expiry():
    out = validate_claims({"sub": "u1", "exp": 95, "aud": "api"}, now=100, expected_aud="api", leeway_seconds=5)
    assert out["sub"] == "u1"

def test_audience_check_rejects_mismatch():
    with pytest.raises(ValueError, match="bad_audience"):
        validate_claims({"sub": "u1", "exp": 200, "aud": "other"}, now=100, expected_aud="api")
""",
        false_ci_src="""
def validate_claims(claims: dict, now: int, expected_aud: str = "", leeway_seconds: int = 0) -> dict:
    exp = int(claims.get("exp", -1))
    if exp <= now - leeway_seconds:
        raise ValueError("token_expired")
    if expected_aud and claims.get("aud") != expected_aud:
        raise ValueError("bad_audience")
    return {"sub": claims["sub"], "exp": exp}
""",
        false_ci_tests="""
import pytest
from src.claim_guard import validate_claims

def test_valid_and_expired_legacy():
    assert validate_claims({"sub": "u1", "exp": 100}, now=90)["sub"] == "u1"
    with pytest.raises(ValueError, match="token_expired"):
        validate_claims({"sub": "u1", "exp": 80}, now=90)

def test_leeway_permits_boundary_expiry():
    out = validate_claims({"sub": "u1", "exp": 95, "aud": "api"}, now=100, expected_aud="api", leeway_seconds=5)
    assert out["sub"] == "u1"
""",
        partial_src="""
def validate_claims(claims: dict, now: int, expected_aud: str = "") -> dict:
    exp = int(claims.get("exp", -1))
    if exp < now:
        raise ValueError("token_expired")
    if expected_aud and claims.get("aud") != expected_aud:
        raise ValueError("bad_audience")
    return {"sub": claims["sub"], "exp": exp}
""",
        partial_tests="""
import pytest
from src.claim_guard import validate_claims

def test_valid_and_expired_legacy():
    assert validate_claims({"sub": "u1", "exp": 100}, now=90)["sub"] == "u1"
    with pytest.raises(ValueError, match="token_expired"):
        validate_claims({"sub": "u1", "exp": 80}, now=90)

def test_audience_check_rejects_mismatch():
    with pytest.raises(ValueError, match="bad_audience"):
        validate_claims({"sub": "u1", "exp": 200, "aud": "other"}, now=100, expected_aud="api")
""",
        oracle_tests="""
import pytest
from src.claim_guard import validate_claims

def test_oracle_leeway_and_audience():
    assert validate_claims({"sub": "u1", "exp": 95, "aud": "api"}, now=100, expected_aud="api", leeway_seconds=5)["sub"] == "u1"
    with pytest.raises(ValueError, match="token_expired"):
        validate_claims({"sub": "u1", "exp": 94, "aud": "api"}, now=100, expected_aud="api", leeway_seconds=5)
    with pytest.raises(ValueError, match="bad_audience"):
        validate_claims({"sub": "u1", "exp": 200, "aud": "web"}, now=100, expected_aud="api")
""",
    ),

    # --- T00: rate_limit (omits req_2) ---
    make_repo_task(
        task_id="T00",
        domain="rate_limit",
        module_name="sliding_window",
        title="Add Per-Tenant Override and Burst Weighting to Sliding Window",
        req_1="Extend `allow_request(events, now, window, limit, overrides=None, tenant='default')` to apply per-tenant overrides from `overrides[tenant]` when present.",
        req_2="Add optional `weight: int = 1` (clamped `>= 1`) appending `weight` copies of `now` when allowed so weighted request units count against the active `(now - window, now]` limit.",
        omitted_req_in_partial="req_2",
        base_src="""
def allow_request(events: list[float], now: float, window: float, limit: int) -> tuple[bool, list[float]]:
    cutoff = now - window
    active = [ts for ts in events if ts > cutoff]
    if len(active) >= limit:
        return False, active
    return True, active + [now]
""",
        base_tests="""
from src.sliding_window import allow_request

def test_legacy_sliding_window():
    ok, ev = allow_request([1.0, 2.0], now=5.0, window=10.0, limit=3)
    assert ok is True and len(ev) == 3
    ok2, _ = allow_request(ev, now=6.0, window=10.0, limit=3)
    assert ok2 is False
""",
        clean_src="""
def allow_request(
    events: list[float],
    now: float,
    window: float,
    limit: int,
    overrides: dict[str, int] | None = None,
    tenant: str = "default",
    weight: int = 1,
) -> tuple[bool, list[float]]:
    eff_limit = overrides.get(tenant, limit) if overrides else limit
    w = max(1, int(weight))
    cutoff = now - window
    active = [ts for ts in events if ts > cutoff]
    if len(active) + w > eff_limit:
        return False, active
    return True, active + [now] * w
""",
        clean_tests="""
from src.sliding_window import allow_request

def test_legacy_sliding_window():
    ok, ev = allow_request([1.0, 2.0], now=5.0, window=10.0, limit=3)
    assert ok is True and len(ev) == 3
    ok2, _ = allow_request(ev, now=6.0, window=10.0, limit=3)
    assert ok2 is False

def test_tenant_override():
    ok, ev = allow_request([1.0, 2.0, 3.0], now=5.0, window=10.0, limit=3, overrides={"vip": 5}, tenant="vip")
    assert ok is True and len(ev) == 4

def test_weighted_request():
    ok, _ = allow_request([1.0, 2.0], now=5.0, window=10.0, limit=3, weight=2)
    assert ok is False
""",
        false_ci_src="""
def allow_request(
    events: list[float],
    now: float,
    window: float,
    limit: int,
    overrides: dict[str, int] | None = None,
    tenant: str = "default",
    weight: int = 1,
) -> tuple[bool, list[float]]:
    eff_limit = overrides.get(tenant, limit) if overrides else limit
    cutoff = now - window
    active = [ts for ts in events if ts >= cutoff]
    if len(active) + weight >= eff_limit:
        return False, active
    return True, active + [now] * weight
""",
        false_ci_tests="""
from src.sliding_window import allow_request

def test_legacy_sliding_window():
    ok, ev = allow_request([1.0, 2.0], now=5.0, window=10.0, limit=3)
    assert ok is True and len(ev) == 3
    ok2, _ = allow_request(ev, now=6.0, window=10.0, limit=3)
    assert ok2 is False

def test_weighted_request():
    ok, ev = allow_request([1.0], now=5.0, window=10.0, limit=3, weight=2)
    assert ok is True and len(ev) == 3
""",
        partial_src="""
def allow_request(
    events: list[float],
    now: float,
    window: float,
    limit: int,
    overrides: dict[str, int] | None = None,
    tenant: str = "default",
) -> tuple[bool, list[float]]:
    eff_limit = overrides.get(tenant, limit) if overrides else limit
    cutoff = now - window
    active = [ts for ts in events if ts > cutoff]
    if len(active) >= eff_limit:
        return False, active
    return True, active + [now]
""",
        partial_tests="""
from src.sliding_window import allow_request

def test_legacy_sliding_window():
    ok, ev = allow_request([1.0, 2.0], now=5.0, window=10.0, limit=3)
    assert ok is True and len(ev) == 3
    ok2, _ = allow_request(ev, now=6.0, window=10.0, limit=3)
    assert ok2 is False

def test_tenant_override():
    ok, ev = allow_request([1.0, 2.0, 3.0], now=5.0, window=10.0, limit=3, overrides={"vip": 5}, tenant="vip")
    assert ok is True and len(ev) == 4
""",
        oracle_tests="""
from src.sliding_window import allow_request

def test_oracle_override_and_weight():
    ok_vip, _ = allow_request([1.0, 2.0, 3.0], now=5.0, window=10.0, limit=3, overrides={"vip": 5}, tenant="vip")
    assert ok_vip is True
    ok_w, ev_w = allow_request([1.0], now=5.0, window=10.0, limit=3, weight=2)
    assert ok_w is True and len(ev_w) == 3
    ok_over, _ = allow_request([1.0, 2.0], now=5.0, window=10.0, limit=3, weight=2)
    assert ok_over is False
""",
    ),

    # --- T12: rate_limit (omits req_2) ---
    make_repo_task(
        task_id="T12",
        domain="rate_limit",
        module_name="quota_pool",
        title="Add Concurrency Lease Release and Shared Pool Fallback",
        req_1="Add `release_lease(leases, lease_id)` to remove an active lease and return the updated set of active leases cleanly (no error if absent).",
        req_2="Extend `acquire_lease(leases, limit, lease_id, shared_reserve=0)` to borrow up to `shared_reserve` slots beyond `limit` only when `limit` is exhausted.",
        omitted_req_in_partial="req_2",
        base_src="""
def acquire_lease(leases: set[str], limit: int, lease_id: str) -> tuple[bool, set[str]]:
    if lease_id in leases:
        return True, set(leases)
    if len(leases) >= limit:
        return False, set(leases)
    return True, set(leases) | {lease_id}
""",
        base_tests="""
from src.quota_pool import acquire_lease

def test_legacy_lease_limit():
    ok, s = acquire_lease({"a"}, 2, "b")
    assert ok is True and len(s) == 2
    ok2, _ = acquire_lease(s, 2, "c")
    assert ok2 is False
""",
        clean_src="""
def release_lease(leases: set[str], lease_id: str) -> set[str]:
    return {x for x in leases if x != lease_id}

def acquire_lease(leases: set[str], limit: int, lease_id: str, shared_reserve: int = 0) -> tuple[bool, set[str]]:
    if lease_id in leases:
        return True, set(leases)
    if len(leases) >= limit + max(0, shared_reserve):
        return False, set(leases)
    return True, set(leases) | {lease_id}
""",
        clean_tests="""
from src.quota_pool import acquire_lease, release_lease

def test_legacy_lease_limit():
    ok, s = acquire_lease({"a"}, 2, "b")
    assert ok is True and len(s) == 2
    ok2, _ = acquire_lease(s, 2, "c")
    assert ok2 is False

def test_release_lease_idempotent():
    s = release_lease({"a", "b"}, "a")
    assert s == {"b"}
    assert release_lease(s, "missing") == {"b"}

def test_shared_reserve_allows_overflow():
    ok, s = acquire_lease({"a", "b"}, 2, "c", shared_reserve=1)
    assert ok is True and "c" in s
""",
        false_ci_src="""
def release_lease(leases: set[str], lease_id: str) -> set[str]:
    out = set(leases)
    out.remove(lease_id)
    return out

def acquire_lease(leases: set[str], limit: int, lease_id: str, shared_reserve: int = 0) -> tuple[bool, set[str]]:
    if lease_id in leases:
        return True, set(leases)
    if len(leases) >= limit + shared_reserve:
        return False, set(leases)
    return True, set(leases) | {lease_id}
""",
        false_ci_tests="""
from src.quota_pool import acquire_lease, release_lease

def test_legacy_lease_limit():
    ok, s = acquire_lease({"a"}, 2, "b")
    assert ok is True and len(s) == 2
    ok2, _ = acquire_lease(s, 2, "c")
    assert ok2 is False

def test_release_lease_idempotent():
    assert release_lease({"a"}, "missing") == {"a"}
""",
        partial_src="""
def release_lease(leases: set[str], lease_id: str) -> set[str]:
    return {x for x in leases if x != lease_id}

def acquire_lease(leases: set[str], limit: int, lease_id: str) -> tuple[bool, set[str]]:
    if lease_id in leases:
        return True, set(leases)
    if len(leases) >= limit:
        return False, set(leases)
    return True, set(leases) | {lease_id}
""",
        partial_tests="""
from src.quota_pool import acquire_lease, release_lease

def test_legacy_lease_limit():
    ok, s = acquire_lease({"a"}, 2, "b")
    assert ok is True and len(s) == 2
    ok2, _ = acquire_lease(s, 2, "c")
    assert ok2 is False

def test_release_lease_idempotent():
    assert release_lease({"a", "b"}, "a") == {"b"}
    assert release_lease({"b"}, "missing") == {"b"}
""",
        oracle_tests="""
from src.quota_pool import acquire_lease, release_lease

def test_oracle_release_and_reserve():
    assert release_lease({"a"}, "x") == {"a"}
    ok, s = acquire_lease({"a", "b"}, 2, "c", shared_reserve=1)
    assert ok is True and len(s) == 3
    ok_full, _ = acquire_lease(s, 2, "d", shared_reserve=1)
    assert ok_full is False
""",
    ),

    # --- T24: rate_limit (omits req_1) ---
    make_repo_task(
        task_id="T24",
        domain="rate_limit",
        module_name="retry_after",
        title="Compute Retry-After Header and Jitter Ceiling",
        req_1="Add `retry_after_seconds(tokens_needed, refill_rate, min_seconds=1)` returning `max(min_seconds, math.ceil(tokens_needed / refill_rate))` when `tokens_needed > 0` else `0`.",
        req_2="Add `cap_backoff_delay(delay: float, max_delay: float = 30.0) -> float` clamping negative values to `0.0` and upper values to `max_delay`.",
        omitted_req_in_partial="req_1",
        base_src="""
import math

def compute_wait_ratio(tokens_needed: float, capacity: float) -> float:
    if capacity <= 0:
        return 1.0
    return max(0.0, min(1.0, tokens_needed / capacity))
""",
        base_tests="""
from src.retry_after import compute_wait_ratio

def test_legacy_wait_ratio():
    assert compute_wait_ratio(5.0, 10.0) == 0.5
    assert compute_wait_ratio(20.0, 10.0) == 1.0
""",
        clean_src="""
import math

def compute_wait_ratio(tokens_needed: float, capacity: float) -> float:
    if capacity <= 0:
        return 1.0
    return max(0.0, min(1.0, tokens_needed / capacity))

def retry_after_seconds(tokens_needed: float, refill_rate: float, min_seconds: int = 1) -> int:
    if tokens_needed <= 0:
        return 0
    return max(min_seconds, math.ceil(tokens_needed / refill_rate))

def cap_backoff_delay(delay: float, max_delay: float = 30.0) -> float:
    return max(0.0, min(float(max_delay), float(delay)))
""",
        clean_tests="""
from src.retry_after import cap_backoff_delay, compute_wait_ratio, retry_after_seconds

def test_legacy_wait_ratio():
    assert compute_wait_ratio(5.0, 10.0) == 0.5
    assert compute_wait_ratio(20.0, 10.0) == 1.0

def test_retry_after_seconds():
    assert retry_after_seconds(0, 2.0) == 0
    assert retry_after_seconds(2.1, 2.0) == 2

def test_cap_backoff_delay():
    assert cap_backoff_delay(-3.0) == 0.0
    assert cap_backoff_delay(45.0, max_delay=30.0) == 30.0
""",
        false_ci_src="""
import math

def compute_wait_ratio(tokens_needed: float, capacity: float) -> float:
    if capacity <= 0:
        return 1.0
    return max(0.0, min(1.0, tokens_needed / capacity))

def retry_after_seconds(tokens_needed: float, refill_rate: float, min_seconds: int = 1) -> int:
    if tokens_needed <= 0:
        return 0
    return max(min_seconds, math.floor(tokens_needed / refill_rate))

def cap_backoff_delay(delay: float, max_delay: float = 30.0) -> float:
    return min(float(max_delay), float(delay))
""",
        false_ci_tests="""
from src.retry_after import cap_backoff_delay, compute_wait_ratio, retry_after_seconds

def test_legacy_wait_ratio():
    assert compute_wait_ratio(5.0, 10.0) == 0.5
    assert compute_wait_ratio(20.0, 10.0) == 1.0

def test_retry_after_seconds():
    assert retry_after_seconds(2.1, 2.0) == 2

def test_cap_backoff_delay():
    assert cap_backoff_delay(-3.0) == 0.0
""",
        partial_src="""
def compute_wait_ratio(tokens_needed: float, capacity: float) -> float:
    if capacity <= 0:
        return 1.0
    return max(0.0, min(1.0, tokens_needed / capacity))

def cap_backoff_delay(delay: float, max_delay: float = 30.0) -> float:
    return max(0.0, min(float(max_delay), float(delay)))
""",
        partial_tests="""
from src.retry_after import cap_backoff_delay, compute_wait_ratio

def test_legacy_wait_ratio():
    assert compute_wait_ratio(5.0, 10.0) == 0.5
    assert compute_wait_ratio(20.0, 10.0) == 1.0

def test_cap_backoff_delay():
    assert cap_backoff_delay(-3.0) == 0.0
    assert cap_backoff_delay(45.0, max_delay=30.0) == 30.0
""",
        oracle_tests="""
from src.retry_after import cap_backoff_delay, compute_wait_ratio, retry_after_seconds

def test_oracle_retry_and_cap():
    assert compute_wait_ratio(5.0, 10.0) == 0.5
    assert retry_after_seconds(2.1, 2.0) == 2
    assert retry_after_seconds(0, 2.0) == 0
    assert cap_backoff_delay(-1.0) == 0.0 and cap_backoff_delay(50.0, 30.0) == 30.0
""",
    ),

    # --- T01: billing (omits req_2) ---
    make_repo_task(
        task_id="T01",
        domain="billing",
        module_name="prorate",
        title="Add Mid-Cycle Upgrade Proration and Zero-Day Guard",
        req_1="Add `prorate_cents(monthly_cents, active_days, cycle_days)` returning integer rounded `(monthly_cents * active_days) // cycle_days` with `0` if `active_days <= 0`.",
        req_2="Add `upgrade_delta_cents(old_monthly, new_monthly, remaining_days, cycle_days)` returning net positive upgrade charge floored at `0` for downgrades.",
        omitted_req_in_partial="req_2",
        base_src="""
def full_cycle_total(items_cents: list[int], tax_bps: int = 0) -> int:
    sub = sum(items_cents)
    return sub + (sub * tax_bps) // 10_000
""",
        base_tests="""
from src.prorate import full_cycle_total

def test_legacy_full_cycle():
    assert full_cycle_total([1000, 2000], tax_bps=500) == 3150
""",
        clean_src="""
def full_cycle_total(items_cents: list[int], tax_bps: int = 0) -> int:
    sub = sum(items_cents)
    return sub + (sub * tax_bps) // 10_000

def prorate_cents(monthly_cents: int, active_days: int, cycle_days: int) -> int:
    if active_days <= 0 or cycle_days <= 0:
        return 0
    return (monthly_cents * active_days) // cycle_days

def upgrade_delta_cents(old_monthly: int, new_monthly: int, remaining_days: int, cycle_days: int) -> int:
    if new_monthly <= old_monthly:
        return 0
    return prorate_cents(new_monthly - old_monthly, remaining_days, cycle_days)
""",
        clean_tests="""
from src.prorate import full_cycle_total, prorate_cents, upgrade_delta_cents

def test_legacy_full_cycle():
    assert full_cycle_total([1000, 2000], tax_bps=500) == 3150

def test_prorate_and_zero_day():
    assert prorate_cents(3000, 10, 30) == 1000
    assert prorate_cents(3000, 0, 30) == 0

def test_upgrade_delta_floors_downgrade():
    assert upgrade_delta_cents(1000, 3000, 15, 30) == 1000
    assert upgrade_delta_cents(3000, 1000, 15, 30) == 0
""",
        false_ci_src="""
def full_cycle_total(items_cents: list[int], tax_bps: int = 0) -> int:
    sub = sum(items_cents)
    return sub + (sub * tax_bps) // 10_000

def prorate_cents(monthly_cents: int, active_days: int, cycle_days: int) -> int:
    if active_days <= 0:
        return 0
    return (monthly_cents * active_days) // cycle_days

def upgrade_delta_cents(old_monthly: int, new_monthly: int, remaining_days: int, cycle_days: int) -> int:
    return prorate_cents(new_monthly - old_monthly, remaining_days, cycle_days)
""",
        false_ci_tests="""
from src.prorate import full_cycle_total, prorate_cents, upgrade_delta_cents

def test_legacy_full_cycle():
    assert full_cycle_total([1000, 2000], tax_bps=500) == 3150

def test_upgrade_delta_floors_downgrade():
    assert upgrade_delta_cents(3000, 1000, 15, 30) == 0
""",
        partial_src="""
def full_cycle_total(items_cents: list[int], tax_bps: int = 0) -> int:
    sub = sum(items_cents)
    return sub + (sub * tax_bps) // 10_000

def prorate_cents(monthly_cents: int, active_days: int, cycle_days: int) -> int:
    if active_days <= 0 or cycle_days <= 0:
        return 0
    return (monthly_cents * active_days) // cycle_days
""",
        partial_tests="""
from src.prorate import full_cycle_total, prorate_cents

def test_legacy_full_cycle():
    assert full_cycle_total([1000, 2000], tax_bps=500) == 3150

def test_prorate_and_zero_day():
    assert prorate_cents(3000, 10, 30) == 1000
    assert prorate_cents(3000, 0, 30) == 0
""",
        oracle_tests="""
from src.prorate import full_cycle_total, prorate_cents, upgrade_delta_cents

def test_oracle_prorate_and_upgrade():
    assert full_cycle_total([1000, 2000], 500) == 3150
    assert prorate_cents(3000, 10, 30) == 1000 and prorate_cents(3000, -1, 30) == 0
    assert upgrade_delta_cents(1000, 3000, 15, 30) == 1000
    assert upgrade_delta_cents(3000, 1000, 15, 30) == 0
""",
    ),

    # --- T13: billing (omits req_2) ---
    make_repo_task(
        task_id="T13",
        domain="billing",
        module_name="credit_memo",
        title="Reverse Pro-Rata Tax and Clamp Refunds to Paid Total",
        req_1="Add `apply_credit_memo(paid_cents, credit_cents)` clamping negative results to `0` so cumulative credit cannot exceed `paid_cents`.",
        req_2="Add `credit_with_tax_cents(net_credit_cents, tax_bps)` computing `net_credit_cents + (net_credit_cents * tax_bps) // 10_000`.",
        omitted_req_in_partial="req_2",
        base_src="""
def invoice_balance(subtotal: int, discounts: list[int]) -> int:
    return max(0, subtotal - sum(discounts))
""",
        base_tests="""
from src.credit_memo import invoice_balance

def test_legacy_balance():
    assert invoice_balance(5000, [500, 300]) == 4200
""",
        clean_src="""
def invoice_balance(subtotal: int, discounts: list[int]) -> int:
    return max(0, subtotal - sum(discounts))

def apply_credit_memo(paid_cents: int, credit_cents: int) -> int:
    return max(0, paid_cents - max(0, credit_cents))

def credit_with_tax_cents(net_credit_cents: int, tax_bps: int) -> int:
    if net_credit_cents <= 0:
        return 0
    return net_credit_cents + (net_credit_cents * tax_bps) // 10_000
""",
        clean_tests="""
from src.credit_memo import apply_credit_memo, credit_with_tax_cents, invoice_balance

def test_legacy_balance():
    assert invoice_balance(5000, [500, 300]) == 4200

def test_apply_credit_clamped():
    assert apply_credit_memo(1000, 1500) == 0
    assert apply_credit_memo(1000, 250) == 750

def test_credit_with_tax():
    assert credit_with_tax_cents(2000, 825) == 2165
""",
        false_ci_src="""
def invoice_balance(subtotal: int, discounts: list[int]) -> int:
    return max(0, subtotal - sum(discounts))

def apply_credit_memo(paid_cents: int, credit_cents: int) -> int:
    return paid_cents - credit_cents

def credit_with_tax_cents(net_credit_cents: int, tax_bps: int) -> int:
    return net_credit_cents + (net_credit_cents * tax_bps) // 100
""",
        false_ci_tests="""
from src.credit_memo import apply_credit_memo, credit_with_tax_cents, invoice_balance

def test_legacy_balance():
    assert invoice_balance(5000, [500, 300]) == 4200

def test_apply_credit_clamped():
    assert apply_credit_memo(1000, 1500) == 0

def test_credit_with_tax():
    assert credit_with_tax_cents(2000, 825) == 2165
""",
        partial_src="""
def invoice_balance(subtotal: int, discounts: list[int]) -> int:
    return max(0, subtotal - sum(discounts))

def apply_credit_memo(paid_cents: int, credit_cents: int) -> int:
    return max(0, paid_cents - max(0, credit_cents))
""",
        partial_tests="""
from src.credit_memo import apply_credit_memo, invoice_balance

def test_legacy_balance():
    assert invoice_balance(5000, [500, 300]) == 4200

def test_apply_credit_clamped():
    assert apply_credit_memo(1000, 1500) == 0
    assert apply_credit_memo(1000, 250) == 750
""",
        oracle_tests="""
from src.credit_memo import apply_credit_memo, credit_with_tax_cents, invoice_balance

def test_oracle_credit_and_tax():
    assert invoice_balance(5000, [500]) == 4500
    assert apply_credit_memo(1000, 1500) == 0
    assert credit_with_tax_cents(2000, 825) == 2165
""",
    ),

    # --- T25: billing (omits req_1) ---
    make_repo_task(
        task_id="T25",
        domain="billing",
        module_name="ledger_round",
        title="Split Payouts Conserving Total Cents Without Penny Drift",
        req_1="Add `split_cents_exact(total_cents, weights)` returning integer shares summing strictly to `total_cents` by distributing remainder pennies one-by-one from the highest fractional part (ties broken by lowest index).",
        req_2="Add `reconcile_ledger(debits, credits)` returning `(balanced: bool, net_delta: int)` where `balanced` holds iff `sum(debits) == sum(credits)`.",
        omitted_req_in_partial="req_1",
        base_src="""
def sum_cents(entries: list[int]) -> int:
    return sum(int(x) for x in entries)
""",
        base_tests="""
from src.ledger_round import sum_cents

def test_legacy_sum():
    assert sum_cents([100, 250, -50]) == 300
""",
        clean_src="""
def sum_cents(entries: list[int]) -> int:
    return sum(int(x) for x in entries)

def split_cents_exact(total_cents: int, weights: list[int]) -> list[int]:
    total_w = sum(weights)
    if total_w <= 0 or not weights:
        return [0] * len(weights)
    exact = [(total_cents * w) / total_w for w in weights]
    floors = [int(x) for x in exact]
    rem = total_cents - sum(floors)
    order = sorted(range(len(weights)), key=lambda i: (-(exact[i] - floors[i]), i))
    for idx in order[:rem]:
        floors[idx] += 1
    return floors

def reconcile_ledger(debits: list[int], credits: list[int]) -> tuple[bool, int]:
    delta = sum(debits) - sum(credits)
    return delta == 0, delta
""",
        clean_tests="""
from src.ledger_round import reconcile_ledger, split_cents_exact, sum_cents

def test_legacy_sum():
    assert sum_cents([100, 250, -50]) == 300

def test_split_conserves_cents():
    shares = split_cents_exact(100, [1, 1, 1])
    assert shares == [34, 33, 33] and sum(shares) == 100

def test_reconcile_ledger():
    assert reconcile_ledger([100, 50], [150]) == (True, 0)
    assert reconcile_ledger([100], [90]) == (False, 10)
""",
        false_ci_src="""
def sum_cents(entries: list[int]) -> int:
    return sum(int(x) for x in entries)

def split_cents_exact(total_cents: int, weights: list[int]) -> list[int]:
    total_w = sum(weights)
    return [(total_cents * w) // total_w for w in weights]

def reconcile_ledger(debits: list[int], credits: list[int]) -> tuple[bool, int]:
    delta = sum(debits) - sum(credits)
    return delta == 0, delta
""",
        false_ci_tests="""
from src.ledger_round import reconcile_ledger, split_cents_exact, sum_cents

def test_legacy_sum():
    assert sum_cents([100, 250, -50]) == 300

def test_split_conserves_cents():
    assert sum(split_cents_exact(100, [1, 1, 1])) == 100
""",
        partial_src="""
def sum_cents(entries: list[int]) -> int:
    return sum(int(x) for x in entries)

def reconcile_ledger(debits: list[int], credits: list[int]) -> tuple[bool, int]:
    delta = sum(debits) - sum(credits)
    return delta == 0, delta
""",
        partial_tests="""
from src.ledger_round import reconcile_ledger, sum_cents

def test_legacy_sum():
    assert sum_cents([100, 250, -50]) == 300

def test_reconcile_ledger():
    assert reconcile_ledger([100, 50], [150]) == (True, 0)
    assert reconcile_ledger([100], [90]) == (False, 10)
""",
        oracle_tests="""
from src.ledger_round import reconcile_ledger, split_cents_exact, sum_cents

def test_oracle_split_and_reconcile():
    assert sum_cents([10, 20]) == 30
    assert split_cents_exact(100, [1, 1, 1]) == [34, 33, 33]
    assert reconcile_ledger([50, 50], [100]) == (True, 0)
""",
    ),

    # --- T02: auth_tokens (omits req_2) ---
    make_repo_task(
        task_id="T02",
        domain="auth_tokens",
        module_name="keyring_rotator",
        title="Support Secondary Key Rotation Lookup and Retired Key Rejection",
        req_1="Extend `select_signing_key(keyring, kid)` to fall back to `keyring['previous']` if `kid` matches previous active key, returning the key dict.",
        req_2="Reject keys whose `status == 'retired'` inside `select_signing_key(...)` by raising `PermissionError('key_retired')`.",
        omitted_req_in_partial="req_2",
        base_src="""
def select_signing_key(keyring: dict, kid: str) -> dict:
    cur = keyring.get("current")
    if cur and cur.get("kid") == kid:
        return cur
    raise KeyError(kid)
""",
        base_tests="""
import pytest
from src.keyring_rotator import select_signing_key

def test_legacy_current_key():
    kr = {"current": {"kid": "k2", "secret": "s2"}}
    assert select_signing_key(kr, "k2")["secret"] == "s2"
    with pytest.raises(KeyError):
        select_signing_key(kr, "unknown")
""",
        clean_src="""
def select_signing_key(keyring: dict, kid: str) -> dict:
    for slot in ("current", "previous"):
        cand = keyring.get(slot)
        if cand and cand.get("kid") == kid:
            if cand.get("status") == "retired":
                raise PermissionError("key_retired")
            return cand
    raise KeyError(kid)
""",
        clean_tests="""
import pytest
from src.keyring_rotator import select_signing_key

def test_legacy_current_key():
    kr = {"current": {"kid": "k2", "secret": "s2"}}
    assert select_signing_key(kr, "k2")["secret"] == "s2"
    with pytest.raises(KeyError):
        select_signing_key(kr, "unknown")

def test_previous_key_fallback():
    kr = {"current": {"kid": "k2", "secret": "s2"}, "previous": {"kid": "k1", "secret": "s1", "status": "grace"}}
    assert select_signing_key(kr, "k1")["secret"] == "s1"

def test_retired_key_rejected():
    kr = {"current": {"kid": "k2", "secret": "s2"}, "previous": {"kid": "k1", "secret": "s1", "status": "retired"}}
    with pytest.raises(PermissionError, match="key_retired"):
        select_signing_key(kr, "k1")
""",
        false_ci_src="""
def select_signing_key(keyring: dict, kid: str) -> dict:
    for slot in ("current", "previous"):
        cand = keyring.get(slot)
        if cand and cand.get("kid") == kid:
            return cand
    raise KeyError(kid)
""",
        false_ci_tests="""
import pytest
from src.keyring_rotator import select_signing_key

def test_legacy_current_key():
    kr = {"current": {"kid": "k2", "secret": "s2"}}
    assert select_signing_key(kr, "k2")["secret"] == "s2"

def test_retired_key_rejected():
    kr = {"previous": {"kid": "k1", "status": "retired"}}
    with pytest.raises(PermissionError):
        select_signing_key(kr, "k1")
""",
        partial_src="""
def select_signing_key(keyring: dict, kid: str) -> dict:
    for slot in ("current", "previous"):
        cand = keyring.get(slot)
        if cand and cand.get("kid") == kid:
            return cand
    raise KeyError(kid)
""",
        partial_tests="""
import pytest
from src.keyring_rotator import select_signing_key

def test_legacy_current_key():
    kr = {"current": {"kid": "k2", "secret": "s2"}}
    assert select_signing_key(kr, "k2")["secret"] == "s2"
    with pytest.raises(KeyError):
        select_signing_key(kr, "unknown")

def test_previous_key_fallback():
    kr = {"current": {"kid": "k2", "secret": "s2"}, "previous": {"kid": "k1", "secret": "s1", "status": "grace"}}
    assert select_signing_key(kr, "k1")["secret"] == "s1"
""",
        oracle_tests="""
import pytest
from src.keyring_rotator import select_signing_key

def test_oracle_rotation_and_retired():
    kr = {
        "current": {"kid": "k2", "secret": "s2"},
        "previous": {"kid": "k1", "secret": "s1", "status": "retired"},
    }
    assert select_signing_key(kr, "k2")["secret"] == "s2"
    with pytest.raises(PermissionError, match="key_retired"):
        select_signing_key(kr, "k1")
""",
    ),

    # --- T14: auth_tokens (omits req_2) ---
    make_repo_task(
        task_id="T14",
        domain="auth_tokens",
        module_name="scope_intersect",
        title="Intersect Requested Token Scopes with Principal Grant Cap",
        req_1="Add `narrow_scopes(requested, granted)` returning sorted list of scopes present in both collections without duplicates.",
        req_2="Add `has_all_required_scopes(token_scopes, required)` returning `True` iff every scope in `required` is present in `token_scopes`.",
        omitted_req_in_partial="req_2",
        base_src="""
def parse_scope_header(raw: str) -> list[str]:
    return [tok for tok in raw.strip().split() if tok]
""",
        base_tests="""
from src.scope_intersect import parse_scope_header

def test_legacy_parse_scope():
    assert parse_scope_header(" read:orders  write:refunds ") == ["read:orders", "write:refunds"]
""",
        clean_src="""
def parse_scope_header(raw: str) -> list[str]:
    return [tok for tok in raw.strip().split() if tok]

def narrow_scopes(requested: list[str] | set[str], granted: list[str] | set[str]) -> list[str]:
    g = set(granted)
    return sorted({s for s in requested if s in g})

def has_all_required_scopes(token_scopes: list[str] | set[str], required: list[str] | set[str]) -> bool:
    return set(required).issubset(set(token_scopes))
""",
        clean_tests="""
from src.scope_intersect import has_all_required_scopes, narrow_scopes, parse_scope_header

def test_legacy_parse_scope():
    assert parse_scope_header(" read:orders  write:refunds ") == ["read:orders", "write:refunds"]

def test_narrow_scopes():
    assert narrow_scopes(["b", "a", "a", "c"], ["a", "b"]) == ["a", "b"]

def test_required_scopes():
    assert has_all_required_scopes(["a", "b", "c"], ["a", "c"]) is True
    assert has_all_required_scopes(["a"], ["a", "b"]) is False
""",
        false_ci_src="""
def parse_scope_header(raw: str) -> list[str]:
    return [tok for tok in raw.strip().split() if tok]

def narrow_scopes(requested: list[str] | set[str], granted: list[str] | set[str]) -> list[str]:
    return sorted(set(requested) | set(granted))

def has_all_required_scopes(token_scopes: list[str] | set[str], required: list[str] | set[str]) -> bool:
    return bool(set(token_scopes) & set(required))
""",
        false_ci_tests="""
from src.scope_intersect import has_all_required_scopes, narrow_scopes, parse_scope_header

def test_legacy_parse_scope():
    assert parse_scope_header(" read:orders  write:refunds ") == ["read:orders", "write:refunds"]

def test_narrow_scopes():
    assert narrow_scopes(["b", "c"], ["a", "b"]) == ["b"]
""",
        partial_src="""
def parse_scope_header(raw: str) -> list[str]:
    return [tok for tok in raw.strip().split() if tok]

def narrow_scopes(requested: list[str] | set[str], granted: list[str] | set[str]) -> list[str]:
    g = set(granted)
    return sorted({s for s in requested if s in g})
""",
        partial_tests="""
from src.scope_intersect import narrow_scopes, parse_scope_header

def test_legacy_parse_scope():
    assert parse_scope_header(" read:orders  write:refunds ") == ["read:orders", "write:refunds"]

def test_narrow_scopes():
    assert narrow_scopes(["b", "a", "a", "c"], ["a", "b"]) == ["a", "b"]
""",
        oracle_tests="""
from src.scope_intersect import has_all_required_scopes, narrow_scopes, parse_scope_header

def test_oracle_scopes():
    assert parse_scope_header("x y") == ["x", "y"]
    assert narrow_scopes(["admin", "read"], ["read"]) == ["read"]
    assert has_all_required_scopes(["read"], ["read", "write"]) is False
    assert has_all_required_scopes(["read", "write"], ["read"]) is True
""",
    ),

    # --- T26: auth_tokens (omits req_1) ---
    make_repo_task(
        task_id="T26",
        domain="auth_tokens",
        module_name="nonce_replay",
        title="Guard Against Single-Use Nonce Replay Within TTL Window",
        req_1="Add `check_and_record_nonce(seen, nonce, now, ttl)` returning `(accepted: bool, updated_seen: dict)` rejecting replays while `now < recorded_expiry`.",
        req_2="Prune all expired nonces (`expiry <= now`) cleanly from `updated_seen` on each call so the store stays bounded.",
        omitted_req_in_partial="req_1",
        base_src="""
def make_nonce_key(issuer: str, jti: str) -> str:
    return f"{issuer}:{jti}"
""",
        base_tests="""
from src.nonce_replay import make_nonce_key

def test_legacy_nonce_key():
    assert make_nonce_key("alpha", "123") == "alpha:123"
""",
        clean_src="""
def make_nonce_key(issuer: str, jti: str) -> str:
    return f"{issuer}:{jti}"

def prune_expired_nonces(seen: dict[str, float], now: float) -> dict[str, float]:
    return {k: exp for k, exp in seen.items() if exp > now}

def check_and_record_nonce(
    seen: dict[str, float], nonce: str, now: float, ttl: float
) -> tuple[bool, dict[str, float]]:
    active = prune_expired_nonces(seen, now)
    if nonce in active:
        return False, active
    active[nonce] = now + ttl
    return True, active
""",
        clean_tests="""
from src.nonce_replay import check_and_record_nonce, make_nonce_key, prune_expired_nonces

def test_legacy_nonce_key():
    assert make_nonce_key("alpha", "123") == "alpha:123"

def test_replay_rejected_until_expiry():
    ok1, s1 = check_and_record_nonce({}, "n1", now=10.0, ttl=5.0)
    ok2, _ = check_and_record_nonce(s1, "n1", now=14.0, ttl=5.0)
    assert ok1 is True and ok2 is False

def test_prune_expired():
    assert prune_expired_nonces({"old": 5.0, "fresh": 20.0}, now=10.0) == {"fresh": 20.0}
""",
        false_ci_src="""
def make_nonce_key(issuer: str, jti: str) -> str:
    return f"{issuer}:{jti}"

def prune_expired_nonces(seen: dict[str, float], now: float) -> dict[str, float]:
    return {k: exp for k, exp in seen.items() if exp >= now}

def check_and_record_nonce(
    seen: dict[str, float], nonce: str, now: float, ttl: float
) -> tuple[bool, dict[str, float]]:
    return True, {**seen, nonce: now + ttl}
""",
        false_ci_tests="""
from src.nonce_replay import check_and_record_nonce, make_nonce_key

def test_legacy_nonce_key():
    assert make_nonce_key("alpha", "123") == "alpha:123"

def test_replay_rejected():
    _, s1 = check_and_record_nonce({}, "n1", now=10.0, ttl=5.0)
    ok2, _ = check_and_record_nonce(s1, "n1", now=12.0, ttl=5.0)
    assert ok2 is False
""",
        partial_src="""
def make_nonce_key(issuer: str, jti: str) -> str:
    return f"{issuer}:{jti}"

def prune_expired_nonces(seen: dict[str, float], now: float) -> dict[str, float]:
    return {k: exp for k, exp in seen.items() if exp > now}
""",
        partial_tests="""
from src.nonce_replay import make_nonce_key, prune_expired_nonces

def test_legacy_nonce_key():
    assert make_nonce_key("alpha", "123") == "alpha:123"

def test_prune_expired():
    assert prune_expired_nonces({"old": 5.0, "fresh": 20.0}, now=10.0) == {"fresh": 20.0}
""",
        oracle_tests="""
from src.nonce_replay import check_and_record_nonce, make_nonce_key, prune_expired_nonces

def test_oracle_nonce_and_prune():
    assert make_nonce_key("a", "b") == "a:b"
    assert prune_expired_nonces({"old": 10.0, "ok": 11.0}, now=10.0) == {"ok": 11.0}
    ok1, s1 = check_and_record_nonce({"old": 5.0}, "n1", now=10.0, ttl=5.0)
    ok2, _ = check_and_record_nonce(s1, "n1", now=12.0, ttl=5.0)
    ok3, _ = check_and_record_nonce(s1, "n1", now=15.0, ttl=5.0)
    assert ok1 and (not ok2) and ok3 and ("old" not in s1)
""",
    ),
]
