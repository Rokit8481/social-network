from django import forms
from groups.models import Group, Tag, GroupMessage, GroupMessageFile
from groups.widgets import TagSelect2Widget

class CreateGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ["title", "description", "tags"]
        
        widgets = {
            "title": forms.TextInput(attrs={'class': 'form-control'}),
            "description": forms.Textarea(attrs={'class': 'form-control'}),
            "tags": TagSelect2Widget(
                attrs={"data-placeholder": "Add or choose tags", "style": "width:100%"}
            ),
        }

class EditGroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['title', 'description', 'tags', 'admins', 'members']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            "tags": TagSelect2Widget(
                attrs={
                    "data-placeholder": "Choose tags",
                    "style": "width: 100%;"
                }),
            'admins': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            if self.instance.pk: 
                self.fields['admins'].queryset = self.fields['admins'].queryset.exclude(id=user.id) | self.instance.admins.filter(id=user.id)
            else:
                self.fields['admins'].queryset = self.fields['admins'].queryset.exclude(id=user.id)

class GroupMessageForm(forms.ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }