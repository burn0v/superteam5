from unittest.mock import patch

from django.test import SimpleTestCase

from analytics.clickhouse_client import fetch_dashboard_stats
from analytics.kafka_consumer import build_clickhouse_rows


class DashboardStatsTests(SimpleTestCase):
    @patch("analytics.clickhouse_client._query_rows")
    def test_fetch_dashboard_stats_returns_dashboard_shape(self, mock_query_rows):
        mock_query_rows.side_effect = [
            [
                {
                    "users_count": 10,
                    "tickets_count": 4,
                    "attempts_count": 25,
                    "active_users_24h": 7,
                    "active_users_7d": 9,
                    "last_attempt_date": "2026-07-12 10:30:00",
                    "avg_score": 35.5,
                    "avg_percentage": 0.71,
                    "best_score": 50,
                }
            ],
            [
                {
                    "subject": "Mathematics",
                    "attempts_count": 10,
                    "avg_score": 30.5,
                    "avg_percentage": 0.61,
                }
            ],
            [
                {
                    "attempt_id": 1,
                    "user_id": 1,
                    "ticket_id": 1,
                    "subject": "Mathematics",
                    "attempt_number": 2,
                    "score_earned": 25,
                    "max_score": 50,
                    "attempt_date": "2026-07-12 10:30:00",
                }
            ],
        ]

        stats = fetch_dashboard_stats()

        self.assertEqual(stats["users_count"], 10)
        self.assertEqual(stats["tickets_count"], 4)
        self.assertEqual(stats["attempts_count"], 25)
        self.assertEqual(stats["active_users_24h"], 7)
        self.assertEqual(stats["active_users_7d"], 9)
        self.assertEqual(stats["avg_score"], 35.5)
        self.assertEqual(stats["avg_percentage"], 0.71)
        self.assertEqual(stats["best_score"], 50)
        self.assertEqual(stats["by_subject"][0]["subject"], "Mathematics")
        self.assertEqual(stats["latest_attempts"][0]["attempt_id"], 1)


class KafkaConsumerTests(SimpleTestCase):
    def test_build_clickhouse_rows_extracts_nested_payload(self):
        payload = {
            "user": {
                "user_id": 7,
                "email": "student@example.com",
                "first_name": "Иван",
                "last_name": "Иванов",
                "middle_name": "Иванович",
                "phone_number": "+79990000000",
                "educational_institution": "IGPT",
                "course": 2,
                "created_at": "10:15:20",
            },
            "ticket": {
                "ticket_id": 3,
                "subject": "Programming",
                "max_points": 50,
                "question_count": 5,
                "difficulty": 8,
            },
            "attempt": {
                "attemptId": 11,
                "userId": 7,
                "ticketId": 3,
                "attemptNumber": 4,
                "scoreEarned": 45,
                "maxScore": 50,
                "attemptDate": "12.07.2026;14:22:00",
                "sessionId": 22,
            },
        }

        rows = build_clickhouse_rows(payload)

        self.assertEqual(rows["users"][0]["user_id"], 7)
        self.assertEqual(rows["tickets"][0]["subject"], "Programming")
        self.assertEqual(rows["attempts"][0]["attempt_id"], 11)
        self.assertEqual(rows["attempts"][0]["attempt_date"].year, 2026)
