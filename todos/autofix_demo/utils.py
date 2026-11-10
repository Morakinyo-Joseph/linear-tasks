"""
Pure helpers for autofix demos.

Intentional bugs live here on purpose: the view/service look plausible;
the failure is a few frames deeper (more realistic auto-fix target).
"""

from __future__ import annotations

from datetime import datetime
from typing import Any


PRIORITY_WEIGHTS = {
    "low": 1,
    "medium": 2,
    # Deliberately omit "high" — board digest KeyErrors on high-priority cards.
}


def format_due_label(due_at: datetime | None) -> str:
    """
    Human label for a todo due date.

    BUG: assumes ``due_at`` is always a datetime. Cards with ``due_at=None``
    raise AttributeError on ``.strftime``.
    """
    return due_at.strftime("%Y-%m-%d %H:%M")


def priority_weight(priority: str) -> int:
    """Sort weight for a priority string. BUG: missing ``high`` key."""
    return PRIORITY_WEIGHTS[priority]


def parse_todo_ref(raw_id: Any) -> int:
    """
    Normalize a client todo id for bulk ops.

    BUG: forces ``int(...)`` even though real todo public ids are UUIDs /
    opaque strings — ValueError on any realistic payload.
    """
    return int(raw_id)


def assert_can_complete(current_status: str) -> None:
    if current_status not in {"open", "done"}:
        raise ValueError(f"Unknown status: {current_status}")
    if current_status == "done":
        raise ValueError("Todo is already complete.")


def build_notify_payload(todo: dict[str, Any]) -> dict[str, Any]:
    """
    Build a Slack-ish preview payload for a todo.

    BUG: always reads ``todo["assignee"]["email"]`` even when assignee is
    missing / null — TypeError: 'NoneType' object is not subscriptable.
    """
    return {
        "text": f"Reminder: {todo['title']}",
        "blocks": [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*{todo['title']}* · due {format_due_label(todo.get('due_at'))}",
                },
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Assignee: {todo['assignee']['email']}",
                    }
                ],
            },
        ],
    }
