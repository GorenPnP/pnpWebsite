# Generated by Django 4.1.7 on 2023-08-11 14:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0131_alter_charakter_gewicht'),
    ]

    operations = [
        migrations.AddField(
            model_name='nachteil',
            name='has_implementation',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='nachteil',
            name='needs_implementation',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vorteil',
            name='has_implementation',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='vorteil',
            name='needs_implementation',
            field=models.BooleanField(default=False),
        ),
    ]
