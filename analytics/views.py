import json

from django.http import HttpRequest, JsonResponse
from django.views.decorators.csrf import csrf_exempt

from analytics.clickhouse_client import (
    fetch_student_progress,
    insert_student_progress,
)


def healthcheck_view(request: HttpRequest) -> JsonResponse:
    return JsonResponse({"status": "ok"})


def progress_view(request: HttpRequest) -> JsonResponse:
    # читаем текущие строки из clickhouse
    return JsonResponse({"rows": fetch_student_progress()})


@csrf_exempt
def insert_progress_view(request: HttpRequest) -> JsonResponse:
    if request.method != "POST":
        return JsonResponse({"error": "use POST"}, status=405)

    try:
        body = json.loads(request.body.decode("utf-8") or "{}")
        student_id = int(body["student_id"])
        score = float(body["score"])
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        return JsonResponse(
            {"error": "expected json with student_id and score"},
            status=400,
        )

    insert_student_progress(student_id=student_id, score=score)
    return JsonResponse(
        {"status": "ok", "inserted": {"student_id": student_id, "score": score}},
        status=201,
    )
