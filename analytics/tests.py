import os
from unittest.mock import patch

from django.test import SimpleTestCase

from analytics import clickhouse_client
from analytics.clickhouse_client import fetch_dashboard_stats
from analytics.serializers import DashboardStatsSerializer, UserAttemptSerializer


class DashboardStatsTests(SimpleTestCase):
    @patch("analytics.clickhouse_client.clickhouse_connect.get_client")
    def test_get_clickhouse_client_falls_back_to_container_host(self, mock_get_client):
        mock_client = object()
        mock_get_client.side_effect = [mock_client]

        with patch.dict(
            os.environ,
            {"CLICKHOUSE_HOST": "localhost", "CLICKHOUSE_USER": "default"},
            clear=False,
        ):
            client = clickhouse_client.get_clickhouse_client()

        self.assertIs(client, mock_client)
        self.assertEqual(mock_get_client.call_args.kwargs["host"], "localhost")

    @patch("analytics.clickhouse_client.clickhouse_connect.get_client")
    def test_get_clickhouse_client_uses_default_credentials_by_default(self, mock_get_client):
        mock_client = object()
        mock_get_client.return_value = mock_client

        with patch.dict(os.environ, {}, clear=False):
            client = clickhouse_client.get_clickhouse_client()

        self.assertIs(client, mock_client)
        self.assertEqual(mock_get_client.call_args.kwargs["username"], "default")
        self.assertEqual(mock_get_client.call_args.kwargs["password"], "clickhouse")

    def test_dashboard_serializer_exposes_summary_and_flat_metrics(self):
        serializer = DashboardStatsSerializer()
        payload = serializer.to_representation(
            {
                "users_count": 10,
                "tickets_count": 4,
                "attempts_count": 25,
                "active_users_24h": 7,
                "active_users_7d": 9,
                "attempts_last_24h": 11,
                "attempts_last_7d": 20,
                "last_attempt_date": "2026-07-12 10:30:00",
                "avg_score": 35.5,
                "avg_percentage": 0.71,
                "best_score": 50,
                "by_subject": [{"subject": "Math", "attempts_count": 5}],
                "latest_attempts": [{"attempt_id": 1, "user_id": 1}],
            }
        )

        self.assertEqual(payload["summary"]["users_count"], 10)
        self.assertEqual(payload["users_count"], 10)
        self.assertEqual(payload["by_subject"][0]["subject"], "Math")

    def test_user_attempt_serializer_maps_rows_to_api_shape(self):
        serializer = UserAttemptSerializer()
        payload = serializer.to_representation(
            [{"attempt_id": 1, "user_id": 1, "ticket_id": 2, "subject": "Math"}]
        )

        self.assertEqual(payload[0]["attempt_id"], 1)
        self.assertEqual(payload[0]["subject"], "Math")

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
