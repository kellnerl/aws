# Generated by Django 4.1 on 2023-08-10 23:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0009_remove_article_scrapping"),
    ]

    operations = [
        migrations.AlterField(
            model_name="article", name="theme", field=models.CharField(max_length=30),
        ),
    ]