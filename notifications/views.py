from django.views.generic import ListView, View
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notification


class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        qs = Notification.objects.filter(
            to_user=self.request.user
        ).order_by("-created_at")

        # Автовідмітка прочитаних при відкритті сторінки
        qs.filter(is_read=False).update(is_read=True)

        return qs

class NotificationMarkReadView(LoginRequiredMixin, View):

    def get(self, request, pk, *args, **kwargs):
        notif = Notification.objects.filter(
            pk=pk, to_user=request.user
        ).first()

        if notif:
            notif.is_read = True
            notif.save()

        return redirect("notifications:notifications_list")
