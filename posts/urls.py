from django.urls import path
from posts.views import PostsListView, ToggleLikeAPI, PostDetailView

urlpatterns = [
    path('', PostsListView.as_view(), name='posts-list'),
    path('api/like/<int:post_pk>/', ToggleLikeAPI.as_view(), name='toggle-like-api'),
    path('post/<int:post_pk>/', PostDetailView.as_view(), name='post-detail'),
]
