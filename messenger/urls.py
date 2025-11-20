from django.urls import path
from .views import *

urlpatterns = [
    path("", ChatView.as_view(), name="main"),
    path("create_chat/", CreateChatView.as_view(), name="create_chat"),
    path("create_group/", CreateGroupView.as_view(), name="create_group"),
    path("chat/<int:chat_pk>/edit/", ChatEditView.as_view(), name="chat_edit"),
    path("chat/<int:chat_pk>/delete/", ChatDeleteView.as_view(), name="chat_delete"),
    path("message/<int:message_pk>/edit/", MessageEditView.as_view(), name="message_edit"),
    path("message/<int:message_pk>/delete/", MessageDeleteView.as_view(), name="message_delete"),
    path("chat/<int:chat_pk>/", ChatView.as_view(), name="chat"),
    path("api/send_message/<int:chat_id>/", SendMessageView.as_view(), name="send_message"),
    path("api/add_reaction/<int:message_id>/", AddReactionView.as_view(), name="add_reaction"),
]