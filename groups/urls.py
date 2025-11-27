from django.urls import path
from groups.views import GroupsListView

urlpatterns = [
    path('', GroupsListView.as_view(), name='groups_list'),
]
