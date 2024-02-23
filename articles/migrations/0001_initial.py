# Generated by Django 4.1 on 2023-07-12 14:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("users", "0006_remove_usersection_domain"),
        (
            "discussions",
            "0031_remove_usercontext_ui_theme_remove_usercontext_user_and_more",
        ),
    ]

    operations = [
        migrations.CreateModel(
            name="ArticleUserQuery",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=120)),
                ("description", models.CharField(max_length=320, null=True)),
                ("url", models.URLField(max_length=240, unique=True)),
                ("domain", models.CharField(max_length=80)),
                ("author", models.CharField(max_length=120, null=True)),
                ("published_before", models.DateTimeField(auto_now=True)),
                ("published_after", models.DateTimeField(auto_now=True)),
                (
                    "theme",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="theme_of_article_query_set",
                        to="discussions.articletheme",
                    ),
                ),
                (
                    "user",
                    models.ForeignKey(
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="user_context_article_query_set",
                        to="users.usercontext",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Article",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=120)),
                ("description", models.CharField(max_length=320, null=True)),
                ("url", models.URLField(max_length=240, unique=True)),
                ("domain", models.CharField(max_length=80)),
                ("author", models.CharField(max_length=120, null=True)),
                ("published_on", models.DateTimeField(auto_now=True)),
                (
                    "theme",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="theme_of_article_set",
                        to="discussions.articletheme",
                    ),
                ),
            ],
        ),
    ]