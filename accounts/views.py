from django.views.generic import View, ListView, CreateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import logout
from accounts.models import Follow
from accounts.forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import get_user_model

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

        is_following = False
        if request.user.is_authenticated:
            is_following = Follow.objects.filter(
                follower=request.user,
                following=user_detail
            ).exists()

        context = {
            "user_detail": user_detail,
            "followers": followers,
            "following": following,
            "followers_count": followers_count,
            "following_count": following_count,
            "is_following": is_following,
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