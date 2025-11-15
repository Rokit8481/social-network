from django.urls import path
from accounts.views import *

urlpatterns = [
    path('register/', RegisterView.as_view() , name='register'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', UsersListView.as_view(), name='users_list'),
    path('profile/<slug:slug>/', UserDetailView.as_view(), name='user_detail'),
]
