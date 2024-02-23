# Generated by Django 4.1 on 2023-07-02 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("discussions", "0026_usercontext_display_fullname"),
    ]

    operations = [
        migrations.AddField(
            model_name="usersection",
            name="domain",
            field=models.CharField(max_length=60, null=True),
        ),
        migrations.AlterField(
            model_name="usersection",
            name="name",
            field=models.CharField(max_length=60),
        ),
        migrations.AlterField(
            model_name="usersection",
            name="number",
            field=models.IntegerField(default=1),
        ),
    ]
