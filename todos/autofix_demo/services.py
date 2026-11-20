"""Service layer for complex DEBUG demos (in-memory cards, no auth required)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from . import utils

_DEMO_CARDS: list[dict[str, Any]] = [
    {
        "id": "11111111-1111-1111-1111-111111111111",
        "title": "Ship board digest",
        "priority": "high",
        "status": "open",
        "due_at": None,
        "assignee": None,
    },
    {
        "id": "22222222-2222-2222-2222-222222222222",
        "title": "Triage medium bugs",
        "priority": "medium",
        "status": "open",
        "due_at": datetime.now(timezone.utc) + timedelta(days=2),
        "assignee": {"email": "owner@linear.test", "name": "Owner"},
    },
    {
        "id": "33333333-3333-3333-3333-333333333333",
        "title": "Archive old noise",
        "priority": "low",
        "status": "done",
        "due_at": datetime.now(timezone.utc) - timedelta(days=5),
        "assignee": {"email": "ops@linear.test", "name": "Ops"},
    },
]


def _cards(*, include_done: bool) -> list[dict[str, Any]]:
    if include_done:
        return list(_DEMO_CARDS)
    return [c for c in _DEMO_CARDS if c["status"] != "done"]


def build_board_digest(*, window: str = "week", include_done: bool = False) -> dict[str, Any]:
    """
    Aggregate demo cards into a priority board digest.

    Calls into utils for due labels and priority weights — that is where
    AttributeError / KeyError fire for the high-priority / undated card.
    """
    cards = _cards(include_done=include_done)
    # Sort by weight first — KeyError on "high" before we even format dues.
    ordered = sorted(cards, key=lambda c: utils.priority_weight(c["priority"]), reverse=True)

    rows = []
    for card in ordered:
        rows.append(
            {
                "id": card["id"],
                "title": card["title"],
                "priority": card["priority"],
                "status": card["status"],
                "due_label": utils.format_due_label(card["due_at"]),
                "weight": utils.priority_weight(card["priority"]),
            }
        )

    return {
        "window": window,
        "count": len(rows),
        "rows": rows,
    }


def bulk_complete_todos(*, todo_ids: list[str], actor: str = "") -> dict[str, Any]:
    """
    Mark many todos complete.

    Parses each id through ``utils.parse_todo_ref`` (intentional int cast bug)
    before applying status transitions.
    """
    completed = []
    for raw in todo_ids:
        ref = utils.parse_todo_ref(raw)
        # Unreachable with current bug; kept so a correct fix still looks real.
        card = next((c for c in _DEMO_CARDS if c["id"] == raw), None)
        if card is None:
            raise LookupError(f"Unknown todo: {raw}")
        utils.assert_can_complete(card["status"])
        card["status"] = "done"
        completed.append({"id": raw, "ref": ref, "actor": actor or "system"})

    return {"completed": completed, "count": len(completed)}


def preview_notify(*, todo_id: str | None = None) -> dict[str, Any]:
    """
    Build a notification preview for one todo.

    Default card is the unassigned high-priority item so ``build_notify_payload``
    hits the assignee None bug (and may also hit format_due_label).
    """
    if todo_id:
        card = next((c for c in _DEMO_CARDS if c["id"] == todo_id), None)
        if card is None:
            raise LookupError(f"Unknown todo: {todo_id}")
    else:
        card = _DEMO_CARDS[0]  # unassigned, due_at=None

    payload = utils.build_notify_payload(card)
    return {"todo_id": card["id"], "payload": payload}


_SPRINT_WINDOWS: dict[str, dict[str, Any]] = {
    # Empty sprint — velocity helper divides by completed_days.
    "empty": {"total_points": 0, "completed_days": 0, "label": "Sprint 0 (empty)"},
    "active": {"total_points": 34, "completed_days": 5, "label": "Sprint 12"},
}


_LOAD_ROWS: list[dict[str, Any]] = [
    {"email": None, "open_count": 4, "title": "Unassigned backlog"},
    {"email": "owner@linear.test", "open_count": 2, "title": "Owner queue"},
]


def build_sprint_velocity(*, window: str = "empty") -> dict[str, Any]:
    """Roll up story-point velocity for a canned sprint window."""
    sprint = _SPRINT_WINDOWS.get(window) or _SPRINT_WINDOWS["empty"]
    rate = utils.velocity_per_day(sprint["total_points"], sprint["completed_days"])
    return {
        "window": window,
        "label": sprint["label"],
        "total_points": sprint["total_points"],
        "completed_days": sprint["completed_days"],
        "points_per_day": rate,
    }


def build_assignee_load() -> dict[str, Any]:
    """Per-assignee open-work chart for the demo board."""
    rows = []
    for row in _LOAD_ROWS:
        rows.append(
            {
                "handle": utils.handle_local_part(row["email"]),
                "open_count": row["open_count"],
                "title": row["title"],
            }
        )
    return {"count": len(rows), "rows": rows}


def build_tag_rollup(*, tags: Any) -> dict[str, Any]:
    """
    Frequency table for client-supplied tags.

    Clients sometimes send a comma-separated string; the helper expects a list.
    """
    freq = utils.tag_frequency(tags)
    colored = []
    for name, count in freq.items():
        # Demo palette lookup — missing keys fall through to raw name as color.
        color = {"bug": "#e11", "ops": "#1a1"}.get(name, name)
        colored.append(
            {
                "tag": name,
                "count": count,
                "rgb": utils.hex_to_rgb(color),
            }
        )
    return {"tags": colored, "unique": len(colored)}
