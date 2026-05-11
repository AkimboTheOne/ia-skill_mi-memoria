from __future__ import annotations

import json
from pathlib import Path


def append_operation_logs(
    *,
    text_log_path: Path,
    jsonl_log_path: Path,
    timestamp: str,
    action: str,
    source: str,
    destination: str,
    result: str,
) -> None:
    text_line = f"{timestamp}\taction={action}\tsource={source}\tdestination={destination}\tresult={result}\n"
    with text_log_path.open("a", encoding="utf-8") as handle:
        handle.write(text_line)

    event = {
        "timestamp": timestamp,
        "command": action,
        "status": result,
        "source": source,
        "destination": destination,
        "message_nl": f"{action}: {result} desde {source} hacia {destination}",
    }
    with jsonl_log_path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
