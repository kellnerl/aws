# Generated by Django 4.1 on 2023-07-13 03:17

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0006_article_commnet_count"),
    ]

    operations = [
        migrations.RenameField(
            model_name="article", old_name="commnet_count", new_name="comments_count",
        ),
    ]
