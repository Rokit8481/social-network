from django.views.generic import ListView, View
from django.shortcuts import redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notification
from django.http import JsonResponse
from django.views.decorators.http import require_GET
from django.utils.decorators import method_decorator

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/list.html"
    context_object_name = "notifications"

    def get_queryset(self):
        qs = Notification.objects.filter(
            to_user=self.request.user
        ).order_by("-created_at")

        return qs

class NotificationMarkReadAPIView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        Notification.objects.filter(
            pk=pk,
            to_user=request.user
        ).update(is_read=True)

        return JsonResponse({"status": "ok"})

class NotificationAPIView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(
            to_user=request.user
        ).order_by("-created_at")

        data = [
            {
                "id": n.id,
                "message": n.get_message(),
                "is_read": n.is_read,
                "created": n.created_at.strftime("%H:%M %d/%m/%Y"),
            }
            for n in notifications
        ]

        return JsonResponse(data, safe=False)
    
class UnreadCountAPI(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        count = Notification.objects.filter(
            to_user=request.user,
            is_read=False
        ).count()
        return JsonResponse({"count": count})
    
class MarkAllReadAPI(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        Notification.objects.filter(
            to_user=request.user,
            is_read=False
        ).update(is_read=True)

        return JsonResponse({"status": "ok"})
