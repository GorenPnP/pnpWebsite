# Generated by Django 3.1.7 on 2022-08-29 20:31

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('shop', '0045_auto_20220527_1348'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShopCategory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('kategorie', models.CharField(choices=[('i', 'Items'), ('w', 'Waffen & Werkzeuge'), ('m', 'Magazine'), ('p', 'Pfeile & Bolzen'), ('s', 'Schusswaffen'), ('a', 'Magische Ausrüstung'), ('r', 'Rituale & Runen'), ('u', 'Rüstungen'), ('f', 'Fahrzeuge'), ('e', 'Einbauten'), ('z', 'Zauber'), ('v', 'Vergessene Zauber'), ('l', 'Alchemie'), ('b', 'Begleiter'), ('t', 'Für Selbstständige')], default='i', max_length=1, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Modifier',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('prio', models.FloatField(default=100, unique=True, validators=[django.core.validators.MinValueValidator(1.0)])),
                ('price_modifier', models.FloatField(default=1.0, validators=[django.core.validators.MinValueValidator(0.0)])),
                ('is_factor_not_addition', models.BooleanField(default=True)),
                ('firmen', models.ManyToManyField(to='shop.Firma')),
                ('kategorien', models.ManyToManyField(to='shop.ShopCategory')),
            ],
            options={
                'verbose_name': 'Modifier',
                'verbose_name_plural': 'Modifier',
                'ordering': ['prio'],
            },
        ),
    ]