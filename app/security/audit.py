from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def query_fingerprint(query: str) -> str:
    return hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]


def record_audit_event(event: str, **details: Any) -> None:
    """Append metadata-only audit events without credentials or result data."""
    default_path = Path(__file__).resolve().parents[2] / "logs" / "audit.jsonl"
    path = Path(os.getenv("AUDIT_LOG_PATH", str(default_path))).expanduser()
    payload = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event": event,
        **details,
    }
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as audit_file:
            audit_file.write(json.dumps(payload, default=str) + "\n")
    except OSError:
        # Audit storage must not expose filesystem details to app users.
        pass
