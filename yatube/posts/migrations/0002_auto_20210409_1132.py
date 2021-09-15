# Generated by Django 2.2.9 on 2021-04-09 03:32

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("posts", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Group",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(blank=True, max_length=100, null=True)),
                ("slug", models.SlugField(max_length=20, unique=True)),
                ("description", models.TextField()),
            ],
        ),
        migrations.AddField(
            model_name="post",
            name="groupe",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="post",
                to="posts.Group",
            ),
        ),
    ]
