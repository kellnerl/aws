# Generated by Django 4.1 on 2023-07-13 01:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0003_alter_article_description_alter_article_published_on"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="discussion",
            field=models.BooleanField(default=False),
        ),
    ]
