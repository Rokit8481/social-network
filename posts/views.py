from django.views.generic import View
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from posts.models import Post, PostLike, Comment, CommentLike, File
from posts.forms import PostForm, CommentForm
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.db.models import Count
from django.template.loader import render_to_string
import json

User = get_user_model()

class PostsListView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        posts = Post.objects.annotate(likes_count=Count("likes")).order_by("-id")[:5]

        form = PostForm()
        return render(request, 'posts/posts_list.html', {
            'posts': posts,
            'form': form
        })

class CreatePostView(LoginRequiredMixin, View):
    form_class = PostForm
    template_name = 'posts/post_create.html'
    
    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            form.save_m2m()
            
            for f in request.FILES.getlist('files'):
                File.objects.create(post=post, file=f)
            return redirect('post_detail', post_pk=post.pk)
        
        return render(request, self.template_name, {'form': form})

class TogglePostLikeAPI(LoginRequiredMixin, View):
    def post(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        like, created = PostLike.objects.get_or_create(user=request.user, post=post)

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        return JsonResponse({
            'liked': liked,
            'likes_count': post.likes.count()
        })
    
class ToggleCommentLikeAPI(LoginRequiredMixin, View):
    def post(self, request, comment_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)
        like, created = CommentLike.objects.get_or_create(user=request.user, comment=comment)

        if not created:
            like.delete()
            liked = False
        else:
            liked = True

        return JsonResponse({
            'liked': liked,
            'likes_count': comment.likes.count()
        })

class PostDetailView(LoginRequiredMixin, View):
    def get(self, request, post_pk):
        post = get_object_or_404(Post.objects.prefetch_related("files"), pk=post_pk)

        liked_by_user = PostLike.objects.filter(post=post, user=request.user).exists()
        likes_count = post.likes.count()

        viewed = post.viewers.filter(id=request.user.id).exists()
        if not viewed:
            post.viewers.add(request.user)
        viewers_count = post.viewers.count()

        comments = post.comments.all().select_related("user")

        media_files = [f for f in post.files.all() if f.is_media]
        attachments = [f for f in post.files.all() if f.is_attachment]

        comment_form = CommentForm()

        return render(request, 'posts/post_detail.html', {
            'post': post,
            'liked_by_user': liked_by_user,
            'likes_count': likes_count,
            'viewers_count': viewers_count,
            'media_files': media_files,
            'attachments':attachments,
            'comments': comments,
            'comment_form': comment_form,
        })

    def post(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        form = CommentForm(request.POST)

        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.user = request.user
            new_comment.post = post
            new_comment.save()
            return redirect('post_detail', post_pk=post.pk)

        comments = post.comments.all()
        liked_by_user = PostLike.objects.filter(post=post, user=request.user).exists()

        return render(request, 'posts/post_detail.html', {
            'post': post,
            'liked_by_user': liked_by_user,
            'likes_count': post.likes.count(),
            'viewers_count': post.viewers.count(),
            'comments': comments,
            'comment_form': form,
        })


class PostEditView(LoginRequiredMixin, View):
    model = Post
    template_name = "posts/post_edit.html"
    form_class = PostForm
    
    def get(self, request, post_pk, *args, **kwargs):
        post = get_object_or_404(self.model, pk=post_pk)

        if post.author != request.user:
            raise PermissionDenied

        form = self.form_class(instance=post)
        return render(request, self.template_name, {"form": form, "post": post})
    
    def post(self, request, post_pk, *args, **kwargs):
        post = get_object_or_404(self.model, pk=post_pk, author=request.user)
        form = self.form_class(request.POST, request.FILES, instance=post)
        if form.is_valid():
            post = form.save(commit=False)
            post.save()
            form.save_m2m()

            delete_ids = request.POST.getlist("delete_files")
            post.files.filter(id__in=delete_ids).delete()

            for f in request.FILES.getlist("files"):
                File.objects.create(post=post, file=f)
            
            return redirect('post_detail', post_pk=post_pk)
        return render(request, self.template_name, {"form": form, "post": post})

class PostDeleteView(LoginRequiredMixin, View):
    def post(self, request, post_pk):
        post = get_object_or_404(Post, pk=post_pk)
        
        if post.author != request.user:
            raise PermissionDenied
        
        post.delete()
        return redirect('posts_list')
    
class CommentDeleteView(LoginRequiredMixin, View):
    def post(self, request, comment_pk, post_pk):
        comment = get_object_or_404(Comment, pk=comment_pk)

        if comment.user != request.user:
            raise PermissionDenied

        comment.delete()
        return redirect('post_detail', post_pk=post_pk)


class CommentEditView(LoginRequiredMixin, View):
    def post(self, request, comment_pk, *args, **kwargs):
        comment = get_object_or_404(Comment, pk=comment_pk, user=request.user)
        data = json.loads(request.body)
        content = data.get("content")

        if not content or not content.strip():
            return JsonResponse({
                "success": False,
                "error": "Порожнє повідомлення"
            }, status=400)
        
        comment.content = content
        comment.save()

        return JsonResponse({
            "success": True,
            "comment": {
                "id": comment.pk,
                "content": comment.content,
                "created_at": comment.created_at.strftime("%d-%m-%Y %H:%M"),
                "updated_at": comment.updated_at.strftime("%d-%m-%Y %H:%M"),
            }
        })
    
class PostsInfiniteAPI(LoginRequiredMixin, View):
    def get(self, request):
        last_id = request.GET.get("last_id")

        qs = Post.objects \
            .select_related("author") \
            .prefetch_related("files", "people_tags") \
            .annotate(likes_count=Count("likes")) \
            .order_by("-id")

        if last_id:
            qs = qs.filter(id__lt=last_id)

        posts = list(qs[:5])

        html = render_to_string(
            "helpers/partials/posts_list.html",
            {"posts": posts},
            request=request
        )

        return JsonResponse({
            "html": html,
            "has_more": len(posts) == 5
        })