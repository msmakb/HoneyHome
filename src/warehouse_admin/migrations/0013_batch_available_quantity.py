# Generated by Django 4.1.3 on 2023-02-12 16:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse_admin', '0012_itemtype_is_retail_child_itemtype_retail_child_of'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='available_quantity',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
