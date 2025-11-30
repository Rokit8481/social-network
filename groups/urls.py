from django.urls import path
from groups.views import GroupsListView, GroupDetailView,\
                            CreateGroupView, EditGroupView,\
                            GroupMessageAjaxView, JoinGroupView, LeaveGroupView,\
                            EditGroupMessageAjaxView, DeleteGroupMessageAjaxView

urlpatterns = [
    path('', GroupsListView.as_view(), name='groups_list'),
    path("create/", CreateGroupView.as_view(), name="create_group"),
    path("<slug:slug>/", GroupDetailView.as_view(), name="group_detail"),
    path("<slug:slug>/edit/", EditGroupView.as_view(), name="edit_group"),
    path("<slug:slug>/join/", JoinGroupView.as_view(), name="join_group"),
    path("<slug:slug>/leave/", LeaveGroupView.as_view(), name="leave_group"),
    path("<slug:slug>/message/", GroupMessageAjaxView.as_view(), name="group_message_ajax"),
    path("<slug:slug>/message/<int:message_id>/edit/", EditGroupMessageAjaxView.as_view(), name="edit_group_message_ajax"),
    path("<slug:slug>/message/<int:message_id>/delete/", DeleteGroupMessageAjaxView.as_view(), name="delete_group_message_ajax"),
]
