from django.test import TestCase, Client
from http import HTTPStatus


class TaskURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_urls_uses_correct_template(self):
        templates_url_names = {
            'about/about_author.html': '/about/author/',
            'about/about_tech.html': '/about/tech/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_unexciting_page_404(self):
        response = self.guest_client.get('about/unexciting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
