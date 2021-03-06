# Generated by Django 2.2.13 on 2020-09-10 12:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0026_auto_20200910_1401'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='spielermodule',
            options={'ordering': ['spieler', 'state'], 'verbose_name': "Spieler's Module", 'verbose_name_plural': "Spieler's Module"},
        ),
        migrations.AlterField(
            model_name='spielermodule',
            name='answered_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
