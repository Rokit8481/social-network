from django.urls import path
from posts.views import PostsMainView, ToggleLikeView

urlpatterns = [
    path('', PostsMainView.as_view(), name='main'),
    path('like/<int:pk>/', ToggleLikeView.as_view(), name='toggle-like'),
]
