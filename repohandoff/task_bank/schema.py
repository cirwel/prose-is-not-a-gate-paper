"""Core dataclass and constructor helper for RepoHandoff tasks."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TaskSpec:
    task_id: str
    domain: str
    module_name: str
    title: str
    req_1: str
    req_2: str
    omitted_req_in_partial: str
    base_files: dict[str, str]
    patch_clean: dict[str, str]
    patch_false_ci: dict[str, str]
    patch_partial: dict[str, str]
    oracle_test_code: str

    def is_calibration(self) -> bool:
        return self.task_id.startswith("C")

    def ticket_text(self) -> str:
        return (
            f"Ticket {self.task_id}: {self.title} (module: src/{self.module_name}.py)\n"
            f"- Req 1: {self.req_1}\n"
            f"- Req 2: {self.req_2}\n"
            "Constraints: Preserve all existing passing behavior and legacy public function signatures."
        )


def make_repo_task(
    *,
    task_id: str,
    domain: str,
    module_name: str,
    title: str,
    req_1: str,
    req_2: str,
    omitted_req_in_partial: str,
    base_src: str,
    base_tests: str,
    clean_src: str,
    clean_tests: str,
    false_ci_src: str,
    false_ci_tests: str,
    partial_src: str,
    partial_tests: str,
    oracle_tests: str,
) -> TaskSpec:
    src_path = f"src/{module_name}.py"
    test_path = f"tests/test_{module_name}.py"
    return TaskSpec(
        task_id=task_id,
        domain=domain,
        module_name=module_name,
        title=title,
        req_1=req_1,
        req_2=req_2,
        omitted_req_in_partial=omitted_req_in_partial,
        base_files={
            "src/__init__.py": "",
            src_path: base_src.lstrip("\n"),
            test_path: base_tests.lstrip("\n"),
        },
        patch_clean={
            src_path: clean_src.lstrip("\n"),
            test_path: clean_tests.lstrip("\n"),
        },
        patch_false_ci={
            src_path: false_ci_src.lstrip("\n"),
            test_path: false_ci_tests.lstrip("\n"),
        },
        patch_partial={
            src_path: partial_src.lstrip("\n"),
            test_path: partial_tests.lstrip("\n"),
        },
        oracle_test_code=oracle_tests.lstrip("\n"),
    )
