# Generated by Django 2.2.13 on 2020-11-30 16:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0052_auto_20200923_1257'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charakter',
            name='gfs',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.Gfs'),
        ),
    ]
