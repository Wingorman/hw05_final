from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(max_length=20, unique=True)
    description = models.TextField()

    class Meta:
        verbose_name_plural = "Сообщества"

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField(
        "date published", auto_now_add=True, db_index=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="posts"
    )
    group = models.ForeignKey(
        "Group",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="posts",
    )
    image = models.ImageField(upload_to="posts/", blank=True, null=True)

    class Meta:
        verbose_name_plural = "Посты"
        ordering = ("-pub_date",)

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name="comments"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="comments"
    )
    text = models.TextField("Текст", help_text="Текст нового комментария")
    created = models.DateTimeField("date published", auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="follower"
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="following"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "author"], name="unique_pair"
            )
        ]
