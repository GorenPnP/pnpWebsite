# Generated by Django 2.2.14 on 2020-08-05 15:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0032_auto_20200805_1722'),
    ]

    operations = [
        migrations.AlterField(
            model_name='professionstufenplan',
            name='tp',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
