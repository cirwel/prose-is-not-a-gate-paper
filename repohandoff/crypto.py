"""Deterministic Ed25519 signing and CI+digest verification gates."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

from . import sandbox

DEFAULT_AUDIENCE = "maintainer-beta"


def canonical_json(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"))


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def derive_keypair(principal: str) -> tuple[Ed25519PrivateKey, Ed25519PublicKey, str]:
    seed = hashlib.sha256(f"repohandoff:{principal}:ed25519:v1".encode("utf-8")).digest()
    priv = Ed25519PrivateKey.from_private_bytes(seed)
    pub = priv.public_key()
    pub_raw = pub.public_bytes(Encoding.Raw, PublicFormat.Raw)
    fp = hashlib.sha256(pub_raw).hexdigest()[:16]
    return priv, pub, fp


def compute_tree_sha256(worktree_dir: Path | str) -> str:
    root = Path(worktree_dir).resolve()
    h = hashlib.sha256()
    for rel in sandbox.list_files(root):
        data = (root / rel).read_bytes()
        h.update(rel.encode("utf-8"))
        h.update(b"\x00")
        h.update(hashlib.sha256(data).digest())
        h.update(b"\n")
    return h.hexdigest()


def issue_voucher(
    worktree_dir: Path | str,
    task_id: str,
    report: dict[str, Any],
    issuer: str = "contributor-alpha",
    audience: str = DEFAULT_AUDIENCE,
) -> dict[str, Any]:
    priv, _, fp = derive_keypair(issuer)
    payload = {
        "task_id": task_id,
        "tree_sha256": compute_tree_sha256(worktree_dir),
        "report_sha256": sha256_text(canonical_json(report)),
        "reported_pytest_exit": int(report.get("reported_pytest_exit", 0)),
        "reported_passed_tests": sorted(str(t) for t in report.get("passed_tests", [])),
        "issuer": issuer,
        "audience": audience,
    }
    sig = priv.sign(canonical_json(payload).encode("utf-8"))
    return {
        "payload": payload,
        "signature_hex": sig.hex(),
        "key_fingerprint": fp,
        "issuer": issuer,
        "audience": audience,
    }


def verify_origin_gate(
    voucher: dict[str, Any],
    expected_issuer: str = "contributor-alpha",
    expected_audience: str = DEFAULT_AUDIENCE,
    expected_task_id: str | None = None,
) -> dict[str, Any]:
    reasons: list[str] = []
    payload = voucher.get("payload")
    sig_hex = voucher.get("signature_hex")
    if not isinstance(payload, dict) or not isinstance(sig_hex, str):
        return {"ok": False, "reasons": ["malformed_voucher"], "key_fingerprint": None}
    if payload.get("issuer") != expected_issuer:
        reasons.append(f"unexpected_issuer:{payload.get('issuer')}")
    if payload.get("audience") != expected_audience:
        reasons.append(f"unexpected_audience:{payload.get('audience')}")
    if expected_task_id is not None and payload.get("task_id") != expected_task_id:
        reasons.append(f"unexpected_task:{payload.get('task_id')}")
    _, pub, fp = derive_keypair(expected_issuer)
    try:
        pub.verify(bytes.fromhex(sig_hex), canonical_json(payload).encode("utf-8"))
    except (ValueError, InvalidSignature):
        reasons.append("invalid_signature")
    return {"ok": len(reasons) == 0, "reasons": reasons, "key_fingerprint": fp}


def verify_ci_digest_gate(
    worktree_dir: Path | str,
    voucher: dict[str, Any],
    report: dict[str, Any],
    expected_issuer: str = "contributor-alpha",
) -> dict[str, Any]:
    origin = verify_origin_gate(voucher, expected_issuer=expected_issuer)
    reasons = list(origin["reasons"])
    payload = voucher.get("payload", {})
    actual_tree = compute_tree_sha256(worktree_dir)
    if payload.get("tree_sha256") != actual_tree:
        reasons.append("tree_digest_mismatch")
    if payload.get("report_sha256") != sha256_text(canonical_json(report)):
        reasons.append("report_digest_mismatch")
    pt = sandbox.run_pytest(worktree_dir)
    if pt["exit_code"] != 0:
        reasons.append(f"pytest_failed_exit_{pt['exit_code']}")
    if not pt["passed_tests"]:
        reasons.append("no_passed_tests_observed")
    reported = sorted(str(t) for t in report.get("passed_tests", []))
    actual = sorted(pt["passed_tests"])
    if reported != actual:
        reasons.append("passed_tests_mismatch")
    return {
        "ok": len(reasons) == 0,
        "origin_ok": origin["ok"],
        "actual_exit": pt["exit_code"],
        "actual_passed": actual,
        "actual_failed": pt["failed_tests"],
        "actual_tree_sha256": actual_tree,
        "reasons": reasons,
    }
