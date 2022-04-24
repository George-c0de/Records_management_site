
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ModelForm

from main.models import Application


class CreateUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ApplicationForm(ModelForm):
    class Meta:
        model = Application
        fields = ["text", "status"]
