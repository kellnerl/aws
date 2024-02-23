# Generated by Django 4.1 on 2023-06-25 02:03

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("discussions", "0006_rename_is_active_usercontext_active_and_more"),
    ]

    operations = [
        migrations.AlterField(
            model_name="comment",
            name="discussion",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="comments_set",
                to="discussions.discussion",
            ),
        ),
    ]