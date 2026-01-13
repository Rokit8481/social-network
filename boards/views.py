from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from boards.models import Board, BoardMessage, Tag
from boards.forms import EditBoardForm, CreateBoardMessageForm, CreateBoardForm
from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.template.loader import render_to_string
from django.http import JsonResponse

User = get_user_model()

class AdminRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        board = get_object_or_404(Board, slug=kwargs.get('slug'))
        if not board.is_admin(request.user):
            return redirect('boards_list')
        return super().dispatch(request, *args, **kwargs)
    
class MemberRequiredMixin(LoginRequiredMixin):
    def dispatch(self, request, *args, **kwargs):
        board = get_object_or_404(Board, slug=kwargs.get('slug'))
        if not board.is_member(request.user):
            return redirect('boards_list')
        return super().dispatch(request, *args, **kwargs)

class BoardsListView(LoginRequiredMixin, View):
    template_name = "boards/boards_list.html"

    def get(self, request):
        query = request.GET.get("q", "").strip()

        boards_qs = (
            Board.objects
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

            boards_qs = boards_qs.filter(q_object).distinct()
            
        boards = boards_qs[:9]

        for board in boards:
            board.user_is_member = board.is_member(request.user)

        context = {
            "boards": boards,
            "query": query,
        }
        return render(request, self.template_name, context)
    
class BoardDetailView(MemberRequiredMixin, View):
    def get(self, request, slug):
        board = get_object_or_404(Board, slug=slug)
        user_is_admin = board.is_admin(request.user)
        user_is_member = board.is_member(request.user)
        board_messages = (board.messages.order_by('-id')[:10])
        tags = board.tags.all()

        context = {
            'board': board,
            'board_messages': board_messages,
            'user_is_admin': user_is_admin,
            'user_is_member': user_is_member,
            'tags': tags,
        }
        return render(request, 'boards/board_detail.html', context)

class CreateBoardView(LoginRequiredMixin, View):
    template_name = "boards/create_board.html"
    form_class = CreateBoardForm
    success_url = reverse_lazy("boards_list")

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        if form.is_valid():
            board = form.save(commit=False)
            board.creator = request.user
            board.save()
            form.save_m2m()

            board.add_creator(request.user)

            return redirect(self.success_url)

        return render(request, self.template_name, {"form": form})
    
class EditBoardView(AdminRequiredMixin, View):
    template_name = "boards/edit_board.html"
    form_class = EditBoardForm
    success_url = reverse_lazy("boards_list")

    def get(self, request, slug, *args, **kwargs):
        board = get_object_or_404(Board, slug=slug)
        form = self.form_class(instance=board)
        return render(request, self.template_name, {"form": form, "board": board})

    def post(self, request, slug, *args, **kwargs):
        board = get_object_or_404(Board, slug=slug)
        form = self.form_class(request.POST, instance=board, user=request.user)
        if form.is_valid():
            board = form.save(commit=False)
            board.save()
            form.save_m2m()

            for admin in board.admins.all():
                if admin not in board.members.all():
                    board.members.add(admin)

            if request.user not in board.members.all():
                board.members.add(request.user)
            if request.user not in board.admins.all():
                board.admins.add(request.user)

            return redirect(self.success_url)
        return render(request, self.template_name, {"form": form, "board": board})
    
class JoinBoardView(LoginRequiredMixin, View):
    def post(self, request, slug, *args, **kwargs):
        board = get_object_or_404(Board, slug=slug)
        board.members.add(request.user)
        return redirect('board_detail', slug=board.slug)

class LeaveBoardView(MemberRequiredMixin, View):
    def post(self, request, slug, *args, **kwargs):
        board = get_object_or_404(Board, slug=slug)
        if board.is_creator(request.user):
            board.delete()
            return redirect('boards_list')

        if board.is_admin(request.user):
            if board.admins.count() <= 1:
                return redirect('board_detail', slug=slug)

            board.admins.remove(request.user)

        board.members.remove(request.user)
        return redirect('boards_list')

class EditBoardMessageAjaxView(AdminRequiredMixin, View):
    form_class = CreateBoardMessageForm

    def post(self, request, slug, message_id, *args, **kwargs):
        board = get_object_or_404(Board, slug=slug)
        board_message = get_object_or_404(BoardMessage, id=message_id, board=board)
        form = self.form_class(request.POST, instance=board_message)
        if form.is_valid():
            board_message = form.save()

            return JsonResponse({
                'success': True,
                'board_message_id': board_message.id,
                'content': board_message.content,
                'updated_at': board_message.updated_at.strftime('%d.%m.%Y %H:%M'),
            })
        return JsonResponse({'success': False, 'errors': form.errors})

class DeleteBoardMessageAjaxView(AdminRequiredMixin, View):
    def post(self, request, slug, message_id, *args, **kwargs):
        board = get_object_or_404(Board, slug=slug)
        board_message = get_object_or_404(BoardMessage, id=message_id, board=board)
        board_message.delete()
        return JsonResponse({'success': True, 'message_id': message_id})
    
class BoardMessageAjaxView(AdminRequiredMixin, View):
    form_class = CreateBoardMessageForm

    def post(self, request, slug, *args, **kwargs):
        board = get_object_or_404(Board, slug=slug)
        form = self.form_class(request.POST)
        if form.is_valid():
            board_message = form.save(commit=False)
            board_message.board = board
            board_message.sender = request.user
            board_message.save()

            return JsonResponse({
                'success': True,
                'id': board_message.id,
                'sender_avatar_url': board_message.sender.avatar.url,
                'content': board_message.content,
                'sender': board_message.sender.username,
                'created_at': board_message.created_at.strftime('%d.%m.%Y %H:%M'),
            })
        return JsonResponse({'success': False, 'errors': form.errors})
    
class BoardsInfiniteAPI(LoginRequiredMixin, View):
    def get(self, request):
        last_id = request.GET.get("last_id")
        query = request.GET.get("q", "").strip()

        qs = (
            Board.objects
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

        boards = list(qs[:9])

        for board in boards:
                board.user_is_member = board.is_member(request.user)

        html = render_to_string(
            "helpers/partials/boards_list.html",
            {"boards": boards},
            request=request
        )

        return JsonResponse({
            "html": html,
            "has_more": len(boards) == 9
        })
    

class BoardMessagesInfiniteAPI(MemberRequiredMixin, View):
    def get(self, request, slug):
        board = get_object_or_404(Board, slug=slug)
        last_id = request.GET.get("last_id")

        qs = (
            BoardMessage.objects
            .filter(board=board)
            .select_related("sender")
            .order_by('-id')
        )

        if last_id:
            qs = qs.filter(id__lt=last_id)

        board_messages = list(qs[:10])


        html = render_to_string(
            "helpers/partials/board_messages_list.html",
            {"board_messages": board_messages},
            request=request
        )

        return JsonResponse({
            "html": html,
            "has_more": len(board_messages) == 10
        })