# Generated by Django 2.2.13 on 2020-07-30 14:15

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0018_auto_20200730_1534'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='stzauber',
            name='preis_cp',
        ),
        migrations.RemoveField(
            model_name='zauber',
            name='preis_cp',
        ),
    ]
