# Generated by Django 2.2.13 on 2020-08-15 15:55

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0024_remove_einbauten_manifestverlust'),
    ]

    operations = [
        migrations.RenameField(
            model_name='einbauten',
            old_name='manifestverlust_str',
            new_name='manifestverlust',
        ),
    ]
