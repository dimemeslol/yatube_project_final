from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.constraints import UniqueConstraint

from core.models import CreatedModel


User = get_user_model()


class Post(CreatedModel):
    text = models.TextField(
        verbose_name='Текст поста',
        help_text='Текст вашего поста'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор поста'
    )
    group = models.ForeignKey(
        'Group',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа поста',
        help_text='Группа к которой будет относиться пост'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Имя группы'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='slug'
    )
    description = models.TextField(verbose_name='Описание группы')

    def __str__(self):
        return self.title

    class Meta:
        indexes = [
            models.Index(fields=['slug'])
        ]


class Comment(CreatedModel):
    text = models.TextField(
        verbose_name='Текст комментария',
        help_text='Текст комментария'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Автор комментария'
    )
    post = models.ForeignKey(
        'Post',
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост комментария',
        help_text='Пост к которому относится комментарий'
    )

    class Meta:
        ordering = ('pub_date',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(CreatedModel):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Кто подписывается',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='На кого подписывается'
    )

    def __str__(self):
        return f'Фолловер: {self.user}, автор: {self.author}'

    class Meta:
        constraints = [
            UniqueConstraint(
                fields=['user', 'author'],
                name='unique_followers'
            )
        ]
