# Generated by Django 4.1 on 2023-07-13 01:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0004_article_discussion"),
    ]

    operations = [
        migrations.AddField(
            model_name="article",
            name="discussion_id",
            field=models.IntegerField(default=0),
        ),
    ]
