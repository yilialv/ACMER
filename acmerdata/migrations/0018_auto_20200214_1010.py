# Generated by Django 3.0.2 on 2020-02-14 02:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acmerdata', '0017_studentgroup_enable'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentgroup',
            name='groupstuID',
            field=models.TextField(default='', max_length=330),
        ),
    ]
