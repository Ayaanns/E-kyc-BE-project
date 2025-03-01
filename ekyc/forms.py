from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django import forms
from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'username', 'password1', 'password2']

    # @property
    # def is_anonymous(self):
    #     """
    #     always return False. This is a way of comparing User objects to is_anonymous users.
    #     """
    #     return False

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label="Email", widget=forms.EmailInput)
    # password1 = forms.CharField(label="Password", widget=forms.PasswordInput(attrs={
    #     'class': 'form-control',
    #     'placeholder': 'Enter your password',
    # }))


class PinVerificationForm(forms.Form):
    pin = forms.CharField(max_length=6, min_length=6)
