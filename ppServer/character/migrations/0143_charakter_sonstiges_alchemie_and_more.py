# Generated by Django 4.2.8 on 2023-12-31 15:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0142_charakter_manaoverflow_bonus'),
    ]

    operations = [
        migrations.AddField(
            model_name='charakter',
            name='sonstiges_alchemie',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AddField(
            model_name='charakter',
            name='sonstiges_cyberware',
            field=models.TextField(blank=True, default=''),
        ),
        migrations.AlterField(
            model_name='charakter',
            name='sonstige_items',
            field=models.TextField(blank=True, default=''),
        ),
    ]
