import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..forms import PostForm
from ..models import Post, User, Group
from http import HTTPStatus
from django.core.cache import cache

TEMP_MEDIA = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA)
class TaskCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username="AndreyG")
        cls.group = Group.objects.create(
            title="test_group",
            slug="test_slug",
        )
        cls.post = Post.objects.create(
            text="TestText",
            author=cls.author,
            group=Group.objects.create(
                title="testGroup",
                slug="slugforgroup",
            ),
        )
        cls.form = PostForm()
        cls.contexted = {
            "text": "TestText",
            "author": "AndreyG",
            "title": "test title",
            "slug": "test-slug",
            "title2": "testGroup",
        }

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
        self.guest_client = Client()
        self.anonymous = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        cache.clear()

    def test_create_post(self):
        """При отправке формы создаётся новая запись в базе данных."""
        posts_count = Post.objects.count()
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        uploaded = SimpleUploadedFile(
            name="small.gif", content=small_gif, content_type="image/gif"
        )
        form_data = {
            "text": "Тест",
            "image": uploaded,
        }
        self.authorized_client.post(reverse("create"), data=form_data)
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(Post.objects.filter(text=form_data["text"]).exists())

    def test_anonymous_not_add_post(self):
        """Неавторизованный пользователь не может опубликовать пост"""
        counter = Post.objects.count()
        response = self.anonymous.get(reverse("create"))
        urls = "/auth/login/?next=/create/"
        self.assertEqual(Post.objects.count(), counter)
        self.assertRedirects(response, urls, status_code=HTTPStatus.FOUND)

    def test_edit_post(self):
        small_gif = (
            b"\x47\x49\x46\x38\x39\x61\x02\x00"
            b"\x01\x00\x80\x00\x00\x00\x00\x00"
            b"\xFF\xFF\xFF\x21\xF9\x04\x00\x00"
            b"\x00\x00\x00\x2C\x00\x00\x00\x00"
            b"\x02\x00\x01\x00\x00\x02\x02\x0C"
            b"\x0A\x00\x3B"
        )
        small_gif_name = "small_new.gif"
        uploaded = SimpleUploadedFile(
            name=small_gif_name, content=small_gif, content_type="image/gif"
        )
        counter = Post.objects.count()
        form_data = {
            "text": "ИзменилТекст",
            "image": uploaded,
        }
        response = self.authorized_client.post(
            reverse(
                "post_edit",
                kwargs={
                    "post_id": self.post.id,
                },
            ),
            data=form_data,
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertEqual(Post.objects.count(), counter)
        response = self.authorized_client.get(reverse("index"))
        self.assertEqual(response.context["page_obj"][0].text, "ИзменилТекст")
        self.assertEqual(response.context["page_obj"][0].author, self.author)
        expected_image_name = f"posts/{form_data['image'].name}"
        self.assertEqual(
            response.context["page_obj"][0].image, expected_image_name
        )

    def test_new_post_page(self):
        """проверяет форма на странице создания поста"""
        response = self.authorized_client.get(reverse("create"))
        form_fields = PostForm
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], form_fields)

    def test_edit_post_page(self):
        """проверяет формы на странице редактирования поста"""
        response = self.authorized_client.get(f"/posts/{ self.post.id }/edit/")
        form_fields = PostForm
        self.assertIn("form", response.context)
        self.assertIsInstance(response.context["form"], form_fields)

    def test_profile_context(self):
        """Добавление поста на страницу автора"""
        response = self.authorized_client.get(
            reverse("profile", kwargs={"username": f"{self.author}"})
        )
        self.assertEqual(
            response.context["page_obj"][0].text, self.contexted["text"]
        )
        self.assertEqual(
            response.context["page_obj"][0].author.username,
            self.contexted["author"],
        )

    def test_post_in_right_group(self):
        """Добавление поста в правильную группу"""
        self.post = Post.objects.create(
            text="Kaktak",
            author=User.objects.create(username="Roman"),
            group=Group.objects.create(
                title="RGroup",
                slug="Rtest-slug",
            ),
        )
        self.group = Group.objects.create(
            title="RGroup2",
            slug="Rtest-slug2",
        )
        response = self.guest_client.get(
            reverse("group", kwargs={"slug": "Rtest-slug2"})
        )
        self.assertEqual(len(response.context["page_obj"]), 0)
