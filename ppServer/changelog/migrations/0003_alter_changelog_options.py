# Generated by Django 4.1.7 on 2023-06-03 20:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('changelog', '0002_alter_changelog_timestamp'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='changelog',
            options={'ordering': ['-timestamp'], 'verbose_name': 'Changelog', 'verbose_name_plural': 'Changelogs'},
        ),
    ]
