# Generated by Django 3.0.2 on 2020-02-20 04:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('acmerdata', '0025_auto_20200220_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='addstudentqueue',
            name='cfID',
            field=models.CharField(default='', max_length=100),
        ),
    ]
