"""Pure helpers used by the complex demo endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Any


PRIORITY_WEIGHTS = {
    "low": 1,
    "medium": 2,
    "high": 3,
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


def velocity_per_day(total_points: int, completed_days: int) -> float:
    """Average story points closed per active day in a sprint window."""
    return total_points / completed_days


def handle_local_part(email: str) -> str:
    """Local part of an email for load charts (before @)."""
    return email.split("@", 1)[0].lower()


def tag_frequency(tags: list[str]) -> dict[str, int]:
    """Count occurrences of each tag label."""
    counts: dict[str, int] = {}
    for tag in tags:
        key = tag.strip().lower()
        counts[key] = counts.get(key, 0) + 1
    return counts


def hex_to_rgb(color: str) -> tuple[int, int, int]:
    """Parse a #RRGGBB color into an RGB tuple."""
    raw = color.lstrip("#")
    return (int(raw[0:2], 16), int(raw[2:4], 16), int(raw[4:6], 16))
