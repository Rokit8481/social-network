from django.urls import path
from boards.views import BoardsListView, BoardDetailView,\
                            CreateBoardView, EditBoardView,\
                            BoardMessageAjaxView, JoinBoardView, LeaveBoardView,\
                            EditBoardMessageAjaxView, DeleteBoardMessageAjaxView,\
                            BoardsInfiniteAPI, BoardMessagesInfiniteAPI

urlpatterns = [
    path('', BoardsListView.as_view(), name='boards_list'),
    path("infinite/", BoardsInfiniteAPI.as_view(), name="boards_infinite"),
    path("create/", CreateBoardView.as_view(), name="create_boards_board"),
    path("<slug:slug>/", BoardDetailView.as_view(), name="board_detail"),
    path("<slug:slug>/infinite/", BoardMessagesInfiniteAPI.as_view(), name="boards_messages_infinite"),
    path("<slug:slug>/edit/", EditBoardView.as_view(), name="edit_board"),
    path("<slug:slug>/join/", JoinBoardView.as_view(), name="join_board"),
    path("<slug:slug>/leave/", LeaveBoardView.as_view(), name="leave_board"),
    path("<slug:slug>/group_message/", BoardMessageAjaxView.as_view(), name="board_message_ajax"),
    path("<slug:slug>/group_message/<int:message_id>/edit/", EditBoardMessageAjaxView.as_view(), name="edit_board_message_ajax"),
    path("<slug:slug>/group_message/<int:message_id>/delete/", DeleteBoardMessageAjaxView.as_view(), name="delete_board_message_ajax"),
]
