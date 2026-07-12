from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpRequest
from django.shortcuts import render
from django.views.decorators.http import require_http_methods

from analytics.clickhouse_client import fetch_dashboard_stats, fetch_user_stats


def is_admin(user):
    return user.is_staff or user.is_superuser


@require_http_methods(["GET"])
def home_view(request: HttpRequest):
    """Главная страница сервиса"""
    context = {
        "title": "Eduanalist - Подготовка к экзаменам",
        "description": "Интерактивный сервис для подготовки к экзаменам по билетам с аналитикой",
    }
    return render(request, "home.html", context)


@require_http_methods(["GET"])
def dashboard_view(request: HttpRequest):
    """Дашборд с общей статистикой"""
    try:
        stats = fetch_dashboard_stats()
    except Exception as e:
        stats = {}
        error = str(e)
        return render(request, "dashboard.html", {"error": error, "stats": stats})

    context = {
        "title": "Дашборд статистики",
        "stats": stats,
    }
    return render(request, "dashboard.html", context)


@login_required
@user_passes_test(is_admin)
@require_http_methods(["GET"])
def admin_panel_view(request: HttpRequest):
    """ЛК администратора"""
    try:
        stats = fetch_dashboard_stats()
    except Exception as e:
        stats = {}
        error = str(e)
        return render(request, "admin_panel.html", {"error": error, "user": request.user})

    context = {
        "title": "Панель администратора",
        "stats": stats,
        "user": request.user,
    }
    return render(request, "admin_panel.html", context)
