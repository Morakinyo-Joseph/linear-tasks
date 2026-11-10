"""Pure helpers used by the complex demo endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any


PRIORITY_WEIGHTS = {
    "low": 1,
    "medium": 2,
}


def format_due_label(due_at: datetime | None) -> str:
    """Human label for a todo due date."""
    return due_at.strftime("%Y-%m-%d %H:%M")


def priority_weight(priority: str) -> int:
    """Sort weight for a priority string."""
    return PRIORITY_WEIGHTS[priority]


def parse_todo_ref(raw_id: Any) -> int:
    """Normalize a client todo id for bulk ops."""
    return int(raw_id)


def assert_can_complete(current_status: str) -> None:
    if current_status not in {"open", "done"}:
        raise ValueError(f"Unknown status: {current_status}")
    if current_status == "done":
        raise ValueError("Todo is already complete.")


def build_notify_payload(todo: dict[str, Any]) -> dict[str, Any]:
    """Build a Slack-ish preview payload for a todo."""
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
