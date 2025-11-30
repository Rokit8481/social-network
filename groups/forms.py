from django import forms
from groups.models import Group, Tag, GroupMessage, GroupMessageFile

class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['title', 'description', 'tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

class EditGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['title', 'description', 'tags', 'admins', 'members']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'admins': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'members': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if self.instance.pk: 
                self.fields['admins'].queryset = self.fields['admins'].queryset.exclude(id=user.id) | self.instance.admins.filter(id=user.id)
                self.fields['members'].queryset = self.fields['members'].queryset.exclude(id=user.id) | self.instance.members.filter(id=user.id)
            else:
                self.fields['admins'].queryset = self.fields['admins'].queryset.exclude(id=user.id)
                self.fields['members'].queryset = self.fields['members'].queryset.exclude(id=user.id)

class GroupMessageForm(forms.ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }