# Generated by Django 4.1.3 on 2023-02-12 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse_admin', '0010_damagedgoodshistory'),
    ]

    operations = [
        migrations.AlterField(
            model_name='retailitem',
            name='price',
            field=models.FloatField(blank=True, null=True),
        ),
    ]
