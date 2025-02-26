# Generated by Django 4.1 on 2023-06-27 10:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discussions", "0016_remove_discussion_comment_count"),
    ]

    operations = [
        migrations.AddField(
            model_name="discussion",
            name="comments_count",
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="discussion",
            name="last_comment",
            field=models.DateTimeField(null=True),
        ),
    ]
