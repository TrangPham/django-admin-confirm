# Generated by Django 3.1.7 on 2021-03-04 03:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('market', '0008_item_description'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingmall',
            name='shops',
            field=models.ManyToManyField(blank=True, null=True, to='market.Shop'),
        ),
    ]