# Generated by Django 2.2.13 on 2020-08-15 15:12

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('create', '0016_auto_20200813_0438'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='newcharakter',
            name='gratis_st_zauber',
        ),
        migrations.DeleteModel(
            name='NewCharakterStZauber',
        ),
    ]
