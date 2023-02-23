from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост123',  # длина тест поста 16 символов
        )

    def test_models_have_correct_object_names(self):
        group = PostModelTest.group
        post = PostModelTest.post
        model_test = {
            group: 'Тестовая группа',
            post: 'Тестовый пост12',  # проверяем что осталось только 15 симв
        }
        for field, excepted_value in model_test.items():
            with self.subTest(field=field):
                self.assertEqual(str(field), excepted_value)
