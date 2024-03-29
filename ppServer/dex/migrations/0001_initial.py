# Generated by Django 4.1.7 on 2023-11-28 15:57

import dex.models
import django.core.validators
from django.db import migrations, models
import django_resized.forms


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('character', '0142_charakter_manaoverflow_bonus'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attacke',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128, unique=True)),
                ('description', models.TextField()),
                ('macht_schaden', models.BooleanField(default=False)),
                ('macht_effekt', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'Attacke',
                'verbose_name_plural': 'Attacken',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Dice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('amount', models.SmallIntegerField(default=1)),
                ('type', models.CharField(choices=[('W2', 'W2'), ('W4', 'W4'), ('W6', 'W6'), ('W8', 'W8'), ('W10', 'W10'), ('W12', 'W12'), ('W20', 'W20'), ('W100', 'W100')], max_length=4)),
            ],
            options={
                'verbose_name': 'Dice',
                'verbose_name_plural': 'Dice',
                'ordering': ['type', 'amount'],
                'unique_together': {('amount', 'type')},
            },
        ),
        migrations.CreateModel(
            name='Typ',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('icon', django_resized.forms.ResizedImageField(crop=None, force_format=None, keep_meta=True, quality=-1, scale=None, size=[256, 256], upload_to=dex.models.upload_and_rename_to_id)),
                ('name', models.CharField(max_length=128)),
                ('schwach_gegen', models.ManyToManyField(blank=True, related_name='schwach', related_query_name='schwach', to='dex.typ')),
                ('stark_gegen', models.ManyToManyField(blank=True, related_name='stark', related_query_name='stark', to='dex.typ')),
                ('trifft_nicht', models.ManyToManyField(blank=True, related_name='miss', related_query_name='miss', to='dex.typ')),
            ],
            options={
                'verbose_name': 'Typ',
                'verbose_name_plural': 'Typen',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Monster',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', django_resized.forms.ResizedImageField(crop=None, force_format=None, keep_meta=True, quality=-1, scale=None, size=[1024, 1024], upload_to=dex.models.upload_and_rename_to_id)),
                ('number', models.PositiveSmallIntegerField(unique=True)),
                ('name', models.CharField(max_length=128)),
                ('description', models.TextField()),
                ('habitat', models.TextField()),
                ('wildrang', models.PositiveIntegerField(default=1, validators=[django.core.validators.MinValueValidator(1)])),
                ('weight', models.FloatField(default=1, help_text='in kg', validators=[django.core.validators.MinValueValidator(0.001)])),
                ('height', models.FloatField(default=1, help_text='in Metern', validators=[django.core.validators.MinValueValidator(0.001)])),
                ('base_hp', models.PositiveIntegerField(default=1)),
                ('alternativeForms', models.ManyToManyField(blank=True, related_name='forms', related_query_name='forms', to='dex.monster')),
                ('attacken', models.ManyToManyField(blank=True, to='dex.attacke')),
                ('base_schadensWI', models.ManyToManyField(to='dex.dice')),
                ('evolutionPost', models.ManyToManyField(blank=True, related_name='evolution_post', related_query_name='evolution_post', to='dex.monster')),
                ('evolutionPre', models.ManyToManyField(blank=True, related_name='evolution_pre', related_query_name='evolution_pre', to='dex.monster')),
                ('opposites', models.ManyToManyField(blank=True, related_name='opposite', related_query_name='opposite', to='dex.monster')),
                ('types', models.ManyToManyField(blank=True, to='dex.typ')),
                ('visible', models.ManyToManyField(blank=True, to='character.spieler')),
            ],
            options={
                'verbose_name': 'Monster',
                'verbose_name_plural': 'Monster',
                'ordering': ['number'],
            },
        ),
        migrations.AddField(
            model_name='attacke',
            name='damage',
            field=models.ManyToManyField(blank=True, to='dex.dice'),
        ),
        migrations.AddField(
            model_name='attacke',
            name='types',
            field=models.ManyToManyField(to='dex.typ'),
        ),
    ]
