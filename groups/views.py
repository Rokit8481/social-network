from django.views.generic import View, ListView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from groups.models import Group, GroupMessage, GroupMessageFile, Tags
from django.contrib.auth import get_user_model
from django.http import JsonResponse

User = get_user_model()

class GroupsListView(LoginRequiredMixin, ListView):
    model = Group
    template_name = 'groups/groups_list.html'
    context_object_name = 'groups'

    def get_queryset(self):
        return Group.objects.all().order_by('title')
    