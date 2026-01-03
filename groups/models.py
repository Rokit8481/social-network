import os
from django.db import models
from django.contrib.auth import get_user_model
from accounts.models import BaseModel
from slugify import slugify
import shortuuid
import uuid

def generate_code():
    return str(uuid.uuid4().int)[:8]

User = get_user_model()

class Tag(BaseModel):
    name = models.CharField(max_length=100, unique=True, verbose_name='Tag Name', null=False, blank=False)

    class Meta:
        verbose_name = 'Tag'
        verbose_name_plural = 'Tags'
        ordering = ['name']
        
    def save(self, *args, **kwargs):
        formatted = slugify(self.name, separator="_", lowercase=False)
        self.name = formatted
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Group(BaseModel):
    title = models.CharField(max_length=200, verbose_name='Title', null=False, blank=False)
    description = models.TextField(verbose_name='Description', null=True, blank=True)
    slug = models.SlugField(unique=True, default=shortuuid.uuid, editable=False)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups', null=False)
    admins = models.ManyToManyField(User, related_name='admin_groups', blank=True)
    members = models.ManyToManyField(User, related_name='members_in_groups', blank=True)
    tags = models.ManyToManyField(Tag, related_name='groups', blank=True)

    class Meta:
        verbose_name = 'Group'
        verbose_name_plural = 'Groups'
        ordering = ['-created_at']

    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.creator:
            self.admins.add(self.creator)
            self.members.add(self.creator)  
    def add_creator(self, user):
        self.members.add(user)
        self.admins.add(user)
    def add_admin(self, user):
        if user not in self.members.all():
            self.members.add(user)
        self.admins.add(user)  
    def add_member(self, user):
        self.members.add(user)
    def remove_admin(self, user):
        self.admins.remove(user)
    def remove_member(self, user):
        self.members.remove(user)
        if user in self.admins.all():
            self.admins.remove(user)
    def is_creator(self, user):
        return self.creator == user
    def is_admin(self, user):
        return user == self.creator or self.admins.filter(id=user.id).exists()
    def is_member(self, user):
        return self.members.filter(id=user.id).exists()
    
class GroupMessage(BaseModel):
    group = models.ForeignKey(Group, on_delete=models.CASCADE, related_name='messages', null=False)
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_messages', null=False)
    slug = models.CharField(max_length=8, unique=True, default=generate_code, editable=False)
    content = models.TextField(verbose_name='Message Content', null=False, blank=False)
    
    class Meta:
        verbose_name = 'Group Message'
        verbose_name_plural = 'Group Messages'
        ordering = ['created_at']

    def __str__(self):
        return f'Message from {self.sender} in {self.group}'