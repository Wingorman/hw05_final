from django.test import TestCase
from ..models import Group, Post, User


class PostsModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username="testuser")
        cls.text = "Тестовый текст больше 15 символов"
        cls.post = Post.objects.create(text=cls.text, author=cls.user)
        cls.group = Group.objects.create(title="testgroup", slug="slug")

    def test_sub_n(self):
        expect = {
            str(self.post): self.post.text[:15],
            str(self.group): self.group.title,
        }
        for key, value in expect.items():
            with self.subTest(value=value):
                self.assertEqual(key, value)
