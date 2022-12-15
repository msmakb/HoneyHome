# Generated by Django 4.1.3 on 2022-12-13 21:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_parameter_access_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='parameter',
            name='access_type',
            field=models.CharField(choices=[(1, 1), (2, 2), (3, 3)], db_column='access_type', default='0', editable=False, max_length=1),
        ),
    ]
