# Generated by Django 4.2.8 on 2024-05-24 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0145_spieler_language_daemonisch'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nachteil',
            name='needs_implementation',
        ),
        migrations.RemoveField(
            model_name='vorteil',
            name='needs_implementation',
        ),
        migrations.AddField(
            model_name='talent',
            name='has_implementation',
            field=models.BooleanField(default=False, verbose_name='ist implementiert'),
        ),
    ]