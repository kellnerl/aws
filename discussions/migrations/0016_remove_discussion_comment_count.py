# Generated by Django 4.1 on 2023-06-27 10:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("discussions", "0015_remove_discussion_last_comment"),
    ]

    operations = [
        migrations.RemoveField(model_name="discussion", name="comment_count",),
    ]