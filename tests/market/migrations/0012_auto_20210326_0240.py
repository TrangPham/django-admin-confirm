# Generated by Django 3.1.7 on 2021-03-26 02:40

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0011_auto_20210326_0130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(auto_created=True),
        ),
    ]
