from .views import DashboardView, events
from django.urls import path
urlpatterns = [
    path('',DashboardView.as_view(),name='dashboard'),
    path("events/",events  ),
]
