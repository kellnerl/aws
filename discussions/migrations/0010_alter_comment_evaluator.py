# Generated by Django 4.1 on 2023-06-25 21:59

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("discussions", "0009_alter_discussion_created_by"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="evaluator",
            field=models.ManyToManyField(null=True, to=settings.AUTH_USER_MODEL),
        ),
    ]
