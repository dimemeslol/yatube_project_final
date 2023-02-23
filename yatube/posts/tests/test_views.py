import shutil
import tempfile

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile

from ..models import Group, Post, Follow


User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='auth')
        cls.user_two = User.objects.create_user(username='another')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.second_authorized_client = Client()
        self.second_authorized_client.force_login(self.user_two)
        self.guest_client = Client()
        cache.clear()

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': 'test-slug'}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': 'auth'}
            ): 'users/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_home_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response.context.get('page_obj')[0], self.post)

    def test_group_list_show_correct_context(self):
        response = (self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'})
        ))
        self.assertEqual(response.context.get('group'), self.group)
        self.assertEqual(response.context.get('page_obj')[0], self.post)

    def test_profile_show_correct_context(self):
        response = (self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'auth'})
        ))
        self.assertEqual(response.context.get('author'), self.user)
        self.assertEqual(response.context.get('page_obj')[0], self.post)

    def test_post_detail_show_correct_context(self):
        response = (self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        ))
        self.assertEqual(response.context.get('post'), self.post)

    def test_forms_post_edit_show_correct_context(self):
        response = (self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_forms_post_create_show_correct_context(self):
        response = (self.authorized_client.get(
            reverse('posts:post_create')
        ))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_group_added_correctly(self):
        post = Post.objects.create(
            text='Текст для проверки добавления',
            author=self.user,
            group=self.group
        )
        response_index = self.authorized_client.get(
            reverse('posts:index')
        )
        response_group = self.authorized_client.get(
            reverse('posts:group_list',
                    kwargs={'slug': f'{self.group.slug}'}
                    )
        )
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}
                    )
        )
        index = response_index.context['page_obj']
        group = response_group.context['page_obj']
        profile = response_profile.context['page_obj']
        self.assertIn(post, index, )
        self.assertIn(post, group, )
        self.assertIn(post, profile, )

    def test_post_group_added_correctly_user_two(self):
        group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_group2',
        )
        posts_count = Post.objects.filter(group=self.group).count()
        post = Post.objects.create(
            text='Тестовый пост от другого автора',
            author=self.user_two,
            group=group2
        )
        response_profile = self.authorized_client.get(
            reverse('posts:profile',
                    kwargs={'username': f'{self.user.username}'}
                    )
        )
        group = Post.objects.filter(group=self.group).count()
        profile = response_profile.context['page_obj']
        self.assertEqual(group, posts_count)
        self.assertNotIn(post, profile)

    def test_pages_img_in_context(self):
        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}),
            reverse('posts:profile', kwargs={'username': 'auth'}),
        ]
        for url in urls:
            response = self.authorized_client.get(url)
            with self.subTest(response=response):
                self.assertEqual(
                    response.context.get('page_obj')[0].image, self.post.image
                )

    def test_comment_on_post_detail(self):
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data={'text': 'Тестовый текст комментария'},
            follow=True
        )
        comment_context = response.context.get('comments')[0]
        self.assertIn(comment_context, self.post.comments.all())

    def test_index_cache(self):
        index_url = reverse('posts:index')
        response = self.authorized_client.get(index_url)
        content_response = response.content
        # Создаём пост
        self.authorized_client.post(
            reverse('posts:post_create'),
            data={'text': 'Тестовый текст cache'},
            follow=True
        )
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст cache',
            ).exists()
        )
        cache_response = self.authorized_client.get(index_url)
        cache_response_content = cache_response.content
        self.assertEqual(content_response, cache_response_content)
        cache.clear()
        no_cache_response = self.authorized_client.get(index_url)
        no_cache_response_content = no_cache_response.content
        self.assertNotEqual(content_response, no_cache_response_content)

    def test_auth_user_follow(self):
        self.second_authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username})
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user_two,
                author=self.user,
            ).exists()
        )
        response = self.second_authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertEqual(response.context.get('page_obj')[0], self.post)

    def test_auth_user_unfollow(self):
        self.second_authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user.username})
        )
        self.second_authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user.username})
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user_two,
                author=self.user,
            ).exists()
        )
        response = self.second_authorized_client.get(
            reverse('posts:follow_index')
        )
        self.assertQuerysetEqual(
            response.context.get('page_obj').object_list, []
        )
