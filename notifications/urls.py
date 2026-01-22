from django.urls import path
from notifications.views import NotificationListView, NotificationMarkReadAPIView, \
                                NotificationAPIView, UnreadNotificationsAPI, \
                                UnreadCountAPI, MarkAllReadAPI

app_name = "notifications"

urlpatterns = [
    path("", NotificationListView.as_view(), name="notifications_list"),
    path("api/", NotificationAPIView.as_view(), name="notifications_api"),
    path("api/<int:pk>/read/", NotificationMarkReadAPIView.as_view(), name="mark_read_api"),
    path("api/unread/", UnreadNotificationsAPI.as_view()),
    path("api/unread_count/", UnreadCountAPI.as_view(), name="notifications_unread_count"),
    path("api/mark_all_read/", MarkAllReadAPI.as_view(), name="mark_all_read_api")

]
