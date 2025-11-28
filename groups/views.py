from django.views.generic import View, DetailView, ListView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from groups.models import Group, GroupMessage, GroupMessageFile, Tag
from django.contrib.auth import get_user_model
from django.http import JsonResponse

User = get_user_model()

class GroupsListView(LoginRequiredMixin, View):
    template_name = "groups/groups_list.html"

    def get(self, request):
        groups = Group.objects.all().order_by("title")
        selected_tags = request.GET.getlist("tag")
        
        if selected_tags:
            groups = groups.filter(tags__name__in=selected_tags).distinct()

        all_tags = Tag.objects.all().order_by('name')
        context = {
            "groups": groups,
            "selected_tags": selected_tags,
            "all_tags": all_tags,
        }
        return render(request, self.template_name, context)


class GroupDetailView(LoginRequiredMixin, View):
    def get(self, request, slug):
        group = get_object_or_404(Group, slug=slug)
        messages = group.messages.all().order_by('created_at')
        tags = group.tags.all()

        context = {
            'group': group,
            'messages': messages,
            'tags': tags,
        }
        return render(request, 'groups/group_detail.html', context)
