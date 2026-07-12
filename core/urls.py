from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views

from analytics.views import (
    analytics_stats_view,
    healthcheck_view,
    user_attempts_view,
    user_stats_view,
)
from analytics.admin_views import (
    home_view,
    dashboard_view,
    admin_panel_view,
)


urlpatterns = [
    path("", home_view, name="home"),
    path("dashboard/", dashboard_view, name="dashboard"),
    path("admin-panel/", admin_panel_view, name="admin_panel"),
    path("admin/", admin.site.urls),
    path("admin/login/", auth_views.LoginView.as_view(template_name="registration/login.html"), name="login"),
    path("admin/logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("health/", healthcheck_view),
    path("analytics/stats/", analytics_stats_view),
    path("analytics/user/<int:user_id>/attempts/", user_attempts_view),
    path("analytics/user/<int:user_id>/stats/", user_stats_view),
]

