# Generated by Django 3.1.6 on 2021-02-24 08:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("market", "0007_generalmanager_headshot"),
    ]

    operations = [
        migrations.AddField(
            model_name="item",
            name="description",
            field=models.TextField(blank=True, null=True),
        ),
    ]
