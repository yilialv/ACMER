# Generated by Django 3.0.2 on 2020-02-16 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acmerdata', '0019_cfcontest'),
    ]

    operations = [
        migrations.AddField(
            model_name='cfcontest',
            name='ctime',
            field=models.IntegerField(default=0),
        ),
    ]