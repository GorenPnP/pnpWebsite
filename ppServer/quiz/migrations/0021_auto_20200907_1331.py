# Generated by Django 2.2.13 on 2020-09-07 11:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0020_auto_20200907_1255'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='prerequisite_modules',
            field=models.ManyToManyField(blank=True, null=True, to='quiz.Module'),
        ),
    ]
