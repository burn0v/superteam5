from __future__ import annotations

from typing import Any

from analytics.models import AnalyticsAttempt, AnalyticsTicket, AnalyticsUser


class UserSerializer:
    @staticmethod
    def to_dict(instance: AnalyticsUser) -> dict[str, Any]:
        return {
            "user_id": instance.user_id,
            "email": instance.email,
            "first_name": instance.first_name,
            "last_name": instance.last_name,
            "middle_name": instance.middle_name,
            "phone_number": instance.phone_number,
            "educational_institution": instance.educational_institution,
            "course": instance.course,
            "created_at": instance.created_at,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> AnalyticsUser:
        return AnalyticsUser(
            user_id=data.get("user_id"),
            email=data.get("email"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            middle_name=data.get("middle_name"),
            phone_number=data.get("phone_number"),
            educational_institution=data.get("educational_institution"),
            course=data.get("course"),
            created_at=data.get("created_at"),
        )


class TicketSerializer:
    @staticmethod
    def to_dict(instance: AnalyticsTicket) -> dict[str, Any]:
        return {
            "ticket_id": instance.ticket_id,
            "subject": instance.subject,
            "max_points": instance.max_points,
            "question_count": instance.question_count,
            "difficulty": instance.difficulty,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> AnalyticsTicket:
        return AnalyticsTicket(
            ticket_id=data.get("ticket_id"),
            subject=data.get("subject"),
            max_points=data.get("max_points"),
            question_count=data.get("question_count"),
            difficulty=data.get("difficulty"),
        )


class AttemptSerializer:
    @staticmethod
    def to_dict(instance: AnalyticsAttempt) -> dict[str, Any]:
        return {
            "session_id": instance.session_id,
            "attempt_id": instance.attempt_id,
            "user_id": instance.user_id,
            "ticket_id": instance.ticket_id,
            "attempt_number": instance.attempt_number,
            "score_earned": instance.score_earned,
            "max_score": instance.max_score,
            "attempt_date": instance.attempt_date.isoformat() if instance.attempt_date else None,
        }

    @staticmethod
    def from_dict(data: dict[str, Any]) -> AnalyticsAttempt:
        return AnalyticsAttempt(
            session_id=data.get("session_id"),
            attempt_id=data.get("attempt_id"),
            user_id=data.get("user_id"),
            ticket_id=data.get("ticket_id"),
            attempt_number=data.get("attempt_number"),
            score_earned=data.get("score_earned"),
            max_score=data.get("max_score"),
            attempt_date=data.get("attempt_date"),
        )
