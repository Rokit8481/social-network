from django.views.generic import ListView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Notification
from django.http import JsonResponse
from django.core.paginator import Paginator

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = "notifications/list.html"
    context_object_name = "notifications"
    paginate_by = 5

    def get_queryset(self):
        qs = Notification.objects.filter(
            to_user=self.request.user
        ).order_by("-created_at")

        q = self.request.GET.get("q")
        if q:
            qs = qs.filter(message__icontains=q)

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
        notifications = Notification.objects.filter(to_user=request.user).order_by("-created_at")
        paginator = Paginator(notifications, 7)  
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        data = [
            {
                "id": n.id,
                "message": n.get_message(),
                "target_url": n.target_url or "",
                "is_read": n.is_read,
                "created": n.created_at.strftime("%H:%M %d/%m/%Y"),
            }
            for n in page_obj
        ]

        return JsonResponse({
            "results": data,
            "page": page_obj.number,
            "num_pages": paginator.num_pages
        })

class UnreadNotificationsAPI(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        notifications = Notification.objects.filter(
            to_user=request.user,
            is_read=False
        ).order_by("-created_at")[:99]

        data = [
            {
                "id": n.id,
                "message": n.get_message(),
                "target_url": n.target_url or "",
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
