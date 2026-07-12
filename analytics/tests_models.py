from django.test import TestCase

from analytics.models import AnalyticsUser
from analytics.sync import sync_rows_to_model


class SyncToDjangoTablesTests(TestCase):
    def test_sync_rows_to_model_creates_real_django_rows(self):
        rows = [
            {
                "user_id": 7,
                "email": "student@example.com",
                "first_name": "Иван",
                "last_name": "Иванов",
                "middle_name": "Иванович",
                "phone_number": "+79990000000",
                "educational_institution": "IGPT",
                "course": 2,
                "created_at": "10:15:20",
            }
        ]

        sync_rows_to_model(
            AnalyticsUser,
            rows,
            {
                "user_id": "user_id",
                "email": "email",
                "first_name": "first_name",
                "last_name": "last_name",
                "middle_name": "middle_name",
                "phone_number": "phone_number",
                "educational_institution": "educational_institution",
                "course": "course",
                "created_at": "created_at",
            },
        )

        self.assertEqual(AnalyticsUser.objects.count(), 1)
        self.assertEqual(AnalyticsUser.objects.get(user_id=7).email, "student@example.com")
