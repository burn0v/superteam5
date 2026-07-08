import os

import clickhouse_connect


def get_clickhouse_client():
    # клиент ходит в clickhouse по http (хост из env или docker-compose)
    host = os.getenv("CLICKHOUSE_HOST", "clickhouse")
    port = int(os.getenv("CLICKHOUSE_PORT", "8123"))

    # В разных запусках clickhouse может быть с разными учетками:
    # - по умолчанию обычно: user=default, pass=""
    # - иногда задают свои: project_user / project_pass
    # Поэтому пробуем варианты, чтобы не ловить "authentication failed".
    username = os.getenv("CLICKHOUSE_USER")
    password = os.getenv("CLICKHOUSE_PASSWORD")

    candidates: list[dict] = []
    if username is not None:
        # если env явно задан — не угадываем, используем его
        candidates.append({"username": username, "password": password or ""})
    else:
        candidates.extend(
            [
                {"username": "default", "password": ""},
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
        except Exception as exc:  # пробуем следующий вариант
            last_exc = exc

    # если все варианты не сработали — отдаём последнее исключение
    assert last_exc is not None
    raise last_exc


def ensure_table() -> None:
    client = get_clickhouse_client()
    client.command(
        """
        CREATE TABLE IF NOT EXISTS student_progress (
            student_id UInt32,
            score Float32
        ) ENGINE = MergeTree()
        ORDER BY student_id
        """
    )
    client.close()


def fetch_student_progress() -> list[dict]:
    ensure_table()
    client = get_clickhouse_client()
    result = client.query(
        "SELECT student_id, score FROM student_progress ORDER BY student_id"
    )
    rows = [
        {"student_id": row[0], "score": row[1]}
        for row in result.result_rows
    ]
    client.close()
    return rows


def insert_student_progress(student_id: int, score: float) -> None:
    ensure_table()
    client = get_clickhouse_client()
    client.insert(
        "student_progress",
        [[student_id, score]],
        column_names=["student_id", "score"],
    )
    client.close()
