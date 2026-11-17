"""Task registry exposing all 4 calibration repos (C00..C03) and 36 confirmatory repos (T00..T35)."""

from __future__ import annotations

from .task_bank.part1_limits_billing_auth import TASKS_PART1
from .task_bank.part2_etl_retry_sanitizer import TASKS_PART2
from .task_bank.part3_rbac_sched_semver import TASKS_PART3
from .task_bank.part4_uri_cache_page import TASKS_PART4
from .task_bank.schema import TaskSpec


def _sort_key(t: TaskSpec) -> tuple[int, int]:
    prefix = 0 if t.task_id.startswith("C") else 1
    return (prefix, int(t.task_id[1:]))


ALL_TASKS: list[TaskSpec] = sorted(
    TASKS_PART1 + TASKS_PART2 + TASKS_PART3 + TASKS_PART4,
    key=_sort_key,
)

CALIBRATION_TASKS: list[TaskSpec] = [t for t in ALL_TASKS if t.is_calibration()]
CONFIRMATORY_TASKS: list[TaskSpec] = [t for t in ALL_TASKS if not t.is_calibration()]
TASK_BY_ID: dict[str, TaskSpec] = {t.task_id: t for t in ALL_TASKS}


def select_tasks(suite: str) -> list[TaskSpec]:
    if suite == "calibration":
        return list(CALIBRATION_TASKS)
    if suite == "confirmatory":
        return list(CONFIRMATORY_TASKS)
    if suite == "all":
        return list(ALL_TASKS)
    ids = [s.strip() for s in suite.split(",") if s.strip()]
    return [TASK_BY_ID[tid] for tid in ids]
