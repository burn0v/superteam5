from unittest.mock import patch

from django.test import SimpleTestCase

from analytics.clickhouse_client import fetch_dashboard_stats


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
