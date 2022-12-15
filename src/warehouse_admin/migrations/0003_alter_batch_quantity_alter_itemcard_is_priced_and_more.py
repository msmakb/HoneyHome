# Generated by Django 4.1.1 on 2022-11-18 07:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('warehouse_admin', '0002_remove_itemcard_receiving_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='quantity',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='itemcard',
            name='is_priced',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='itemcard',
            name='is_transforming',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='itemcard',
            name='price',
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='itemcard',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='retailcard',
            name='weight',
            field=models.PositiveIntegerField(),
        ),
        migrations.AlterField(
            model_name='retailitem',
            name='price',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='retailitem',
            name='quantity',
            field=models.PositiveIntegerField(),
        ),
    ]
