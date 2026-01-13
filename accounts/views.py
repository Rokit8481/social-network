from django.views.generic import View, ListView, FormView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import logout, login
from accounts.models import Follow
from posts.models import Post, PostLike
from django.contrib import messages
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from accounts.forms import RegistrationStep1Form, RegistrationStep2Form, CustomAuthenticationForm, UserEditForm
from boards.models import Board
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.messages import get_messages

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

class RegisterStep1View(FormView):
    template_name = 'accounts/register_step1.html'
    form_class = RegistrationStep1Form
    success_url = reverse_lazy('register_step2')

    def form_valid(self, form):
        self.request.session['registration_data'] = form.cleaned_data
        return super().form_valid(form)


class RegisterStep2View(FormView):
    template_name = 'accounts/register_step2.html'
    form_class = RegistrationStep2Form
    success_url = reverse_lazy('login')

    def dispatch(self, request, *args, **kwargs):
        if 'registration_data' not in request.session:
            return redirect('register_step1')
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        action = self.request.POST.get('action')
        data = self.request.session.get('registration_data')

        if action == 'later':
            user = User.objects.create_user(
                username=data['username'],
                email=data['email'],
                password=data['password1']
            )

            self.request.session.pop('registration_data', None)
            login(self.request, user)

            messages.info(self.request, "Your account has been created. You can complete your profile later.")
            return redirect('user_detail', slug=user.slug) 

        user = User.objects.create_user(
            username=data['username'],
            email=data['email'],
            password=data['password1']
        )
        user.first_name = form.cleaned_data.get('first_name')
        user.last_name = form.cleaned_data.get('last_name')
        user.bio = form.cleaned_data.get('bio')
        user.avatar = form.cleaned_data.get('avatar')
        user.mobile = form.cleaned_data.get('mobile')
        user.birthday = form.cleaned_data.get('birthday')
        user.save()

        self.request.session.pop('registration_data', None)
        login(self.request, user)
        return super().form_valid(form)

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
        
        storage = get_messages(request)
        for _ in storage:
            pass

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

        is_following = Follow.objects.filter(
            follower=request.user,
            following=user_detail
        ).exists()

        #POSTS
        posts_qs = Post.objects.filter(author=user_detail).order_by('-created_at')
        posts_paginator = Paginator(posts_qs, 3) 
        posts_page = request.GET.get('posts_page')
        try:
            posts = posts_paginator.page(posts_page)
        except PageNotAnInteger:
            posts = posts_paginator.page(1)
        except EmptyPage:
            posts = posts_paginator.page(posts_paginator.num_pages)

        #BOARDS
        boards_qs = Board.objects.filter(members=user_detail)
        for board in boards_qs:
            board.user_is_member = board.is_member(request.user)
        boards_paginator = Paginator(boards_qs, 6)
        boards_page = request.GET.get('boards_page')
        try:
            user_boards = boards_paginator.page(boards_page)
        except PageNotAnInteger:
            user_boards = boards_paginator.page(1)
        except EmptyPage:
            user_boards = boards_paginator.page(boards_paginator.num_pages)
        
        #LIKED_POSTS
        liked_qs = Post.objects.filter(
        id__in=PostLike.objects.filter(user=user_detail)
            .values_list('post_id', flat=True)
        ).order_by('-created_at')
        liked_paginator = Paginator(liked_qs, 3)
        liked_page = request.GET.get('liked_page')
        try:
            posts_user_liked = liked_paginator.page(liked_page)
        except PageNotAnInteger:
            posts_user_liked = liked_paginator.page(1)
        except EmptyPage:
            posts_user_liked = liked_paginator.page(liked_paginator.num_pages)

        context = {
            "user_detail": user_detail,
            "followers": followers,
            "following": following,
            "followers_count": followers.count(),
            "following_count": following.count(),
            "is_following": is_following,
            "posts": posts,
            "posts_paginator": posts_paginator,
            "user_boards": user_boards,
            "boards_paginator": boards_paginator,
            "posts_user_liked": posts_user_liked,
            "liked_paginator": liked_paginator,
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