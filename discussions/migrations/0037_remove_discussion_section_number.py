# Generated by Django 4.1 on 2023-08-13 01:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("discussions", "0036_section_type"),
    ]

    operations = [
        migrations.RemoveField(model_name="discussion", name="section_number",),
    ]