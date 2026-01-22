from django import forms
from boards.models import Board, BoardMessage
from boards.widgets import TagSelect2Widget
from accounts.helpers.custom_settings import MAX_TAGS_PER_BOARD, MAX_TAG_LEN

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
    
    def clean_tags(self):
        tags = self.cleaned_data.get("tags")
        
        if not tags:
            return tags

        if tags.count() > MAX_TAGS_PER_BOARD:
            raise forms.ValidationError(
                f"You can add no more than {MAX_TAGS_PER_BOARD} tags."
            )
        
        for tag in tags:
            if len(tag.name) > MAX_TAG_LEN:
                raise forms.ValidationError(
                    f"Tag “{tag.name[:20]}…” is too long (max {MAX_TAG_LEN} characters)"
                )

        return tags

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
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['admins'].queryset = self.instance.members.all()

    def clean_tags(self):
        tags = self.cleaned_data.get("tags")

        if not tags:
            return tags

        if tags.count() > MAX_TAGS_PER_BOARD:
            raise forms.ValidationError(
                f"You can add no more than {MAX_TAGS_PER_BOARD} tags."
            )
        
        for tag in tags:
            if len(tag.name) > MAX_TAG_LEN:
                raise forms.ValidationError(
                    f"Tag “{tag.name[:20]}…” is too long (max {MAX_TAG_LEN} characters)"
                )

        return tags

class CreateBoardMessageForm(forms.ModelForm):
    class Meta:
        model = BoardMessage
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 1}),
        }