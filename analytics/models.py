from django.db import models


class AnalyticsUser(models.Model):
    user_id = models.IntegerField(primary_key=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    educational_institution = models.CharField(max_length=255, blank=True, null=True)
    course = models.IntegerField(blank=True, null=True)
    created_at = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = "users"

    @classmethod
    def from_clickhouse_row(cls, row: dict) -> "AnalyticsUser":
        return cls(
            user_id=row.get("user_id"),
            email=row.get("email"),
            first_name=row.get("first_name"),
            last_name=row.get("last_name"),
            middle_name=row.get("middle_name"),
            phone_number=row.get("phone_number"),
            educational_institution=row.get("educational_institution"),
            course=row.get("course"),
            created_at=row.get("created_at"),
        )


class AnalyticsTicket(models.Model):
    ticket_id = models.IntegerField(primary_key=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    max_points = models.IntegerField(blank=True, null=True)
    question_count = models.IntegerField(blank=True, null=True)
    difficulty = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "tickets"

    @classmethod
    def from_clickhouse_row(cls, row: dict) -> "AnalyticsTicket":
        return cls(
            ticket_id=row.get("ticket_id"),
            subject=row.get("subject"),
            max_points=row.get("max_points"),
            question_count=row.get("question_count"),
            difficulty=row.get("difficulty"),
        )


class AnalyticsAttempt(models.Model):
    attempt_id = models.IntegerField(primary_key=True)
    session_id = models.IntegerField(blank=True, null=True)
    user_id = models.IntegerField(blank=True, null=True)
    ticket_id = models.IntegerField(blank=True, null=True)
    attempt_number = models.IntegerField(blank=True, null=True)
    score_earned = models.IntegerField(blank=True, null=True)
    max_score = models.IntegerField(blank=True, null=True)
    attempt_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "attempts"

    @classmethod
    def from_clickhouse_row(cls, row: dict) -> "AnalyticsAttempt":
        return cls(
            attempt_id=row.get("attempt_id"),
            session_id=row.get("session_id"),
            user_id=row.get("user_id"),
            ticket_id=row.get("ticket_id"),
            attempt_number=row.get("attempt_number"),
            score_earned=row.get("score_earned"),
            max_score=row.get("max_score"),
            attempt_date=row.get("attempt_date"),
        )
