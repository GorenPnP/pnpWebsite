# Generated by Django 4.2.8 on 2024-01-29 16:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('lerneinheiten', '0002_alter_einheit_number'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='page',
            unique_together=set(),
        ),
    ]
