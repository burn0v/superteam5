from typing import Any

from django.db import models

from analytics.serializers import AttemptSerializer, TicketSerializer, UserSerializer


def sync_rows_to_model(model: type[models.Model], rows: list[dict[str, Any]], field_mapping: dict[str, str]) -> int:
    created = 0
    for row in rows:
        lookup_kwargs = {}
        for field_name, source_name in field_mapping.items():
            if field_name in {"user_id", "ticket_id", "attempt_id"}:
                lookup_kwargs[field_name] = row.get(source_name)
        if not lookup_kwargs:
            continue

        obj, was_created = model.objects.update_or_create(defaults={k: row.get(v) for k, v in field_mapping.items()}, **lookup_kwargs)
        if was_created:
            created += 1
    return created


def serialize_payload(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "user": UserSerializer.to_dict(payload["user"])
        if isinstance(payload.get("user"), dict)
        else payload.get("user"),
        "ticket": TicketSerializer.to_dict(payload["ticket"])
        if isinstance(payload.get("ticket"), dict)
        else payload.get("ticket"),
        "attempt": AttemptSerializer.to_dict(payload["attempt"])
        if isinstance(payload.get("attempt"), dict)
        else payload.get("attempt"),
    }
