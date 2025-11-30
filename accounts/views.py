from django.views.generic import View, ListView, CreateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from accounts.models import Follow
from posts.models import Post, PostLike
from django.contrib import messages
from accounts.forms import CustomUserCreationForm, CustomAuthenticationForm, UserEditForm
from groups.models import Group
from django.contrib.auth import get_user_model, update_session_auth_hash

User = get_user_model()

class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'
    redirect_authenticated_user = True
    form_class = CustomAuthenticationForm 

class CustomLogoutView(View):
    next_page = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect(self.next_page)

class RegisterView(CreateView):
    model = User
    template_name = 'accounts/register.html'
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users_list')

class UsersListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/users_list.html'
    context_object_name = 'users'
    paginate_by = 10
    login_url = reverse_lazy('login')
    redirect_field_name = 'next'

class EditUserView(LoginRequiredMixin, View):
    template_name = 'accounts/edit_user.html'
    login_url = reverse_lazy('login')
    redirect_field_name = 'next'

    def get(self, request, *args, **kwargs):
        user = request.user
        form = UserEditForm(instance=user)
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        user = request.user
        form = UserEditForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            return redirect('user_detail', slug=user.slug)
        return render(request, self.template_name, {'form': form})

class ChangePasswordView(LoginRequiredMixin, View):
    template_name = 'accounts/change_password.html'

    def get(self, request, slug, *args, **kwargs):
        if request.user.slug != slug:
            return redirect('user_detail', slug=request.user.slug)

        return render(request, self.template_name)

    def post(self, request, slug, *args, **kwargs):
        if request.user.slug != slug:
            return redirect('user_detail', slug=request.user.slug)

        user = request.user

        old_password = request.POST.get("old_password")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")

        if not user.check_password(old_password):
            messages.error(request, "Old password is incorrect.")
            return render(request, self.template_name)
            
        if new_password1 != new_password2:
            messages.error(request, "New passwords do not match.")
            return render(request, self.template_name)

        user.set_password(new_password1)
        user.save()

        update_session_auth_hash(request, user)

        messages.success(request, "Password successfully changed!")
        return redirect('user_detail', slug=user.slug)

class UserDetailView(LoginRequiredMixin, View):
    template_name = 'accounts/user_detail.html'
    login_url = reverse_lazy('login')
    redirect_field_name = 'next'
    slug_url_kwarg = 'slug'

    def get(self, request, *args, **kwargs):
        slug = kwargs.get(self.slug_url_kwarg)
        user_detail = get_object_or_404(User, slug=slug)

        followers = user_detail.followers.all()
        following = user_detail.following.all()
        followers_count = user_detail.followers.count()
        following_count = user_detail.following.count()

        is_following = Follow.objects.filter(
            follower=request.user,
            following=user_detail
        ).exists()

        user_groups = Group.objects.filter(members=user_detail)

        posts_user_liked = Post.objects.filter(
            id__in=PostLike.objects.filter(user=user_detail).values_list('post_id', flat=True)
        ).order_by('-created_at')

        posts = Post.objects.filter(author=user_detail).order_by("-created_at")

        context = {
            "user_detail": user_detail,
            "followers": followers,
            "following": following,
            "posts_user_liked": posts_user_liked,
            "user_groups": user_groups,
            "followers_count": followers_count,
            "following_count": following_count,
            "is_following": is_following,
            "posts": posts,
        }

        return render(request, self.template_name, context)

class ToggleFollowView(LoginRequiredMixin, View):
    login_url = reverse_lazy('login')
    redirect_field_name = 'next'

    def post(self, request, slug, *args, **kwargs):
        user_to_follow = get_object_or_404(User, slug=slug)

        follow_obj = Follow.objects.filter(
            follower=request.user,
            following=user_to_follow
        )

        if follow_obj.exists():
            follow_obj.delete()
        else:
            Follow.objects.create(
                follower=request.user,
                following=user_to_follow
            )

        return redirect("user_detail", slug=slug)