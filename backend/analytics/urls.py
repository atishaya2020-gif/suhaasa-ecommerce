from django.urls import path

from .views import dashboard_data, track_page_view

urlpatterns = [
    path("track/", track_page_view, name="analytics-track"),
    path("dashboard/", dashboard_data, name="analytics-dashboard"),
]
