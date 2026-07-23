"""Hash-chained audit ledger for experiment reproducibility."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any


def _hash_record(record: dict[str, Any]) -> str:
    payload = json.dumps(record, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def append_record(path: str | Path, payload: dict[str, Any]) -> dict[str, Any]:
    """Append an immutable-style hash-linked audit record."""
    audit_path = Path(path)
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    previous_hash = "GENESIS"
    sequence = 1
    if audit_path.exists():
        lines = [line for line in audit_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        if lines:
            last = json.loads(lines[-1])
            previous_hash = last["record_hash"]
            sequence = int(last["sequence"]) + 1
    record = {"sequence": sequence, "previous_hash": previous_hash, "payload": payload}
    record["record_hash"] = _hash_record(record)
    with audit_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
    return record


def verify_log(path: str | Path) -> dict[str, Any]:
    """Verify hash-chain continuity."""
    audit_path = Path(path)
    if not audit_path.exists():
        return {"valid": True, "records": 0}
    previous = "GENESIS"
    count = 0
    for line in audit_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        record_hash = record.get("record_hash")
        check = dict(record)
        check.pop("record_hash", None)
        if record.get("previous_hash") != previous or _hash_record(check) != record_hash:
            return {"valid": False, "records": count}
        previous = record_hash
        count += 1
    return {"valid": True, "records": count}
