"""Tasks for rbac, scheduling, and semver domains (C03, T06, T07, T08, T18, T19, T20, T30, T31, T32)."""

from __future__ import annotations

from .schema import TaskSpec, make_repo_task

TASKS_PART3: list[TaskSpec] = [
    # --- C03: rbac (omits req_1) ---
    make_repo_task(
        task_id="C03",
        domain="rbac",
        module_name="deny_policy",
        title="Enforce Explicit Deny Precedence and Wildcard Action Matching",
        req_1="Extend `is_allowed(allow_rules, action, resource, deny_rules=())` so explicit `deny_rules` always override `allow_rules` cleanly (return `False`).",
        req_2="Support trailing `*` wildcard suffix matching on rule actions/resources (e.g. `'read:*'` matches `'read:orders'`).",
        omitted_req_in_partial="req_1",
        base_src="""
def _exact_match(rule: tuple[str, str], action: str, resource: str) -> bool:
    return rule[0] == action and rule[1] == resource

def is_allowed(allow_rules: list[tuple[str, str]], action: str, resource: str) -> bool:
    return any(_exact_match(r, action, resource) for r in allow_rules)
""",
        base_tests="""
from src.deny_policy import is_allowed

def test_legacy_exact_allow():
    assert is_allowed([("read", "orders")], "read", "orders") is True
    assert is_allowed([("read", "orders")], "write", "orders") is False
""",
        clean_src="""
def _pat_match(pattern: str, value: str) -> bool:
    if pattern.endswith("*"):
        return value.startswith(pattern[:-1])
    return pattern == value

def _rule_match(rule: tuple[str, str], action: str, resource: str) -> bool:
    return _pat_match(rule[0], action) and _pat_match(rule[1], resource)

def is_allowed(
    allow_rules: list[tuple[str, str]],
    action: str,
    resource: str,
    deny_rules: list[tuple[str, str]] | tuple[tuple[str, str], ...] = (),
) -> bool:
    if any(_rule_match(d, action, resource) for d in deny_rules):
        return False
    return any(_rule_match(a, action, resource) for a in allow_rules)
""",
        clean_tests="""
from src.deny_policy import is_allowed

def test_legacy_exact_allow():
    assert is_allowed([("read", "orders")], "read", "orders") is True
    assert is_allowed([("read", "orders")], "write", "orders") is False

def test_wildcard_action_and_resource():
    assert is_allowed([("read:*", "orders/*")], "read:detail", "orders/123") is True

def test_explicit_deny_wins():
    assert is_allowed([("*", "*")], "delete:user", "users/1", deny_rules=[("delete:*", "*")]) is False
""",
        false_ci_src="""
def _pat_match(pattern: str, value: str) -> bool:
    if pattern.endswith("*"):
        return value.startswith(pattern[:-1])
    return pattern == value

def is_allowed(
    allow_rules: list[tuple[str, str]],
    action: str,
    resource: str,
    deny_rules: list[tuple[str, str]] | tuple[tuple[str, str], ...] = (),
) -> bool:
    if any(_pat_match(a[0], action) and _pat_match(a[1], resource) for a in allow_rules):
        return True
    return not any(_pat_match(d[0], action) and _pat_match(d[1], resource) for d in deny_rules)
""",
        false_ci_tests="""
from src.deny_policy import is_allowed

def test_legacy_exact_allow():
    assert is_allowed([("read", "orders")], "read", "orders") is True
    assert is_allowed([("read", "orders")], "write", "orders") is False

def test_explicit_deny_wins():
    assert is_allowed([("*", "*")], "delete:user", "users/1", deny_rules=[("delete:*", "*")]) is False
""",
        partial_src="""
def _pat_match(pattern: str, value: str) -> bool:
    if pattern.endswith("*"):
        return value.startswith(pattern[:-1])
    return pattern == value

def is_allowed(allow_rules: list[tuple[str, str]], action: str, resource: str) -> bool:
    return any(_pat_match(r[0], action) and _pat_match(r[1], resource) for r in allow_rules)
""",
        partial_tests="""
from src.deny_policy import is_allowed

def test_legacy_exact_allow():
    assert is_allowed([("read", "orders")], "read", "orders") is True
    assert is_allowed([("read", "orders")], "write", "orders") is False

def test_wildcard_action_and_resource():
    assert is_allowed([("read:*", "orders/*")], "read:detail", "orders/123") is True
""",
        oracle_tests="""
from src.deny_policy import is_allowed

def test_oracle_rbac_deny_wildcard():
    assert is_allowed([("read", "orders")], "read", "orders") is True
    assert is_allowed([("read:*", "orders/*")], "read:detail", "orders/9") is True
    assert is_allowed([("*", "*")], "delete:db", "prod/db", deny_rules=[("delete:*", "prod/*")]) is False
""",
    ),

    # --- T06: rbac (omits req_2) ---
    make_repo_task(
        task_id="T06",
        domain="rbac",
        module_name="group_inherit",
        title="Expand Transitive Role Hierarchy Safely Under Cycles",
        req_1="Add `expand_roles(direct_roles, role_graph)` traversing inherited roles via BFS/DFS without infinite loops on cycles.",
        req_2="Raise `ValueError('role_cycle_detected')` from `detect_role_cycle(role_graph)` iff the directed `role -> parent_roles` graph contains a cycle.",
        omitted_req_in_partial="req_2",
        base_src="""
def normalize_roles(roles: list[str]) -> set[str]:
    return {r.strip().lower() for r in roles if r.strip()}
""",
        base_tests="""
from src.group_inherit import normalize_roles

def test_legacy_normalize_roles():
    assert normalize_roles([" Admin ", "VIEWER"]) == {"admin", "viewer"}
""",
        clean_src="""
def normalize_roles(roles: list[str]) -> set[str]:
    return {r.strip().lower() for r in roles if r.strip()}

def expand_roles(direct_roles: list[str] | set[str], role_graph: dict[str, list[str]]) -> set[str]:
    visited: set[str] = set()
    stack = list(direct_roles)
    while stack:
        cur = stack.pop()
        if cur in visited:
            continue
        visited.add(cur)
        for nxt in role_graph.get(cur, ()):
            if nxt not in visited:
                stack.append(nxt)
    return visited

def detect_role_cycle(role_graph: dict[str, list[str]]) -> bool:
    state: dict[str, int] = {}
    def dfs(node: str) -> None:
        st = state.get(node, 0)
        if st == 1:
            raise ValueError("role_cycle_detected")
        if st == 2:
            return
        state[node] = 1
        for nxt in role_graph.get(node, ()):
            dfs(nxt)
        state[node] = 2
    for root in role_graph:
        if state.get(root, 0) == 0:
            dfs(root)
    return False
""",
        clean_tests="""
import pytest
from src.group_inherit import detect_role_cycle, expand_roles, normalize_roles

def test_legacy_normalize_roles():
    assert normalize_roles([" Admin ", "VIEWER"]) == {"admin", "viewer"}

def test_expand_roles_with_cycle():
    g = {"admin": ["editor"], "editor": ["viewer", "admin"]}
    assert expand_roles(["admin"], g) == {"admin", "editor", "viewer"}

def test_detect_role_cycle_raises():
    assert detect_role_cycle({"admin": ["viewer"], "viewer": []}) is False
    with pytest.raises(ValueError, match="role_cycle_detected"):
        detect_role_cycle({"a": ["b"], "b": ["a"]})
""",
        false_ci_src="""
def normalize_roles(roles: list[str]) -> set[str]:
    return {r.strip().lower() for r in roles if r.strip()}

def expand_roles(direct_roles: list[str] | set[str], role_graph: dict[str, list[str]]) -> set[str]:
    visited = set(direct_roles)
    for r in direct_roles:
        visited.update(role_graph.get(r, ()))
    return visited

def detect_role_cycle(role_graph: dict[str, list[str]]) -> bool:
    return False
""",
        false_ci_tests="""
import pytest
from src.group_inherit import detect_role_cycle, expand_roles, normalize_roles

def test_legacy_normalize_roles():
    assert normalize_roles([" Admin ", "VIEWER"]) == {"admin", "viewer"}

def test_detect_role_cycle_raises():
    with pytest.raises(ValueError, match="role_cycle_detected"):
        detect_role_cycle({"a": ["b"], "b": ["a"]})
""",
        partial_src="""
def normalize_roles(roles: list[str]) -> set[str]:
    return {r.strip().lower() for r in roles if r.strip()}

def expand_roles(direct_roles: list[str] | set[str], role_graph: dict[str, list[str]]) -> set[str]:
    visited: set[str] = set()
    stack = list(direct_roles)
    while stack:
        cur = stack.pop()
        if cur in visited:
            continue
        visited.add(cur)
        for nxt in role_graph.get(cur, ()):
            if nxt not in visited:
                stack.append(nxt)
    return visited
""",
        partial_tests="""
from src.group_inherit import expand_roles, normalize_roles

def test_legacy_normalize_roles():
    assert normalize_roles([" Admin ", "VIEWER"]) == {"admin", "viewer"}

def test_expand_roles_with_cycle():
    g = {"admin": ["editor"], "editor": ["viewer", "admin"]}
    assert expand_roles(["admin"], g) == {"admin", "editor", "viewer"}
""",
        oracle_tests="""
import pytest
from src.group_inherit import detect_role_cycle, expand_roles, normalize_roles

def test_oracle_rbac_inherit():
    assert normalize_roles([" A "]) == {"a"}
    assert expand_roles(["a"], {"a": ["b"], "b": ["c", "a"]}) == {"a", "b", "c"}
    assert detect_role_cycle({"a": ["b"]}) is False
    with pytest.raises(ValueError, match="role_cycle_detected"):
        detect_role_cycle({"a": ["b"], "b": ["c"], "c": ["a"]})
""",
    ),

    # --- T18: rbac (omits req_1) ---
    make_repo_task(
        task_id="T18",
        domain="rbac",
        module_name="tenant_acl",
        title="Enforce Cross-Tenant Isolation and Break-Glass Expiry",
        req_1="Add `check_tenant_access(actor_tenant, resource_tenant, break_glass=None, now=0)` returning `True` iff `actor_tenant == resource_tenant` or `break_glass` grants active temporary access (`break_glass['tenant'] == resource_tenant` and `now < break_glass['expires_at']`).",
        req_2="Add `redact_cross_tenant(records, actor_tenant)` returning only records whose `record['tenant'] == actor_tenant` cleanly without mutating inputs.",
        omitted_req_in_partial="req_1",
        base_src="""
def owns_resource(actor_id: str, owner_id: str) -> bool:
    return bool(actor_id) and actor_id == owner_id
""",
        base_tests="""
from src.tenant_acl import owns_resource

def test_legacy_owner():
    assert owns_resource("u1", "u1") is True
    assert owns_resource("u1", "u2") is False
""",
        clean_src="""
def owns_resource(actor_id: str, owner_id: str) -> bool:
    return bool(actor_id) and actor_id == owner_id

def check_tenant_access(
    actor_tenant: str,
    resource_tenant: str,
    break_glass: dict | None = None,
    now: float = 0.0,
) -> bool:
    if actor_tenant and actor_tenant == resource_tenant:
        return True
    if break_glass and break_glass.get("tenant") == resource_tenant:
        return float(now) < float(break_glass.get("expires_at", -1))
    return False

def redact_cross_tenant(records: list[dict], actor_tenant: str) -> list[dict]:
    return [dict(r) for r in records if r.get("tenant") == actor_tenant]
""",
        clean_tests="""
from src.tenant_acl import check_tenant_access, owns_resource, redact_cross_tenant

def test_legacy_owner():
    assert owns_resource("u1", "u1") is True
    assert owns_resource("u1", "u2") is False

def test_break_glass_expiry():
    bg = {"tenant": "t2", "expires_at": 100.0}
    assert check_tenant_access("t1", "t2", break_glass=bg, now=90.0) is True
    assert check_tenant_access("t1", "t2", break_glass=bg, now=100.0) is False

def test_redact_cross_tenant():
    rows = [{"id": 1, "tenant": "t1"}, {"id": 2, "tenant": "t2"}]
    assert redact_cross_tenant(rows, "t1") == [{"id": 1, "tenant": "t1"}]
""",
        false_ci_src="""
def owns_resource(actor_id: str, owner_id: str) -> bool:
    return bool(actor_id) and actor_id == owner_id

def check_tenant_access(
    actor_tenant: str,
    resource_tenant: str,
    break_glass: dict | None = None,
    now: float = 0.0,
) -> bool:
    if break_glass is not None:
        return True
    return actor_tenant == resource_tenant

def redact_cross_tenant(records: list[dict], actor_tenant: str) -> list[dict]:
    return [dict(r) for r in records if r.get("tenant") == actor_tenant]
""",
        false_ci_tests="""
from src.tenant_acl import check_tenant_access, owns_resource

def test_legacy_owner():
    assert owns_resource("u1", "u1") is True

def test_break_glass_expired_rejected():
    bg = {"tenant": "t2", "expires_at": 100.0}
    assert check_tenant_access("t1", "t2", break_glass=bg, now=150.0) is False
""",
        partial_src="""
def owns_resource(actor_id: str, owner_id: str) -> bool:
    return bool(actor_id) and actor_id == owner_id

def redact_cross_tenant(records: list[dict], actor_tenant: str) -> list[dict]:
    return [dict(r) for r in records if r.get("tenant") == actor_tenant]
""",
        partial_tests="""
from src.tenant_acl import owns_resource, redact_cross_tenant

def test_legacy_owner():
    assert owns_resource("u1", "u1") is True
    assert owns_resource("u1", "u2") is False

def test_redact_cross_tenant():
    rows = [{"id": 1, "tenant": "t1"}, {"id": 2, "tenant": "t2"}]
    assert redact_cross_tenant(rows, "t1") == [{"id": 1, "tenant": "t1"}]
""",
        oracle_tests="""
from src.tenant_acl import check_tenant_access, owns_resource, redact_cross_tenant

def test_oracle_tenant_acl():
    assert owns_resource("u1", "u1") is True
    assert check_tenant_access("t1", "t1") is True
    assert check_tenant_access("t1", "t2", {"tenant": "t2", "expires_at": 50}, now=50) is False
    assert check_tenant_access("t1", "t2", {"tenant": "t2", "expires_at": 51}, now=50) is True
    assert redact_cross_tenant([{"tenant": "a"}, {"tenant": "b"}], "a") == [{"tenant": "a"}]
""",
    ),

    # --- T30: rbac (omits req_1) ---
    make_repo_task(
        task_id="T30",
        domain="rbac",
        module_name="field_mask",
        title="Enforce Field-Level Visibility Allowlists and Mask Secrets",
        req_1="Add `project_allowed_fields(record, role, role_fields)` returning a filtered copy preserving only keys in `role_fields.get(role, set())` (plus always `'id'` if present).",
        req_2="Add `mask_secret(value, keep_last=4)` masking leading characters with `'*'` while returning `'*' * len(value)` when `len(value) <= keep_last`.",
        omitted_req_in_partial="req_1",
        base_src="""
def has_role(actor_roles: set[str], required_role: str) -> bool:
    return required_role in actor_roles
""",
        base_tests="""
from src.field_mask import has_role

def test_legacy_has_role():
    assert has_role({"auditor", "reader"}, "auditor") is True
""",
        clean_src="""
def has_role(actor_roles: set[str], required_role: str) -> bool:
    return required_role in actor_roles

def project_allowed_fields(record: dict, role: str, role_fields: dict[str, set[str]]) -> dict:
    allowed = set(role_fields.get(role, ())) | {"id"}
    return {k: v for k, v in record.items() if k in allowed}

def mask_secret(value: str, keep_last: int = 4) -> str:
    if len(value) <= keep_last:
        return "*" * len(value)
    return "*" * (len(value) - keep_last) + value[-keep_last:]
""",
        clean_tests="""
from src.field_mask import has_role, mask_secret, project_allowed_fields

def test_legacy_has_role():
    assert has_role({"auditor", "reader"}, "auditor") is True

def test_project_allowed_fields():
    rec = {"id": 1, "name": "Ada", "ssn": "secret"}
    assert project_allowed_fields(rec, "reader", {"reader": {"name"}}) == {"id": 1, "name": "Ada"}

def test_mask_secret():
    assert mask_secret("12345678", 4) == "****5678"
    assert mask_secret("123", 4) == "***"
""",
        false_ci_src="""
def has_role(actor_roles: set[str], required_role: str) -> bool:
    return required_role in actor_roles

def project_allowed_fields(record: dict, role: str, role_fields: dict[str, set[str]]) -> dict:
    return dict(record)

def mask_secret(value: str, keep_last: int = 4) -> str:
    return "*" * 4 + value[-keep_last:]
""",
        false_ci_tests="""
from src.field_mask import has_role, mask_secret, project_allowed_fields

def test_legacy_has_role():
    assert has_role({"auditor", "reader"}, "auditor") is True

def test_mask_secret_short():
    assert mask_secret("12", 4) == "**"
""",
        partial_src="""
def has_role(actor_roles: set[str], required_role: str) -> bool:
    return required_role in actor_roles

def mask_secret(value: str, keep_last: int = 4) -> str:
    if len(value) <= keep_last:
        return "*" * len(value)
    return "*" * (len(value) - keep_last) + value[-keep_last:]
""",
        partial_tests="""
from src.field_mask import has_role, mask_secret

def test_legacy_has_role():
    assert has_role({"auditor", "reader"}, "auditor") is True

def test_mask_secret():
    assert mask_secret("12345678", 4) == "****5678"
    assert mask_secret("123", 4) == "***"
""",
        oracle_tests="""
from src.field_mask import has_role, mask_secret, project_allowed_fields

def test_oracle_field_mask():
    assert has_role({"a"}, "a") is True
    assert project_allowed_fields({"id": 9, "email": "e", "token": "t"}, "support", {"support": {"email"}}) == {"id": 9, "email": "e"}
    assert mask_secret("abcdef", 2) == "****ef" and mask_secret("ab", 4) == "**"
""",
    ),

    # --- T07: scheduling (omits req_2) ---
    make_repo_task(
        task_id="T07",
        domain="scheduling",
        module_name="cron_steps",
        title="Expand Step Ranges and Reject Out-of-Bounds Cron Fields",
        req_1="Add `expand_cron_field(expr, min_v, max_v)` supporting integers, `a-b` ranges, `*`, and `/step` qualifiers returning sorted unique ints.",
        req_2="Raise `ValueError('cron_out_of_bounds')` when any literal or range endpoint falls outside `[min_v, max_v]` cleanly.",
        omitted_req_in_partial="req_2",
        base_src="""
def parse_hour_minute(hhmm: str) -> tuple[int, int]:
    h_s, m_s = hhmm.strip().split(":")
    return int(h_s), int(m_s)
""",
        base_tests="""
from src.cron_steps import parse_hour_minute

def test_legacy_hhmm():
    assert parse_hour_minute("09:30") == (9, 30)
""",
        clean_src="""
def parse_hour_minute(hhmm: str) -> tuple[int, int]:
    h_s, m_s = hhmm.strip().split(":")
    return int(h_s), int(m_s)

def expand_cron_field(expr: str, min_v: int, max_v: int) -> list[int]:
    out: set[int] = set()
    for part in expr.split(","):
        p = part.strip()
        base, _, step_s = p.partition("/")
        step = int(step_s) if step_s else 1
        if step <= 0:
            raise ValueError("cron_out_of_bounds")
        if base == "*":
            lo, hi = min_v, max_v
        elif "-" in base:
            a_s, b_s = base.split("-", 1)
            lo, hi = int(a_s), int(b_s)
        else:
            val = int(base)
            if val < min_v or val > max_v:
                raise ValueError("cron_out_of_bounds")
            out.add(val)
            continue
        if lo < min_v or hi > max_v or lo > hi:
            raise ValueError("cron_out_of_bounds")
        out.update(range(lo, hi + 1, step))
    return sorted(out)
""",
        clean_tests="""
import pytest
from src.cron_steps import expand_cron_field, parse_hour_minute

def test_legacy_hhmm():
    assert parse_hour_minute("09:30") == (9, 30)

def test_expand_step_and_range():
    assert expand_cron_field("0-10/5,12", 0, 59) == [0, 5, 10, 12]

def test_out_of_bounds_raises():
    with pytest.raises(ValueError, match="cron_out_of_bounds"):
        expand_cron_field("0-70", 0, 59)
""",
        false_ci_src="""
def parse_hour_minute(hhmm: str) -> tuple[int, int]:
    h_s, m_s = hhmm.strip().split(":")
    return int(h_s), int(m_s)

def expand_cron_field(expr: str, min_v: int, max_v: int) -> list[int]:
    if expr == "*":
        return list(range(min_v, max_v + 1))
    return [int(expr)]
""",
        false_ci_tests="""
import pytest
from src.cron_steps import expand_cron_field, parse_hour_minute

def test_legacy_hhmm():
    assert parse_hour_minute("09:30") == (9, 30)

def test_expand_step_range():
    assert expand_cron_field("0-10/5", 0, 59) == [0, 5, 10]
""",
        partial_src="""
def parse_hour_minute(hhmm: str) -> tuple[int, int]:
    h_s, m_s = hhmm.strip().split(":")
    return int(h_s), int(m_s)

def expand_cron_field(expr: str, min_v: int, max_v: int) -> list[int]:
    out: set[int] = set()
    for part in expr.split(","):
        p = part.strip()
        base, _, step_s = p.partition("/")
        step = int(step_s) if step_s else 1
        if base == "*":
            lo, hi = min_v, max_v
        elif "-" in base:
            a_s, b_s = base.split("-", 1)
            lo, hi = int(a_s), int(b_s)
        else:
            out.add(int(base))
            continue
        out.update(range(lo, hi + 1, step))
    return sorted(out)
""",
        partial_tests="""
from src.cron_steps import expand_cron_field, parse_hour_minute

def test_legacy_hhmm():
    assert parse_hour_minute("09:30") == (9, 30)

def test_expand_step_and_range():
    assert expand_cron_field("0-10/5,12", 0, 59) == [0, 5, 10, 12]
""",
        oracle_tests="""
import pytest
from src.cron_steps import expand_cron_field, parse_hour_minute

def test_oracle_cron():
    assert parse_hour_minute("01:02") == (1, 2)
    assert expand_cron_field("*/15", 0, 45) == [0, 15, 30, 45]
    with pytest.raises(ValueError, match="cron_out_of_bounds"):
        expand_cron_field("60", 0, 59)
""",
    ),

    # --- T19: scheduling (omits req_1) ---
    make_repo_task(
        task_id="T19",
        domain="scheduling",
        module_name="biz_days",
        title="Roll Dates Past Weekends and Configured Public Holidays",
        req_1="Add `next_business_day(day, holidays=())` advancing past Saturday/Sunday (`weekday() >= 5`) and any date in `holidays` strictly in `datetime.date` arithmetic.",
        req_2="Add `is_business_day(day, holidays=()) -> bool` returning `True` iff `day` is Mon–Fri and not in `holidays`.",
        omitted_req_in_partial="req_1",
        base_src="""
from datetime import date

def parse_iso_date(s: str) -> date:
    return date.fromisoformat(s.strip())
""",
        base_tests="""
from datetime import date
from src.biz_days import parse_iso_date

def test_legacy_parse_date():
    assert parse_iso_date("2026-11-16") == date(2026, 11, 16)
""",
        clean_src="""
from datetime import date, timedelta

def parse_iso_date(s: str) -> date:
    return date.fromisoformat(s.strip())

def is_business_day(day: date, holidays: tuple[date, ...] | set[date] = ()) -> bool:
    return day.weekday() < 5 and day not in set(holidays)

def next_business_day(day: date, holidays: tuple[date, ...] | set[date] = ()) -> date:
    cur = day + timedelta(days=1)
    hset = set(holidays)
    while not is_business_day(cur, hset):
        cur += timedelta(days=1)
    return cur
""",
        clean_tests="""
from datetime import date
from src.biz_days import is_business_day, next_business_day, parse_iso_date

def test_legacy_parse_date():
    assert parse_iso_date("2026-11-16") == date(2026, 11, 16)

def test_is_business_day():
    assert is_business_day(date(2026, 11, 14)) is False
    assert is_business_day(date(2026, 11, 16), {date(2026, 11, 16)}) is False

def test_next_business_day_skips_weekend_and_holiday():
    # Fri 2026-11-13 -> skips Sat/Sun + Mon holiday -> Tue 2026-11-17
    assert next_business_day(date(2026, 11, 13), {date(2026, 11, 16)}) == date(2026, 11, 17)
""",
        false_ci_src="""
from datetime import date, timedelta

def parse_iso_date(s: str) -> date:
    return date.fromisoformat(s.strip())

def is_business_day(day: date, holidays: tuple[date, ...] | set[date] = ()) -> bool:
    return day.weekday() < 5

def next_business_day(day: date, holidays: tuple[date, ...] | set[date] = ()) -> date:
    return day + timedelta(days=1)
""",
        false_ci_tests="""
from datetime import date
from src.biz_days import next_business_day, parse_iso_date

def test_legacy_parse_date():
    assert parse_iso_date("2026-11-16") == date(2026, 11, 16)

def test_next_business_day_skips_weekend():
    assert next_business_day(date(2026, 11, 13)) == date(2026, 11, 16)
""",
        partial_src="""
from datetime import date

def parse_iso_date(s: str) -> date:
    return date.fromisoformat(s.strip())

def is_business_day(day: date, holidays: tuple[date, ...] | set[date] = ()) -> bool:
    return day.weekday() < 5 and day not in set(holidays)
""",
        partial_tests="""
from datetime import date
from src.biz_days import is_business_day, parse_iso_date

def test_legacy_parse_date():
    assert parse_iso_date("2026-11-16") == date(2026, 11, 16)

def test_is_business_day():
    assert is_business_day(date(2026, 11, 14)) is False
    assert is_business_day(date(2026, 11, 16), {date(2026, 11, 16)}) is False
""",
        oracle_tests="""
from datetime import date
from src.biz_days import is_business_day, next_business_day, parse_iso_date

def test_oracle_biz_days():
    assert parse_iso_date("2026-11-16") == date(2026, 11, 16)
    assert is_business_day(date(2026, 11, 16)) is True
    assert next_business_day(date(2026, 11, 13), {date(2026, 11, 16)}) == date(2026, 11, 17)
""",
    ),

    # --- T31: scheduling (omits req_1) ---
    make_repo_task(
        task_id="T31",
        domain="scheduling",
        module_name="window_merge",
        title="Merge Overlapping Maintenance Windows and Detect Quiet Blackouts",
        req_1="Add `merge_windows(intervals)` coalescing overlapping or adjacent half-open `[start, end)` intervals sorted by start.",
        req_2="Add `is_in_blackout(ts, intervals) -> bool` returning `True` iff `start <= ts < end` for any interval.",
        omitted_req_in_partial="req_1",
        base_src="""
def interval_duration(start: int, end: int) -> int:
    return max(0, end - start)
""",
        base_tests="""
from src.window_merge import interval_duration

def test_legacy_duration():
    assert interval_duration(10, 25) == 15
""",
        clean_src="""
def interval_duration(start: int, end: int) -> int:
    return max(0, end - start)

def merge_windows(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    ordered = sorted((s, e) for s, e in intervals if e > s)
    if not ordered:
        return []
    merged: list[tuple[int, int]] = [ordered[0]]
    for s, e in ordered[1:]:
        prev_s, prev_e = merged[-1]
        if s <= prev_e:
            merged[-1] = (prev_s, max(prev_e, e))
        else:
            merged.append((s, e))
    return merged

def is_in_blackout(ts: int, intervals: list[tuple[int, int]]) -> bool:
    return any(s <= ts < e for s, e in intervals)
""",
        clean_tests="""
from src.window_merge import interval_duration, is_in_blackout, merge_windows

def test_legacy_duration():
    assert interval_duration(10, 25) == 15

def test_merge_windows_adjacent():
    assert merge_windows([(10, 20), (20, 30), (35, 40)]) == [(10, 30), (35, 40)]

def test_is_in_blackout_half_open():
    assert is_in_blackout(10, [(10, 20)]) is True
    assert is_in_blackout(20, [(10, 20)]) is False
""",
        false_ci_src="""
def interval_duration(start: int, end: int) -> int:
    return max(0, end - start)

def merge_windows(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    return sorted(intervals)

def is_in_blackout(ts: int, intervals: list[tuple[int, int]]) -> bool:
    return any(s <= ts <= e for s, e in intervals)
""",
        false_ci_tests="""
from src.window_merge import interval_duration, is_in_blackout, merge_windows

def test_legacy_duration():
    assert interval_duration(10, 25) == 15

def test_merge_windows_adjacent():
    assert merge_windows([(10, 20), (20, 30)]) == [(10, 30)]

def test_half_open_end():
    assert is_in_blackout(20, [(10, 20)]) is False
""",
        partial_src="""
def interval_duration(start: int, end: int) -> int:
    return max(0, end - start)

def is_in_blackout(ts: int, intervals: list[tuple[int, int]]) -> bool:
    return any(s <= ts < e for s, e in intervals)
""",
        partial_tests="""
from src.window_merge import interval_duration, is_in_blackout

def test_legacy_duration():
    assert interval_duration(10, 25) == 15

def test_is_in_blackout_half_open():
    assert is_in_blackout(10, [(10, 20)]) is True
    assert is_in_blackout(20, [(10, 20)]) is False
""",
        oracle_tests="""
from src.window_merge import interval_duration, is_in_blackout, merge_windows

def test_oracle_windows():
    assert interval_duration(2, 5) == 3
    assert merge_windows([(15, 25), (10, 20), (30, 35)]) == [(10, 25), (30, 35)]
    assert is_in_blackout(10, [(10, 20)]) and (not is_in_blackout(20, [(10, 20)]))
""",
    ),

    # --- T08: semver (omits req_2) ---
    make_repo_task(
        task_id="T08",
        domain="semver",
        module_name="caret_spec",
        title="Match SemVer Caret Bounds and Reject Prerelease Opt-Out",
        req_1="Add `matches_caret(version, floor)` enforcing `>= floor` and strictly `< next_major` (`< (0, minor+1, 0)` when `major == 0 and minor > 0`; `< (0, 0, patch+1)` when `major == 0 and minor == 0`) on `(major, minor, patch)` tuples.",
        req_2="Extend `parse_semver_tag(tag)` returning `(major, minor, patch, pre: str | None)` and reject prerelease versions in `matches_caret(...)` unless `allow_prerelease=True`.",
        omitted_req_in_partial="req_2",
        base_src="""
def parse_core_tuple(ver: str) -> tuple[int, int, int]:
    parts = ver.lstrip("v").split("-", 1)[0].split(".")
    return int(parts[0]), int(parts[1]), int(parts[2])
""",
        base_tests="""
from src.caret_spec import parse_core_tuple

def test_legacy_core_tuple():
    assert parse_core_tuple("v1.2.3") == (1, 2, 3)
""",
        clean_src="""
def parse_core_tuple(ver: str) -> tuple[int, int, int]:
    parts = ver.lstrip("v").split("-", 1)[0].split(".")
    return int(parts[0]), int(parts[1]), int(parts[2])

def parse_semver_tag(tag: str) -> tuple[int, int, int, str | None]:
    core, _, pre = tag.lstrip("v").partition("-")
    maj, min_, pat = (int(x) for x in core.split("."))
    return maj, min_, pat, (pre or None)

def matches_caret(version: str, floor: str, allow_prerelease: bool = False) -> bool:
    maj, min_, pat, pre = parse_semver_tag(version)
    if pre is not None and not allow_prerelease:
        return False
    f_maj, f_min, f_pat, _ = parse_semver_tag(floor)
    v = (maj, min_, pat)
    f = (f_maj, f_min, f_pat)
    if f_maj == 0:
        upper = (0, 0, f_pat + 1) if f_min == 0 else (0, f_min + 1, 0)
    else:
        upper = (f_maj + 1, 0, 0)
    return f <= v < upper
""",
        clean_tests="""
from src.caret_spec import matches_caret, parse_core_tuple, parse_semver_tag

def test_legacy_core_tuple():
    assert parse_core_tuple("v1.2.3") == (1, 2, 3)

def test_caret_bounds():
    assert matches_caret("1.9.0", "1.2.0") is True
    assert matches_caret("2.0.0", "1.2.0") is False
    assert matches_caret("0.2.5", "0.2.0") is True
    assert matches_caret("0.3.0", "0.2.0") is False

def test_prerelease_excluded_by_default():
    assert parse_semver_tag("1.3.0-rc1") == (1, 3, 0, "rc1")
    assert matches_caret("1.3.0-rc1", "1.2.0") is False
    assert matches_caret("1.3.0-rc1", "1.2.0", allow_prerelease=True) is True
""",
        false_ci_src="""
def parse_core_tuple(ver: str) -> tuple[int, int, int]:
    parts = ver.lstrip("v").split("-", 1)[0].split(".")
    return int(parts[0]), int(parts[1]), int(parts[2])

def parse_semver_tag(tag: str) -> tuple[int, int, int, str | None]:
    return (*parse_core_tuple(tag), None)

def matches_caret(version: str, floor: str, allow_prerelease: bool = False) -> bool:
    v = parse_core_tuple(version)
    f = parse_core_tuple(floor)
    return f <= v < (f[0] + 1, 0, 0)
""",
        false_ci_tests="""
from src.caret_spec import matches_caret, parse_core_tuple, parse_semver_tag

def test_legacy_core_tuple():
    assert parse_core_tuple("v1.2.3") == (1, 2, 3)

def test_zero_major_and_prerelease():
    assert matches_caret("0.3.0", "0.2.0") is False
    assert matches_caret("1.3.0-rc1", "1.2.0") is False
""",
        partial_src="""
def parse_core_tuple(ver: str) -> tuple[int, int, int]:
    parts = ver.lstrip("v").split("-", 1)[0].split(".")
    return int(parts[0]), int(parts[1]), int(parts[2])

def matches_caret(version: str, floor: str) -> bool:
    v = parse_core_tuple(version)
    f = parse_core_tuple(floor)
    if f[0] == 0:
        upper = (0, 0, f[2] + 1) if f[1] == 0 else (0, f[1] + 1, 0)
    else:
        upper = (f[0] + 1, 0, 0)
    return f <= v < upper
""",
        partial_tests="""
from src.caret_spec import matches_caret, parse_core_tuple

def test_legacy_core_tuple():
    assert parse_core_tuple("v1.2.3") == (1, 2, 3)

def test_caret_bounds():
    assert matches_caret("1.9.0", "1.2.0") is True
    assert matches_caret("2.0.0", "1.2.0") is False
    assert matches_caret("0.2.5", "0.2.0") is True
    assert matches_caret("0.3.0", "0.2.0") is False
""",
        oracle_tests="""
from src.caret_spec import matches_caret, parse_core_tuple, parse_semver_tag

def test_oracle_caret_and_pre():
    assert parse_core_tuple("1.0.0") == (1, 0, 0)
    assert parse_semver_tag("1.2.3-alpha") == (1, 2, 3, "alpha")
    assert matches_caret("0.2.9", "0.2.0") is True
    assert matches_caret("0.3.0", "0.2.0") is False
    assert matches_caret("1.3.0-rc1", "1.2.0") is False
""",
    ),

    # --- T20: semver (omits req_1) ---
    make_repo_task(
        task_id="T20",
        domain="semver",
        module_name="tilde_spec",
        title="Support Tilde Patch Bounds and Highest Compatible Version Selection",
        req_1="Add `matches_tilde(version, floor)` permitting patch updates strictly `< (major, minor + 1, 0)` and `>= (major, minor, patch)`.",
        req_2="Add `pick_highest_matching(candidates, predicate)` returning the highest SemVer string matching `predicate(v)` or `None` if empty.",
        omitted_req_in_partial="req_1",
        base_src="""
def ver_key(ver: str) -> tuple[int, int, int]:
    return tuple(int(p) for p in ver.lstrip("v").split("."))  # type: ignore[return-value]
""",
        base_tests="""
from src.tilde_spec import ver_key

def test_legacy_ver_key():
    assert ver_key("1.4.2") == (1, 4, 2)
""",
        clean_src="""
from typing import Callable

def ver_key(ver: str) -> tuple[int, int, int]:
    return tuple(int(p) for p in ver.lstrip("v").split("."))  # type: ignore[return-value]

def matches_tilde(version: str, floor: str) -> bool:
    v = ver_key(version)
    f = ver_key(floor)
    return f <= v < (f[0], f[1] + 1, 0)

def pick_highest_matching(candidates: list[str], predicate: Callable[[str], bool]) -> str | None:
    matching = [c for c in candidates if predicate(c)]
    if not matching:
        return None
    return max(matching, key=ver_key)
""",
        clean_tests="""
from src.tilde_spec import matches_tilde, pick_highest_matching, ver_key

def test_legacy_ver_key():
    assert ver_key("1.4.2") == (1, 4, 2)

def test_matches_tilde():
    assert matches_tilde("1.4.9", "1.4.2") is True
    assert matches_tilde("1.5.0", "1.4.2") is False

def test_pick_highest_matching():
    assert pick_highest_matching(["1.2.1", "1.2.9", "1.3.0"], lambda v: v.startswith("1.2.")) == "1.2.9"
    assert pick_highest_matching([], lambda v: True) is None
""",
        false_ci_src="""
from typing import Callable

def ver_key(ver: str) -> tuple[int, int, int]:
    return tuple(int(p) for p in ver.lstrip("v").split("."))  # type: ignore[return-value]

def matches_tilde(version: str, floor: str) -> bool:
    v = ver_key(version)
    f = ver_key(floor)
    return f <= v <= (f[0], f[1] + 1, 0)

def pick_highest_matching(candidates: list[str], predicate: Callable[[str], bool]) -> str | None:
    matching = [c for c in candidates if predicate(c)]
    return max(matching) if matching else None
""",
        false_ci_tests="""
from src.tilde_spec import matches_tilde, pick_highest_matching, ver_key

def test_legacy_ver_key():
    assert ver_key("1.4.2") == (1, 4, 2)

def test_tilde_upper_and_numeric_max():
    assert matches_tilde("1.5.0", "1.4.2") is False
    assert pick_highest_matching(["1.2.2", "1.2.10"], lambda _: True) == "1.2.10"
""",
        partial_src="""
from typing import Callable

def ver_key(ver: str) -> tuple[int, int, int]:
    return tuple(int(p) for p in ver.lstrip("v").split("."))  # type: ignore[return-value]

def pick_highest_matching(candidates: list[str], predicate: Callable[[str], bool]) -> str | None:
    matching = [c for c in candidates if predicate(c)]
    if not matching:
        return None
    return max(matching, key=ver_key)
""",
        partial_tests="""
from src.tilde_spec import pick_highest_matching, ver_key

def test_legacy_ver_key():
    assert ver_key("1.4.2") == (1, 4, 2)

def test_pick_highest_matching():
    assert pick_highest_matching(["1.2.1", "1.2.9", "1.3.0"], lambda v: v.startswith("1.2.")) == "1.2.9"
    assert pick_highest_matching([], lambda v: True) is None
""",
        oracle_tests="""
from src.tilde_spec import matches_tilde, pick_highest_matching, ver_key

def test_oracle_tilde():
    assert ver_key("2.0.1") == (2, 0, 1)
    assert matches_tilde("1.4.12", "1.4.2") is True
    assert matches_tilde("1.5.0", "1.4.2") is False
    assert pick_highest_matching(["1.2.2", "1.2.10"], lambda _: True) == "1.2.10"
""",
    ),

    # --- T32: semver (omits req_1) ---
    make_repo_task(
        task_id="T32",
        domain="semver",
        module_name="lock_resolver",
        title="Verify Lockfile Pin Integrity and Detect Breaking Upgrades",
        req_1="Add `is_breaking_bump(old_ver, new_ver) -> bool` returning `True` when `new_ver` increments major version (`new[0] > old[0]`) or increments minor on `0.y.z` (`old[0] == 0 and new[1] > old[1]`).",
        req_2="Add `verify_lock_pins(declared, locked)` returning sorted list of package names present in `declared` that are missing from `locked` or violate exact version equality.",
        omitted_req_in_partial="req_1",
        base_src="""
def split_ver(v: str) -> tuple[int, int, int]:
    a, b, c = v.split(".")
    return int(a), int(b), int(c)
""",
        base_tests="""
from src.lock_resolver import split_ver

def test_legacy_split_ver():
    assert split_ver("0.9.1") == (0, 9, 1)
""",
        clean_src="""
def split_ver(v: str) -> tuple[int, int, int]:
    a, b, c = v.split(".")
    return int(a), int(b), int(c)

def is_breaking_bump(old_ver: str, new_ver: str) -> bool:
    o = split_ver(old_ver)
    n = split_ver(new_ver)
    if n[0] > o[0]:
        return True
    return o[0] == 0 and n[0] == 0 and n[1] > o[1]

def verify_lock_pins(declared: dict[str, str], locked: dict[str, str]) -> list[str]:
    bad: list[str] = []
    for pkg, ver in declared.items():
        if locked.get(pkg) != ver:
            bad.append(pkg)
    return sorted(bad)
""",
        clean_tests="""
from src.lock_resolver import is_breaking_bump, split_ver, verify_lock_pins

def test_legacy_split_ver():
    assert split_ver("0.9.1") == (0, 9, 1)

def test_breaking_bump_zero_major():
    assert is_breaking_bump("1.2.0", "1.3.0") is False
    assert is_breaking_bump("0.2.0", "0.3.0") is True
    assert is_breaking_bump("1.2.0", "2.0.0") is True

def test_verify_lock_pins():
    assert verify_lock_pins({"a": "1.0.0", "b": "2.0.0"}, {"a": "1.0.0"}) == ["b"]
""",
        false_ci_src="""
def split_ver(v: str) -> tuple[int, int, int]:
    a, b, c = v.split(".")
    return int(a), int(b), int(c)

def is_breaking_bump(old_ver: str, new_ver: str) -> bool:
    return split_ver(new_ver)[0] > split_ver(old_ver)[0]

def verify_lock_pins(declared: dict[str, str], locked: dict[str, str]) -> list[str]:
    return [pkg for pkg, ver in declared.items() if locked.get(pkg) != ver]
""",
        false_ci_tests="""
from src.lock_resolver import is_breaking_bump, split_ver

def test_legacy_split_ver():
    assert split_ver("0.9.1") == (0, 9, 1)

def test_breaking_bump_zero_major():
    assert is_breaking_bump("0.2.0", "0.3.0") is True
""",
        partial_src="""
def split_ver(v: str) -> tuple[int, int, int]:
    a, b, c = v.split(".")
    return int(a), int(b), int(c)

def verify_lock_pins(declared: dict[str, str], locked: dict[str, str]) -> list[str]:
    return sorted(pkg for pkg, ver in declared.items() if locked.get(pkg) != ver)
""",
        partial_tests="""
from src.lock_resolver import split_ver, verify_lock_pins

def test_legacy_split_ver():
    assert split_ver("0.9.1") == (0, 9, 1)

def test_verify_lock_pins():
    assert verify_lock_pins({"a": "1.0.0", "b": "2.0.0"}, {"a": "1.0.0"}) == ["b"]
""",
        oracle_tests="""
from src.lock_resolver import is_breaking_bump, split_ver, verify_lock_pins

def test_oracle_lock_resolver():
    assert split_ver("1.2.3") == (1, 2, 3)
    assert is_breaking_bump("0.1.0", "0.2.0") is True
    assert is_breaking_bump("1.1.0", "1.9.0") is False
    assert verify_lock_pins({"b": "1", "a": "2"}, {"b": "1"}) == ["a"]
""",
    ),
]
