from http import HTTPStatus
from django.core.cache import cache
from django.test import Client, TestCase
from ..models import Group, Post, User

# from django.urls import reverse


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="Testuser")
        cls.not_author = User.objects.create_user(username="Notauthoruser")
        cls.post = Post.objects.create(
            author=cls.author, text="Тестовый текст"
        )
        cls.group = Group.objects.create(
            title="testgroup",
            slug="test_slug",
            description="test descriptions",
        )
        cls.templates_url_names_open = {
            "index.html": "/",
            "group_list.html": f"/group/{cls.group.slug}/",
            "profile.html": f"/profile/{cls.author.username}/",
            "post.html": f"/posts/{cls.post.id}/",
        }
        cls.templates_url_names_close = (
            ("new_post.html", "/create/"),
            ("new_post.html", f"/posts/{cls.post.id}/edit/"),
        )

    def setUp(self):
        self.anonim_user = Client()
        self.authorized_user = Client()
        self.authorized_user.force_login(self.author)
        self.not_author_user = Client()
        self.not_author_user.force_login(self.not_author)
        cache.clear()

    def test_urls_anonymous(self):
        """URL-адрес доступность для анонимного пользователя и проверка
        перенаправления"""
        for template, reverse_name in self.templates_url_names_open.items():
            with self.subTest():
                response = self.anonim_user.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_anonymous_close(self):
        for template, reverse_name in self.templates_url_names_close:
            with self.subTest(reverse_name=reverse_name):
                response = self.anonim_user.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.FOUND)
                self.assertRedirects(
                    response, "/auth/login/?next={}".format(reverse_name)
                )

    def test_urls_author(self):
        """URL-адрес доступен автору поста"""
        for template, reverse_name in self.templates_url_names_open.items():
            with self.subTest():
                response = self.authorized_user.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        for template, reverse_name in self.templates_url_names_close:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_user.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_not_author(self):
        """URL-адрес доступен не автору поста"""
        for template, reverse_name in self.templates_url_names_open.items():
            with self.subTest():
                response = self.not_author_user.get(reverse_name)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.not_author_user.get(
            f"/posts/{self.post.id}/edit/"
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.not_author_user.get("/create/")
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон"""
        for template, reverse_name in self.templates_url_names_open.items():
            with self.subTest(reverse_name=reverse_name, template=template):
                cache.clear()
                response = self.authorized_user.get(reverse_name)
                self.assertTemplateUsed(response, template)
        response = self.authorized_user.get(
            f"/posts/{self.post.id}/edit/"
        )
        self.assertTemplateUsed(response, "new_post.html")
