from django.urls import path
from .views import NotificationListView, NotificationMarkReadAPIView, NotificationAPIView

app_name = "notifications"

urlpatterns = [
    path("", NotificationListView.as_view(), name="notifications_list"),
    path("api/", NotificationAPIView.as_view(), name="notifications_api"),
    path("api/<int:pk>/read/", NotificationMarkReadAPIView.as_view(), name="mark_read_api"),
]
