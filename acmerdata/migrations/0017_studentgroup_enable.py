# Generated by Django 3.0.2 on 2020-02-14 02:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acmerdata', '0016_auto_20200213_2026'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentgroup',
            name='enable',
            field=models.BooleanField(default=True),
        ),
    ]
