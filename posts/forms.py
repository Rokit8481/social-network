from django import forms
from posts.models import Post, Comment
from django.contrib.auth import get_user_model

User = get_user_model()

class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['title', 'content', 'people_tags']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter content'}),
            'people_tags': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if self.user:
            allowed_users = User.objects.filter(followers__follower=self.user)
            self.fields['people_tags'].queryset = allowed_users

    def clean_people_tags(self):
        people = self.cleaned_data.get('people_tags')

        if not self.user:
            return people

        if people.count() > 25:
            raise forms.ValidationError(
                "You can tag no more than 25 people."
            )

        allowed_users = User.objects.filter(followers__follower=self.user)

        for person in people:
            if person not in allowed_users:
                raise forms.ValidationError(
                    "You can only tag users you follow."
                )

        return people



class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Enter your comment', 'rows': 3}),
        }
