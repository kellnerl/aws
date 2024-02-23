# Generated by Django 4.1 on 2023-08-09 21:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0009_alter_userdetail_photo"),
    ]

    operations = [
        migrations.AddField(
            model_name="userdetail",
            name="place_of_residence",
            field=models.CharField(max_length=160, null=True),
        ),
        migrations.AlterField(
            model_name="userdetail",
            name="about_me",
            field=models.TextField(max_length=480, null=True),
        ),
        migrations.AlterField(
            model_name="userdetail",
            name="photo",
            field=models.ImageField(upload_to="photos/"),
        ),
    ]