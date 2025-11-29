from django.views.generic import View, DetailView, ListView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from groups.models import Group, GroupMessage, GroupMessageFile, Tag
from groups.forms import CreateGroupForm, EditGroupForm, GroupMessageForm
from django.contrib.auth import get_user_model
from django.http import JsonResponse

User = get_user_model()

class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        group = get_object_or_404(Group, slug=kwargs.get('slug'))
        if not group.is_admin(request.user):
            return redirect('groups_list')
        return super().dispatch(request, *args, **kwargs)
    
class MemberRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        group = get_object_or_404(Group, slug=kwargs.get('slug'))
        if not group.is_member(request.user):
            return redirect('groups_list')
        return super().dispatch(request, *args, **kwargs)

class GroupsListView(LoginRequiredMixin, View):
    template_name = "groups/groups_list.html"

    def get(self, request):
        groups = Group.objects.prefetch_related('tags').order_by("title")
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


class GroupDetailView(MemberRequiredMixin, View):
    def get(self, request, slug):
        group = get_object_or_404(Group, slug=slug)
        user_is_admin = group.is_admin(request.user)
        messages = group.messages.all().order_by('-created_at')
        tags = group.tags.all()

        context = {
            'group': group,
            'messages': messages,
            'user_is_admin': user_is_admin,
            'tags': tags,
        }
        return render(request, 'groups/group_detail.html', context)

class CreateGroupView(LoginRequiredMixin, View):
    template_name = "groups/create_group.html"
    form_class = CreateGroupForm
    success_url = reverse_lazy("groups_list")

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            group = form.save(commit=False)
            group.creator = request.user
            group.save()
            form.save_m2m()
            group.add_creator(request.user)
            return redirect(self.success_url)
        return render(request, self.template_name, {"form": form})

class EditGroupView(AdminRequiredMixin, View):
    template_name = "groups/edit_group.html"
    form_class = EditGroupForm
    success_url = reverse_lazy("groups_list")

    def get(self, request, slug, *args, **kwargs):
        group = get_object_or_404(Group, slug=slug)
        form = self.form_class(instance=group)
        return render(request, self.template_name, {"form": form, "group": group})

    def post(self, request, slug, *args, **kwargs):
        group = get_object_or_404(Group, slug=slug)
        form = self.form_class(request.POST, instance=group, user=request.user)
        if form.is_valid():
            group = form.save(commit=False)
            group.save()
            form.save_m2m()

            if request.user not in group.members.all():
                group.members.add(request.user)
            if request.user not in group.admins.all():
                group.admins.add(request.user)

            return redirect(self.success_url)
        return render(request, self.template_name, {"form": form, "group": group})
    
class GroupMessageAjaxView(AdminRequiredMixin, View):
    form_class = GroupMessageForm

    def post(self, request, slug, *args, **kwargs):
        group = get_object_or_404(Group, slug=slug)
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.group = group
            message.sender = request.user
            message.save()

            return JsonResponse({
                'success': True,
                'message_id': message.id,
                'content': message.content,
                'sender': message.sender.username,
                'created_at': message.created_at.strftime('%Y-%m-%d %H:%M'),
            })
        return JsonResponse({'success': False, 'errors': form.errors})