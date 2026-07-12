from __future__ import annotations

from typing import Any


class DashboardStatsSerializer:
    """Shape the ClickHouse dashboard payload for the Django views."""

    def to_representation(self, stats: dict[str, Any]) -> dict[str, Any]:
        summary = {
            "users_count": int(stats.get("users_count") or 0),
            "tickets_count": int(stats.get("tickets_count") or 0),
            "attempts_count": int(stats.get("attempts_count") or 0),
            "active_users_24h": int(stats.get("active_users_24h") or 0),
            "active_users_7d": int(stats.get("active_users_7d") or 0),
            "attempts_last_24h": int(stats.get("attempts_last_24h") or 0),
            "attempts_last_7d": int(stats.get("attempts_last_7d") or 0),
            "last_attempt_date": stats.get("last_attempt_date"),
            "avg_score": stats.get("avg_score"),
            "avg_percentage": stats.get("avg_percentage"),
            "best_score": stats.get("best_score"),
        }
        return {
            **summary,
            "summary": summary,
            "by_subject": list(stats.get("by_subject") or []),
            "latest_attempts": list(stats.get("latest_attempts") or []),
        }


class UserAttemptSerializer:
    """Serialize ClickHouse rows into the API shape used by the UI."""

    def to_representation(self, rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
        return [
            {
                "attempt_id": row.get("attempt_id"),
                "user_id": row.get("user_id"),
                "ticket_id": row.get("ticket_id"),
                "subject": row.get("subject"),
                "attempt_number": row.get("attempt_number"),
                "score_earned": row.get("score_earned"),
                "max_score": row.get("max_score"),
                "attempt_date": row.get("attempt_date"),
            }
            for row in rows
        ]


class UserStatsSerializer:
    """Serialize user-level analytics rows into a stable payload."""

    def to_representation(self, user_id: int, rows: list[dict[str, Any]]) -> dict[str, Any]:
        return {
            "user_id": user_id,
            "subjects": [row.get("subject") for row in rows],
            "avg_scores": [row.get("avg_score") for row in rows],
            "percentages": [row.get("avg_percentage") for row in rows],
            "attempts_count": sum(int(row.get("attempts_count") or 0) for row in rows),
            "details": rows,
        }
