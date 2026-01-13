from django import forms
from boards.models import Board, BoardMessage
from boards.widgets import TagSelect2Widget

class CreateBoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ["title", "description", "tags"]
        
        widgets = {
            "title": forms.TextInput(attrs={'class': 'form-control'}),
            "description": forms.Textarea(attrs={'class': 'form-control'}),
            "tags": TagSelect2Widget(
                attrs={"data-placeholder": "Add or choose tags", "style": "width:100%"}
            ),
        }

class EditBoardForm(forms.ModelForm):
    class Meta:
        model = Board
        fields = ['title', 'description', 'tags', 'admins']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            "tags": TagSelect2Widget(
                attrs={
                    "data-placeholder": "Add or choose tags",
                    "style": "width: 100%;"
                }),
            'admins': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['admins'].queryset = self.instance.members.all()

class CreateBoardMessageForm(forms.ModelForm):
    class Meta:
        model = BoardMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }