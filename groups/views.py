from django.views.generic import View, DetailView, ListView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from groups.models import Group, GroupMessage, GroupMessageFile, Tag
from groups.forms import EditGroupForm, GroupMessageForm, CreateGroupForm
from django.contrib.auth import get_user_model
from django.db.models import Q
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

        query = request.GET.get("q", "").strip()

        if query:
            keywords = query.split()

            q_object = Q()
            for word in keywords:
                q_object |= Q(title__icontains=word)
                q_object |= Q(description__icontains=word)
                q_object |= Q(tags__name__icontains=word)

            groups = groups.filter(q_object).distinct()

        for group in groups:
            group.user_is_member = group.is_member(request.user)

        context = {
            "groups": groups,
            "query": query,
        }
        return render(request, self.template_name, context)
    
class GroupDetailView(MemberRequiredMixin, View):
    def get(self, request, slug):
        group = get_object_or_404(Group, slug=slug)
        user_is_admin = group.is_admin(request.user)
        user_is_member = group.is_member(request.user)
        messages = group.messages.prefetch_related('files').order_by('-created_at')
        tags = group.tags.all()
        messages_with_files = []
        for msg in messages:
            media_files = [f for f in msg.files.all() if f.is_media]
            attachments = [f for f in msg.files.all() if f.is_attachment]
            messages_with_files.append({
                'message': msg,
                'media_files': media_files,
                'attachments': attachments,
            })

        context = {
            'group': group,
            'messages': messages,
            'user_is_admin': user_is_admin,
            'user_is_member': user_is_member,
            'tags': tags,
            'messages_with_files': messages_with_files,
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
    
class JoinGroupView(LoginRequiredMixin, View):
    def post(self, request, slug, *args, **kwargs):
        group = get_object_or_404(Group, slug=slug)
        group.members.add(request.user)
        return redirect('group_detail', slug=group.slug)

class LeaveGroupView(MemberRequiredMixin, View):
    def post(self, request, slug, *args, **kwargs):
        group = get_object_or_404(Group, slug=slug)
        if group.is_creator(request.user):
            group.delete()
            return redirect('groups_list')

        if group.is_admin(request.user):
            if group.admins.count() <= 1:
                return redirect('group_detail', slug=slug)

            group.admins.remove(request.user)

        group.members.remove(request.user)
        return redirect('groups_list')

class EditGroupMessageAjaxView(AdminRequiredMixin, View):
    form_class = GroupMessageForm

    def post(self, request, slug, message_id, *args, **kwargs):
        group = get_object_or_404(Group, slug=slug)
        message = get_object_or_404(GroupMessage, id=message_id, group=group)
        form = self.form_class(request.POST, request.FILES, instance=message)
        if form.is_valid():
            message = form.save()

            delete_ids = request.POST.getlist("delete_files")
            message.files.filter(id__in=delete_ids).delete()

            for f in request.FILES.getlist("files"):
                GroupMessageFile.objects.create(message=message, file=f)

            return JsonResponse({
                'success': True,
                'message_id': message.id,
                'content': message.content,
                'updated_at': message.updated_at.strftime('%d.%m.%Y %H:%M'),
            })
        return JsonResponse({'success': False, 'errors': form.errors})

class DeleteGroupMessageAjaxView(AdminRequiredMixin, View):
    def post(self, request, slug, message_id, *args, **kwargs):
        group = get_object_or_404(Group, slug=slug)
        message = get_object_or_404(GroupMessage, id=message_id, group=group)
        message.delete()
        return JsonResponse({'success': True, 'message_id': message_id})
    
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

            for f in request.FILES.getlist("files"):
                GroupMessageFile.objects.create(message=message, file=f)

            return JsonResponse({
                'success': True,
                'id': message.id,
                'sender_avatar_url': message.sender.avatar.url,
                'content': message.content,
                'sender': message.sender.username,
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
            })
        return JsonResponse({'success': False, 'errors': form.errors})