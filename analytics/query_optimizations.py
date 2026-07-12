from django.db import connection


def debug_query_count() -> int:
    return len(connection.queries)
