# Generated by Django 2.0.5 on 2018-11-19 19:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('create', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='newcharakter',
            name='wesenschaden_waff_kampf',
            field=models.IntegerField(default=0, verbose_name='Basisschaden'),
        ),
    ]
