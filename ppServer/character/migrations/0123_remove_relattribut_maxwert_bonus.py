# Generated by Django 4.1.7 on 2023-07-29 12:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0122_remove_relattribut_fg_bonus'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='relattribut',
            name='maxWert_bonus',
        ),
    ]