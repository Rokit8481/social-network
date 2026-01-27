from django.urls import path
from posts.views import PostsListView, TogglePostLikeAPI, \
                        PostDetailView, ToggleCommentLikeAPI, \
                        PostEditView, PostDeleteView, \
                        CommentDeleteView, CommentEditView, CreatePostView, PostsInfiniteAPI, CommentMessagesInfiniteAPI

urlpatterns = [
    path('', PostsListView.as_view(), name='posts_list'),
    path("infinite/", PostsInfiniteAPI.as_view(), name="posts-infinite"),
    path("create/", CreatePostView.as_view(), name="post_create"),
    path("<int:post_pk>/", PostDetailView.as_view(), name='post_detail'),
    path("<int:post_pk>/infinite/", CommentMessagesInfiniteAPI.as_view(), name="posts_comments_infinite"),
    path("<int:post_pk>/edit", PostEditView.as_view(), name="post_edit"),
    path("<int:post_pk>/delete", PostDeleteView.as_view(), name="post_delete"),
    path('api/post/like/<int:post_pk>/', TogglePostLikeAPI.as_view(), name='toggle-post-like-api'),
    path("comment/<int:comment_pk>/edit/", CommentEditView.as_view(), name="comment_edit"),
    path("<int:post_pk>/comment/<int:comment_pk>/delete", CommentDeleteView.as_view(), name="comment_delete"),
    path('api/comment/like/<int:comment_pk>/', ToggleCommentLikeAPI.as_view(), name='toggle-comment-like-api'),
]
