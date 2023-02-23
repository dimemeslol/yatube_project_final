from django import forms
from django.forms import Textarea
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        widgets = {
            'text': Textarea(attrs={'cols': 80, 'rows': 20})
        }
        labels = {
            'text': 'Текст поста',
            'group': 'Группа поста',
        }
        help_texts = {
            'text': 'Напишите свой пост здесь',
            'group': 'Выберите группу к которой относится пост',
        }


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        widgets = {
            'text': Textarea(attrs={'cols': 5, 'rows': 2})
        }
