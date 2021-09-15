from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ("text", "group", "image")
        help_text = {
            "text": "Введите текст записи",
            "group": "Выберите группу",
        }
        labels = {"text": "Текст", "groupe": "Группа"}


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ("text",)
        labels = {
            "text": "Текст",
        }
        help_texts = {
            "text": "Текст нового комментария",
        }
