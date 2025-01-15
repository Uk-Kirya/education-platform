from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Notification, Comment


class HomeWorkSendForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ('text',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', 'file')
