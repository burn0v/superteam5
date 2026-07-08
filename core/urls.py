from django.contrib import admin
from django.urls import path

from analytics.views import healthcheck_view, insert_progress_view, progress_view


urlpatterns = [
    path("admin/", admin.site.urls),
    path("health/", healthcheck_view),
    path("progress/", progress_view),
    path("progress/insert/", insert_progress_view),
]
