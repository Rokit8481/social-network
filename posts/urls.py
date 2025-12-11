from django.urls import path
from posts.views import PostsListView, TogglePostLikeAPI, PostDetailView, ToggleCommentLikeAPI, PostEditView, PostDeleteView, CommentDeleteView

urlpatterns = [
    path('', PostsListView.as_view(), name='posts-list'),
    path('api/post/like/<int:post_pk>/', TogglePostLikeAPI.as_view(), name='toggle-post-like-api'),
    path('api/comment/like/<int:comment_pk>/', ToggleCommentLikeAPI.as_view(), name='toggle-comment-like-api'),
    path('post/<int:post_pk>/', PostDetailView.as_view(), name='post-detail'),
    path("post/<int:post_pk>/edit", PostEditView.as_view(), name="post_edit"),
    path("post/<int:post_pk>/delete", PostDeleteView.as_view(), name="post_delete"),
    path("post/<int:post_pk>/comment/<int:comment_pk>/delete", CommentDeleteView.as_view(), name="comment_delete"),
]
