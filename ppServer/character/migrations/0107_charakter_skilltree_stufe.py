# Generated by Django 4.1.7 on 2023-07-23 20:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0106_alter_charakter_tp'),
    ]

    operations = [
        migrations.AddField(
            model_name='charakter',
            name='skilltree_stufe',
            field=models.PositiveSmallIntegerField(default=1),
        ),
    ]
