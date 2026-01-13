from django.urls import path
from accounts.views import RegisterStep1View, RegisterStep2View, CustomLoginView, \
                           CustomLogoutView, UsersListView, UserDetailView, \
                           EditUserView, ChangePasswordView, ToggleFollowView

urlpatterns = [
    path('register/step1/', RegisterStep1View.as_view(), name='register_step1'),
    path('register/step2/', RegisterStep2View.as_view(), name='register_step2'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', CustomLogoutView.as_view(), name='logout'),
    path('', UsersListView.as_view(), name='users_list'),
    path('user/<slug:slug>/', UserDetailView.as_view(), name='user_detail'),
    path('user/<slug:slug>/edit/', EditUserView.as_view(), name='edit_user'),
    path('user/<slug:slug>/change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('user/<slug:slug>/follow/', ToggleFollowView.as_view(), name='toggle_follow'),
]
