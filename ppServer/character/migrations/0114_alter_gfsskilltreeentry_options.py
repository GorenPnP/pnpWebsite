# Generated by Django 4.1.7 on 2023-07-25 17:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0113_gfsskilltreeentry_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='gfsskilltreeentry',
            options={'ordering': ['gfs', 'base', 'operation'], 'verbose_name': 'Gfs Skilltree', 'verbose_name_plural': 'Gfs Skilltrees'},
        ),
    ]
