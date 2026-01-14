from django import forms
from phonenumber_field.formfields import PhoneNumberField
from phonenumber_field.widgets import RegionalPhoneNumberWidget 
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegistrationStep1Form(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})


class RegistrationStep2Form(forms.ModelForm):
    mobile = PhoneNumberField(
        widget=RegionalPhoneNumberWidget(attrs={'class': 'form-control'}),
        required=False
    )

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'bio', 'avatar', 'mobile', 'birthday')

        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class UserEditForm(forms.ModelForm):
    mobile = PhoneNumberField(
        widget=RegionalPhoneNumberWidget(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 
            'bio', 'avatar', 'mobile', 'birthday'
        )
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
            'birthday': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
