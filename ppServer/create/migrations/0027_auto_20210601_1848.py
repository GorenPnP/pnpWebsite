# Generated by Django 3.1.5 on 2021-06-01 16:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0054_auto_20201223_1709'),
        ('create', '0026_auto_20210601_1814'),
    ]

    operations = [
        migrations.AlterField(
            model_name='gfscharacterization',
            name='gfs',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='character.gfs'),
        ),
    ]
