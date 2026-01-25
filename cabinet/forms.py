from django import forms

from .models import Notification, Comment


class HomeWorkSendForm(forms.ModelForm):
    class Meta:
        model = Notification
        fields = ('text',)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text', 'file')
