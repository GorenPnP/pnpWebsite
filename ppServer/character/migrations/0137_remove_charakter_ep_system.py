# Generated by Django 4.1.7 on 2023-09-10 10:32

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0136_remove_charakter_spezies_remove_relattribut_fg_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='charakter',
            name='ep_system',
        ),
    ]
