# Generated by Django 4.1 on 2023-07-10 01:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0004_remove_usercontext_about_me_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="usersectiondomain",
            name="section_number",
            field=models.IntegerField(default=1),
        ),
    ]
