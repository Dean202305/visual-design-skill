#!/usr/bin/env python3
"""Read or record local visual design revisions and preferences with Python 3."""
import argparse
import json
import os
import sqlite3
import sys
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path


SCOPES = ("global", "medium", "project")
OUTCOMES = {"proposed", "applied", "accepted", "rejected", "reverted"}
DATABASE = "design-memory.sqlite3"
PPT_REFERENCES = "ppt-references.md"
SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    id TEXT PRIMARY KEY,
    recorded_at TEXT NOT NULL,
    payload TEXT NOT NULL
)
"""


def clean_text(value, field):
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} requires nonempty text")
    return value.strip()


def normalize_event(raw):
    if not isinstance(raw, dict):
        raise ValueError("Input must be one JSON object")
    event = {"id": clean_text(raw.get("id"), "id")}
    if "revision" in raw:
        revision = raw["revision"]
        if not isinstance(revision, dict):
            raise ValueError("revision must be an object")
        fields = ("id", "project", "artifact", "medium", "feedback", "change", "status")
        event["revision"] = {field: clean_text(revision.get(field), f"revision.{field}") for field in fields}
        if event["revision"]["status"] not in OUTCOMES:
            raise ValueError(f"revision.status must be one of {', '.join(sorted(OUTCOMES))}")
        for field in ("before", "check"):
            if field in revision:
                event["revision"][field] = clean_text(revision[field], f"revision.{field}")

    preferences = raw.get("preferences", [])
    if not isinstance(preferences, list):
        raise ValueError("preferences must be a list")
    learned = []
    seen = set()
    for item in preferences:
        if not isinstance(item, dict):
            raise ValueError("Each preference must be an object")
        scope = item.get("scope")
        if scope not in SCOPES:
            raise ValueError("preference.scope must be global, medium, or project")
        context = clean_text(item.get("context"), "preference.context") if scope != "global" else ""
        key = clean_text(item.get("key"), "preference.key")
        evidence = clean_text(item.get("evidence"), "preference.evidence")
        if "value" not in item:
            raise ValueError("preference.value must contain a decision or null to retract it")
        value = item["value"]
        if value is not None:
            value = clean_text(value, "preference.value")
        identity = (scope, context, key)
        if identity in seen:
            raise ValueError("Each preference may appear only once in an event")
        seen.add(identity)
        learned.append({"scope": scope, "context": context, "key": key, "value": value, "evidence": evidence})
    if learned:
        event["preferences"] = learned
    if "revision" not in event and not learned:
        raise ValueError("Provide a revision or a confirmed preference")
    return event


def record(folder, raw):
    event = normalize_event(raw)
    canonical = json.dumps(event, ensure_ascii=False, sort_keys=True)
    folder.mkdir(mode=0o700, parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    with closing(sqlite3.connect(folder / DATABASE, timeout=8)) as database, database:
        database.execute(SCHEMA)
        cursor = database.execute(
            "INSERT OR IGNORE INTO events(id, recorded_at, payload) VALUES (?, ?, ?)",
            (event["id"], timestamp, canonical),
        )
        if cursor.rowcount == 0:
            stored = database.execute("SELECT payload FROM events WHERE id = ?", (event["id"],)).fetchone()[0]
            if stored != canonical:
                raise ValueError("This event ID already has different content. Use a new event ID for a later decision.")
    return {"id": event["id"], "recorded": cursor.rowcount == 1}


def events(folder):
    target = folder / DATABASE
    if not target.is_file():
        return []
    with closing(sqlite3.connect(target.as_uri() + "?mode=ro", uri=True, timeout=8)) as database:
        rows = database.execute("SELECT recorded_at, payload FROM events ORDER BY rowid DESC")
        return [dict(json.loads(payload), recorded_at=timestamp) for timestamp, payload in rows]


def revisions(rows, project, medium, artifact):
    for event in rows:
        revision = event.get("revision")
        if not revision:
            continue
        if project and revision["project"] != project:
            continue
        if medium and revision["medium"] != medium:
            continue
        if artifact and revision["artifact"] != artifact:
            continue
        yield dict(revision, event_id=event["id"], recorded_at=event["recorded_at"])


def recall(folder, project, medium, artifact, limit):
    rows = events(folder)
    context = {"global": "", "medium": medium, "project": project}
    current = {}
    for event in rows:
        for preference in event.get("preferences", []):
            scope = preference["scope"]
            selector = context[scope]
            if selector is not None and preference["context"] == selector:
                identity = (scope, preference["key"])
                current.setdefault(identity, dict(preference, event_id=event["id"]))
    effective = {}
    for scope in SCOPES:
        for (level, key), preference in current.items():
            if scope == level and preference["value"] is not None:
                effective[key] = preference

    recent = {}
    if project:
        for revision in revisions(rows, project, medium, artifact):
            identity = (revision["medium"], revision["artifact"], revision["id"])
            recent.setdefault(identity, revision)
    result = {
        "enabled": (folder / DATABASE).is_file(),
        "preferences": [effective[key] for key in sorted(effective)],
        "recent_revisions": list(recent.values())[:limit],
    }
    index = folder / PPT_REFERENCES
    if medium == "slides" and index.is_file():
        result["ppt_references"] = str(index)
    return result


def main():
    default = Path(os.getenv("VISUAL_DESIGN_MEMORY_DIR") or "~/.visual-design/memory")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--memory-dir", type=Path, default=default)
    commands = parser.add_subparsers(dest="command", required=True)
    save = commands.add_parser("record", help="Record a revision or explicit preference from JSON")
    save.add_argument("input", help="UTF-8 JSON file, or - for standard input")
    for command in ("recall", "history"):
        lookup = commands.add_parser(command)
        lookup.add_argument("--project")
        lookup.add_argument("--medium")
        lookup.add_argument("--artifact")
        lookup.add_argument("--limit", type=int, default=5 if command == "recall" else 30)
    args = parser.parse_args()
    folder = args.memory_dir.expanduser().absolute()
    try:
        if args.command == "record":
            os.umask(0o077)
            source = sys.stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
            result = record(folder, json.loads(source))
        else:
            if args.limit < 1:
                raise ValueError("--limit must be positive")
            if args.command == "recall":
                result = recall(folder, args.project, args.medium, args.artifact, args.limit)
            else:
                rows = list(revisions(events(folder), args.project, args.medium, args.artifact))
                result = {"total": len(rows), "revisions": rows[:args.limit]}
    except (OSError, ValueError, sqlite3.Error) as error:
        parser.exit(1, f"Design memory: {error}\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
