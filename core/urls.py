from django.contrib import admin
from django.urls import path

from analytics.views import (
    analytics_stats_view,
    healthcheck_view,
    user_attempts_view,
    user_stats_view,
)


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", healthcheck_view),
    path("analytics/stats/", analytics_stats_view),
    path("analytics/user/<int:user_id>/attempts/", user_attempts_view),
    path("analytics/user/<int:user_id>/stats/", user_stats_view),
]
