# Generated by Django 2.2.13 on 2020-09-07 13:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0021_auto_20200907_1331'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='module',
            options={'verbose_name': 'Module', 'verbose_name_plural': 'Modules'},
        ),
        migrations.AddField(
            model_name='module',
            name='num',
            field=models.FloatField(default=0, unique=True),
            preserve_default=False,
        ),
    ]
