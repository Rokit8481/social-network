from django.views.generic import View, DetailView, ListView, CreateView
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.contrib.auth import logout
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
    success_url = reverse_lazy('login')

class UsersListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'accounts/users_list.html'
    context_object_name = 'users'
    paginate_by = 10
    login_url = reverse_lazy('login')
    redirect_field_name = 'next'
