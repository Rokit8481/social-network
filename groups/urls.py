from django.urls import path
from groups.views import GroupsListView, GroupDetailView

urlpatterns = [
    path('', GroupsListView.as_view(), name='groups_list'),
    path("group/<slug:slug>/", GroupDetailView.as_view(), name="group_detail"),
]
