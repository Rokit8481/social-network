from django.urls import path
from groups.views import GroupsListView, GroupDetailView, CreateGroupView, EditGroupView, GroupMessageAjaxView

urlpatterns = [
    path('', GroupsListView.as_view(), name='groups_list'),
    path("create/", CreateGroupView.as_view(), name="create_group"),
    path("<slug:slug>/", GroupDetailView.as_view(), name="group_detail"),
    path("<slug:slug>/edit/", EditGroupView.as_view(), name="edit_group"),
    path("<slug:slug>/message/", GroupMessageAjaxView.as_view(), name="group_message_ajax"),
]
