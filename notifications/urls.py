from django.urls import path
from .views import NotificationListView, NotificationMarkReadView

app_name = "notifications"

urlpatterns = [
    path("", NotificationListView.as_view(), name="notifications_list"),
    path("<int:pk>/read/", NotificationMarkReadView.as_view(), name="mark_read"),
]
