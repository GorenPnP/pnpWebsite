# Generated by Django 2.2.13 on 2020-09-10 12:16

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0029_auto_20200910_1415'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='module',
            options={'ordering': ['num'], 'verbose_name': 'Module', 'verbose_name_plural': 'Modules'},
        ),
    ]
