# Generated by Django 4.1 on 2023-06-23 16:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discussions", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="section",
            name="tabname",
            field=models.CharField(default="tab", max_length=6),
        ),
        migrations.AlterField(
            model_name="usercontext",
            name="default_comments_ordering",
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="usercontext",
            name="default_discussions_ordering",
            field=models.IntegerField(default=1),
        ),
        migrations.AlterField(
            model_name="usercontext",
            name="default_user_comments_ordering",
            field=models.IntegerField(default=1),
        ),
    ]
