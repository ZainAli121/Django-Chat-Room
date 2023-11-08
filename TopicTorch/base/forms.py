from django.forms import ModelForm
from .models import *
from django.contrib.auth.forms import UserCreationForm


class RoomForm(ModelForm):
    class Meta:
        model = Room
        fields = '__all__'
        exclude = ['host', 'members']


class UserForm(ModelForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'bio', 'avatar']

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'username', 'email', 'password1', 'password2']