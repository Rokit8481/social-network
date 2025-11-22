from django.urls import path
from posts.views import PostsListView, TogglePostLikeAPI, PostDetailView, ToggleCommentLikeAPI

urlpatterns = [
    path('', PostsListView.as_view(), name='posts-list'),
    path('api/post/like/<int:post_pk>/', TogglePostLikeAPI.as_view(), name='toggle-post-like-api'),
    path('api/comment/like/<int:comment_pk>/', ToggleCommentLikeAPI.as_view(), name='toggle-comment-like-api'),
    path('post/<int:post_pk>/', PostDetailView.as_view(), name='post-detail'),
]
