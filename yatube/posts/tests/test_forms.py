import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse
from ..forms import PostForm
from ..models import Post, User, Group
from http import HTTPStatus
from django.core.cache import cache

TEMP_MEDIA = tempfile.mkdtemp(dir=settings.BASE_DIR)


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
            text="текст",
            author=cls.author,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)
        super().tearDownClass()

    def setUp(self):
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
        counter = Post.objects.count()
        form_data = {"text": "ИзменилТекст"}
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
