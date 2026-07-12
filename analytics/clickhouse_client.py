import os

import clickhouse_connect


def get_clickhouse_client():
    # клиент ходит в clickhouse по http (хост из env или docker-compose)
    host = os.getenv("CLICKHOUSE_HOST")
    if not host:
        host = "localhost"
    port = int(os.getenv("CLICKHOUSE_PORT", "8123"))

    username = os.getenv("CLICKHOUSE_USER")
    password = os.getenv("CLICKHOUSE_PASSWORD")

    candidates: list[dict] = []
    if username is not None:
        candidates.append({"username": username, "password": password or ""})
    else:
        candidates.extend(
            [
                {"username": "default", "password": ""},
                {"username": "default", "password": "default"},
                {"username": "project_user", "password": "project_pass"},
            ]
        )

    last_exc: Exception | None = None
    for cand in candidates:
        try:
            return clickhouse_connect.get_client(
                host=host,
                port=port,
                username=cand["username"],
                password=cand["password"],
            )
        except Exception as exc:
            last_exc = exc

    assert last_exc is not None
    raise last_exc


def _query_rows(sql: str, params: dict | None = None) -> list[dict]:
    client = get_clickhouse_client()
    result = client.query(sql, parameters=params or {})
    columns = result.column_names
    rows = [dict(zip(columns, row)) for row in result.result_rows]
    client.close()
    return rows


def fetch_pipeline_counts() -> dict:
    # сколько строк уже дошло из kafka в clickhouse
    rows = _query_rows(
        """
        SELECT
            (SELECT count() FROM users) AS users,
            (SELECT count() FROM tickets) AS tickets,
            (SELECT count() FROM attempts) AS attempts
        """
    )
    return rows[0] if rows else {"users": 0, "tickets": 0, "attempts": 0}


def fetch_dashboard_stats() -> dict:
    metrics_rows = _query_rows(
        """
        SELECT
            count(DISTINCT user_id) AS users_count,
            (SELECT count() FROM tickets) AS tickets_count,
            count() AS attempts_count,
            count(DISTINCT if(attempt_date >= now() - INTERVAL 1 DAY, user_id, NULL)) AS active_users_24h,
            count(DISTINCT if(attempt_date >= now() - INTERVAL 7 DAY, user_id, NULL)) AS active_users_7d,
            countIf(attempt_date >= now() - INTERVAL 1 DAY) AS attempts_last_24h,
            countIf(attempt_date >= now() - INTERVAL 7 DAY) AS attempts_last_7d,
            max(attempt_date) AS last_attempt_date,
            round(avg(score_earned), 2) AS avg_score,
            round(avg(score_earned / nullIf(max_score, 0)), 2) AS avg_percentage,
            max(score_earned) AS best_score
        FROM attempts
        """
    )
    metrics = metrics_rows[0] if metrics_rows else {}

    dashboard_rows = _query_rows(
        """
        SELECT
            t.subject AS subject,
            count() AS attempts_count,
            round(avg(a.score_earned), 2) AS avg_score,
            round(avg(a.score_earned / nullIf(a.max_score, 0)), 2) AS avg_percentage,
            a.attempt_id,
            a.user_id,
            a.ticket_id,
            a.attempt_number,
            a.score_earned,
            a.max_score,
            a.attempt_date
        FROM attempts AS a
        LEFT JOIN tickets AS t ON a.ticket_id = t.ticket_id
        GROUP BY
            t.subject,
            a.attempt_id,
            a.user_id,
            a.ticket_id,
            a.attempt_number,
            a.score_earned,
            a.max_score,
            a.attempt_date
        ORDER BY a.attempt_date DESC
        LIMIT 10
        """
    )

    by_subject_rows = []
    latest_attempts_rows = []
    for row in dashboard_rows:
        by_subject_rows.append(
            {
                "subject": row.get("subject"),
                "attempts_count": row.get("attempts_count"),
                "avg_score": row.get("avg_score"),
                "avg_percentage": row.get("avg_percentage"),
            }
        )
        latest_attempts_rows.append(
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
        )

    return {
        "users_count": int(metrics.get("users_count") or 0),
        "tickets_count": int(metrics.get("tickets_count") or 0),
        "attempts_count": int(metrics.get("attempts_count") or 0),
        "active_users_24h": int(metrics.get("active_users_24h") or 0),
        "active_users_7d": int(metrics.get("active_users_7d") or 0),
        "attempts_last_24h": int(metrics.get("attempts_last_24h") or 0),
        "attempts_last_7d": int(metrics.get("attempts_last_7d") or 0),
        "last_attempt_date": metrics.get("last_attempt_date"),
        "avg_score": metrics.get("avg_score"),
        "avg_percentage": metrics.get("avg_percentage"),
        "best_score": metrics.get("best_score"),
        "by_subject": by_subject_rows,
        "latest_attempts": latest_attempts_rows,
    }


def fetch_user_attempts(user_id: int) -> list[dict]:
    return _query_rows(
        """
        SELECT
            a.attempt_id,
            a.user_id,
            a.ticket_id,
            t.subject,
            a.attempt_number,
            a.score_earned,
            a.max_score,
            a.attempt_date
        FROM attempts AS a
        LEFT JOIN tickets AS t ON a.ticket_id = t.ticket_id
        WHERE a.user_id = {user_id:UInt32}
        ORDER BY a.attempt_date DESC
        LIMIT 100
        """,
        {"user_id": user_id},
    )


def fetch_user_stats(user_id: int) -> dict:
    rows = _query_rows(
        """
        SELECT
            t.subject AS subject,
            round(avg(a.score_earned), 2) AS avg_score,
            round(avg(a.score_earned / nullIf(a.max_score, 0)), 2) AS avg_percentage,
            count() AS attempts_count
        FROM attempts AS a
        INNER JOIN tickets AS t ON a.ticket_id = t.ticket_id
        WHERE a.user_id = {user_id:UInt32}
        GROUP BY t.subject
        ORDER BY t.subject
        """,
        {"user_id": user_id},
    )

    return {
        "user_id": user_id,
        "subjects": [row["subject"] for row in rows],
        "avg_scores": [row["avg_score"] for row in rows],
        "percentages": [row["avg_percentage"] for row in rows],
        "attempts_count": sum(row["attempts_count"] for row in rows),
        "details": rows,
    }
