# Generated by Django 4.1 on 2023-08-12 13:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0010_userdetail_place_of_residence_and_more"),
    ]

    operations = [
        migrations.RemoveField(model_name="usercontext", name="ui_theme",),
        migrations.RemoveField(model_name="usersectiondomain", name="description",),
    ]