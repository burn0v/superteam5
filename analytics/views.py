from django.http import HttpRequest, JsonResponse

from analytics.clickhouse_client import (
    fetch_dashboard_stats,
    fetch_user_attempts,
    fetch_user_stats,
)


def healthcheck_view(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})


def analytics_stats_view(request: HttpRequest) -> JsonResponse:
    return JsonResponse(fetch_dashboard_stats())


def user_attempts_view(request: HttpRequest, user_id: int) -> JsonResponse:
    return JsonResponse(
        {
            "user_id": user_id,
            "attempts": fetch_user_attempts(user_id),
        }
    )


def user_stats_view(request: HttpRequest, user_id: int) -> JsonResponse:
    # аналитика по предметам для пользователя (как на схеме пайплайна)
    return JsonResponse(fetch_user_stats(user_id))
