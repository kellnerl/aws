# Generated by Django 4.1 on 2024-02-23 02:52

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("discussions", "0040_remove_discussion_first_level_domain"),
    ]

    operations = [
        migrations.AddField(
            model_name="comment", name="root_id", field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name="discussion",
            name="favorite",
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name="section",
            name="region",
            field=models.CharField(default="cz", max_length=2),
        ),
        migrations.AddField(
            model_name="section",
            name="title",
            field=models.CharField(max_length=160, null=True),
        ),
        migrations.AlterField(
            model_name="comment",
            name="evaluator",
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AlterField(
            model_name="discussion",
            name="theme",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="theme_of_dicsussion_set",
                to="discussions.articletheme",
            ),
        ),
        migrations.AlterModelTable(name="domain", table="domain",),
    ]