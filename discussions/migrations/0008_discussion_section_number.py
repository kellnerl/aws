# Generated by Django 4.1 on 2023-06-25 02:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discussions", "0007_alter_comment_discussion"),
    ]

    operations = [
        migrations.AddField(
            model_name="discussion",
            name="section_number",
            field=models.IntegerField(default=1),
        ),
    ]
