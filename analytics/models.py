from django.db import models


class AnalyticsUser(models.Model):
    user_id = models.IntegerField(unique=True)
    email = models.EmailField(blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    middle_name = models.CharField(max_length=255, blank=True, null=True)
    phone_number = models.CharField(max_length=255, blank=True, null=True)
    educational_institution = models.CharField(max_length=255, blank=True, null=True)
    course = models.IntegerField(default=0)
    created_at = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        app_label = "analytics"


class AnalyticsTicket(models.Model):
    ticket_id = models.IntegerField(unique=True)
    subject = models.CharField(max_length=255, blank=True, null=True)
    max_points = models.IntegerField(default=0)
    question_count = models.IntegerField(default=0)
    difficulty = models.IntegerField(default=0)

    class Meta:
        app_label = "analytics"


class AnalyticsAttempt(models.Model):
    session_id = models.IntegerField(default=0)
    attempt_id = models.IntegerField(unique=True)
    user_id = models.IntegerField(default=0)
    ticket_id = models.IntegerField(default=0)
    attempt_number = models.IntegerField(default=0)
    score_earned = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    attempt_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        app_label = "analytics"
