from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from groups.models import Group, GroupMessage, Tag
from groups.forms import EditGroupForm, GroupMessageForm, CreateGroupForm
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.template.loader import render_to_string
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
        query = request.GET.get("q", "").strip()

        groups_qs = (
            Group.objects
            .prefetch_related('tags')
            .order_by("-id")
        )

        if query:
            keywords = query.split()
            q_object = Q()
            for word in keywords:
                q_object |= Q(title__icontains=word)
                q_object |= Q(description__icontains=word)
                q_object |= Q(tags__name__icontains=word)

            groups_qs = groups_qs.filter(q_object).distinct()
            
        groups = groups_qs[:9]

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
        group_messages = (group.messages.order_by('-id')[:10])
        tags = group.tags.all()

        context = {
            'group': group,
            'group_messages': group_messages,
            'user_is_admin': user_is_admin,
            'user_is_member': user_is_member,
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
        form = self.form_class(request.POST, instance=message)
        if form.is_valid():
            message = form.save()

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
        form = self.form_class(request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.group = group
            message.sender = request.user
            message.save()

            return JsonResponse({
                'success': True,
                'id': message.id,
                'sender_avatar_url': message.sender.avatar.url,
                'content': message.content,
                'sender': message.sender.username,
                'created_at': message.created_at.strftime('%d.%m.%Y %H:%M'),
            })
        return JsonResponse({'success': False, 'errors': form.errors})
    
class GroupsInfiniteAPI(LoginRequiredMixin, View):
    def get(self, request):
        last_id = request.GET.get("last_id")
        query = request.GET.get("q", "").strip()

        qs = (
            Group.objects
            .select_related("creator")
            .prefetch_related("tags")
            .annotate(messages_count=Count("messages"))
            .order_by("-id")
        )

        if query:
            keywords = query.split()
            q_object = Q()
            for word in keywords:
                q_object |= Q(title__icontains=word)
                q_object |= Q(description__icontains=word)
                q_object |= Q(tags__name__icontains=word)

            qs = qs.filter(q_object).distinct()

        if last_id:
            qs = qs.filter(id__lt=last_id)

        groups = list(qs[:9])

        for group in groups:
                group.user_is_member = group.is_member(request.user)

        html = render_to_string(
            "helpers/partials/groups_list.html",
            {"groups": groups},
            request=request
        )

        return JsonResponse({
            "html": html,
            "has_more": len(groups) == 9
        })
    

class GroupMessagesInfiniteAPI(MemberRequiredMixin, View):
    def get(self, request, slug):
        group = get_object_or_404(Group, slug=slug)
        last_id = request.GET.get("last_id")

        qs = (
            GroupMessage.objects
            .filter(group=group)
            .select_related("sender")
            .order_by('-id')
        )

        if last_id:
            qs = qs.filter(id__lt=last_id)

        group_messages = list(qs[:10])


        html = render_to_string(
            "helpers/partials/group_messages_list.html",
            {"group_messages": group_messages},
            request=request
        )

        return JsonResponse({
            "html": html,
            "has_more": len(group_messages) == 10
        })