from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post, Comment, Follow
from django.core.cache import cache

User = get_user_model()


class UrlTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username="YarSlav")
        cls.post = Post.objects.create(
            text="TestText",
            author=cls.author,
            group=Group.objects.create(
                title="testGroup",
                slug="slugforgroup",
            ),
        )
        cls.group = Group.objects.create(title="test title", slug="test-slug")
        cls.contexted = {
            "text": "TestText",
            "author": "YarSlav",
            "title": "test title",
            "slug": "test-slug",
            "title2": "testGroup",
        }

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.author)
        self.another_authorized_client = Client()
        self.another_authorized_client.force_login(
            User.objects.create_user(username="Test_User")
        )
        cache.clear()

    def test_cache_index(self):
        response = self.authorized_client.get(reverse("index"))
        Post.objects.get(
            text=self.post.text, author=self.post.author, group=self.post.group
        ).delete()
        self.assertIn(self.post.text, response.content.decode("utf-8"))
        cache.clear()
        response = self.authorized_client.get(reverse("index"))
        self.assertNotIn(self.post.text, response.content.decode("utf-8"))

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "имя_html_шаблона: reverse(name)"
        templates_page_names = {
            "index.html": reverse("index"),
            "new_post.html": reverse("create"),
            "group_list.html": (
                reverse("group", kwargs={"slug": "test-slug"})
            ),
        }
        # Проверяем, что при обращении к name
        # вызывается соответствующий HTML-шаблон
        for template, reverse_name in templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_page_index(self):
        """пост добавился на 1-ю страницу index"""
        response = self.authorized_client.get(
            reverse(
                "index",
            )
        )
        self.assertEqual(
            response.context["page_obj"][0].text, self.contexted["text"]
        )
        self.assertEqual(
            response.context["page_obj"][0].author.username,
            self.contexted["author"],
        )
        self.assertEqual(
            response.context["page_obj"][0].group.title,
            self.contexted["title2"],
        )

    def test_group_page(self):
        """откр тестовая группа в её контексте передается test title и слаг"""
        response = self.authorized_client.get(
            reverse("group", kwargs={"slug": "test-slug"})
        )
        self.assertEqual(
            response.context["group"].title, self.contexted["title"]
        )
        self.assertEqual(
            response.context["group"].slug, self.contexted["slug"]
        )


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username="auth")
        cls.group = Group.objects.create(
            title="Тестовая группа",
            slug="test-slug",
            description="Описание тестовой группы",
        )
        cls.post = Post.objects.create(
            text="текст поста",
            author=cls.author,
            group=cls.group,
            pk=61,
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем авторизованый клиент
        self.user = User.objects.create_user(username="Wings")
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client = Client()
        self.author_client.force_login(self.author)
        cache.clear()

    def test_follow_author(self):
        self.authorized_client.post(
            reverse("profile_follow", args={self.author})
        )
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.author,
            ).exists()
        )

    def test_unfollow_author(self):
        self.authorized_client.post(
            reverse("profile_unfollow", args={self.author})
        )
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.author,
            ).exists()
        )

    def test_follow_author_appears_at_desired_location(self):
        following_count = Follow.objects.count()
        Follow.objects.create(user=self.user, author=self.author)
        response = self.authorized_client.get(reverse("follow_index"))
        response_count = len(response.context["page_obj"])
        self.assertEqual(response_count, following_count + 1)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.author,
            ).exists()
        )
        Follow.objects.filter(user=self.user, author=self.author).delete()
        response = self.authorized_client.get(reverse("follow_index"))
        response_count_last = len(response.context["page_obj"])
        self.assertEqual(response_count_last, following_count)


class TestComment(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create(username="COCO")
        cls.test_group = Group.objects.create(
            title="Тестовое сообщество",
            slug="Comtest-slug",
            description="Тестовое описание сообщества",
        )
        cls.test_post = Post.objects.create(
            text="Тестовый текст",
            author=get_user_model().objects.create_user(username="DJ"),
            group=cls.test_group,
        )
        cls.post_another_author = Post.objects.create(
            text="Другой автор",
            author=get_user_model().objects.create_user(username="MC"),
            group=cls.test_group,
        )
        kwargs_post = {
            "post_id": cls.test_post.id,
        }
        post_URL = reverse("post", kwargs=kwargs_post)
        post_edit_URL = reverse("post_edit", kwargs=kwargs_post)
        username = cls.test_post.author.username
        cls.templates_reverse_names = {
            reverse("index"): "index.html",
            reverse(
                "group", kwargs={"slug": "Comtest-slug"}
            ): "group_list.html",
            reverse("create"): "new_post.html",
            reverse("profile", kwargs={"username": username}): "profile.html",
            post_URL: "post.html",
            post_edit_URL: "new_post.html",
        }

    def setUp(self):
        self.guest_client = Client()
        self.user = self.test_post.author
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment(self):
        """Только авторизированный пользователь может комментировать посты."""
        comment_count = Comment.objects.count()
        post_id = self.post_another_author.id
        kwargs = {"post_id": post_id}
        reverse_name = reverse("add_comment", kwargs=kwargs)
        form_data = {
            "text": "Тестовый комментарий",
        }
        self.authorized_client.post(reverse_name, data=form_data)
        self.assertEqual(Comment.objects.count(), comment_count + 1)
        self.guest_client.post(reverse_name, data=form_data)
        self.assertNotEqual(Comment.objects.count(), comment_count + 2)


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title="testGroup",
            slug="slugforgroup",
        )
        cls.author = User.objects.create_user(username="Test_User2")
        cls.posts = [
            Post(
                text="TestText",
                author=cls.author,
                group=cls.group,
            )
            for i in range(13)
        ]
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.client = Client()
        cache.clear()

    def test_first_page_second_page_contains_records(self):
        expected = [("", 10), ("?page=2", 3)]
        for query_param, expected_post_count in expected:
            with self.subTest(value=query_param):
                response = self.client.get(reverse("index") + query_param)
                self.assertEqual(
                    len(response.context.get("page_obj").object_list),
                    expected_post_count,
                )

    def test_group_10post(self):
        response = self.client.get(
            reverse("group", kwargs={"slug": "slugforgroup"})
        )
        self.assertEqual(len(response.context.get("page_obj").object_list), 10)

    def test_profile_10post(self):
        response = self.client.get(
            reverse("profile", kwargs={"username": f"{self.author}"})
        )
        self.assertEqual(len(response.context.get("page_obj").object_list), 10)
