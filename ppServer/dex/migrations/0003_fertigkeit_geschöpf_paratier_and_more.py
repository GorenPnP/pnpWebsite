# Generated by Django 4.1.7 on 2023-11-28 18:25

import dex.models
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('dex', '0002_parapflanze_parapflanzenimage_parapflanze_images_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Fertigkeit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Geschöpf',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('number', models.PositiveSmallIntegerField(unique=True)),
                ('gefahrenklasse', models.PositiveSmallIntegerField(choices=[(1, 'Sicher'), (2, 'Bedenklich'), (3, 'Lethal'), (4, 'Hortend')], default=1)),
                ('verwahrungsklasse', models.PositiveSmallIntegerField(default=3, validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('status', models.PositiveSmallIntegerField(choices=[(1, 'Gefangen'), (2, 'Ausgebrochen'), (3, 'Noch Frei'), (4, 'Tot'), (5, 'Existenz Noch Unsicher')], default=5)),
                ('verhalten', models.TextField()),
                ('gefahren_fähigkeiten', models.TextField()),
                ('gefahrenprävention', models.TextField()),
                ('aufenthaltsort', models.TextField()),
                ('forschungsstand', models.TextField()),
                ('hp', models.PositiveSmallIntegerField()),
                ('reaktion', models.PositiveSmallIntegerField(default=0)),
                ('image', django_resized.forms.ResizedImageField(blank=True, crop=None, force_format=None, keep_meta=True, quality=-1, scale=None, size=[1024, 1024], upload_to=dex.models.upload_and_rename_to_id)),
            ],
            options={
                'verbose_name': 'Geschöpf',
                'verbose_name_plural': 'Geschöpfe',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='ParaTier',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=128)),
                ('image', django_resized.forms.ResizedImageField(blank=True, crop=None, force_format=None, keep_meta=True, quality=-1, scale=None, size=[1024, 1024], upload_to=dex.models.upload_and_rename_to_id)),
                ('description', models.TextField()),
                ('habitat', models.TextField()),
            ],
            options={
                'verbose_name': 'Para-Tier',
                'verbose_name_plural': 'Para-Tiere',
                'ordering': ['name'],
            },
        ),
        migrations.AlterModelOptions(
            name='parapflanzenimage',
            options={'ordering': ['plant', 'phase'], 'verbose_name': 'Para-Pflanzenbild', 'verbose_name_plural': 'Para-Pflanzenbilder'},
        ),
        migrations.RemoveField(
            model_name='parapflanze',
            name='images',
        ),
        migrations.AlterField(
            model_name='parapflanze',
            name='boden',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Weich'), (2, 'Mittel'), (3, 'Hart')], default=2),
        ),
        migrations.AlterField(
            model_name='parapflanze',
            name='größe',
            field=models.FloatField(default=1, help_text='in Metern', validators=[django.core.validators.MinValueValidator(0.001)]),
        ),
        migrations.AlterField(
            model_name='parapflanze',
            name='krankheitsanfälligkeit',
            field=models.SmallIntegerField(choices=[(1, 'Sehr Gering'), (2, 'Gering'), (3, 'Mäßig'), (4, 'Hoch'), (5, 'Sehr Hoch'), (6, 'Extrem Hoch')], default=3),
        ),
        migrations.AlterField(
            model_name='parapflanze',
            name='licht',
            field=models.PositiveSmallIntegerField(choices=[(1, '0/4'), (2, '1/4'), (3, '2/4'), (4, '3/4'), (5, '4/4')], default=3),
        ),
        migrations.AlterField(
            model_name='parapflanze',
            name='soziale_bedürfnisse',
            field=models.SmallIntegerField(default=0, help_text='von -3 bis 3', validators=[django.core.validators.MinValueValidator(-3), django.core.validators.MaxValueValidator(3)]),
        ),
        migrations.AlterField(
            model_name='parapflanze',
            name='wasser',
            field=models.PositiveSmallIntegerField(choices=[(1, 'Wenig'), (2, 'Mittel'), (3, 'Viel')], default=2),
        ),
        migrations.CreateModel(
            name='ParaTierFertigkeit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pool', models.PositiveSmallIntegerField(default=5, help_text='W6')),
                ('fertigkeit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dex.fertigkeit')),
                ('tier', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dex.paratier')),
            ],
            options={
                'verbose_name': 'Para-Tier',
                'verbose_name_plural': 'Para-Tiere',
                'ordering': ['tier', 'fertigkeit'],
            },
        ),
        migrations.AddField(
            model_name='paratier',
            name='fertigkeiten',
            field=models.ManyToManyField(through='dex.ParaTierFertigkeit', to='dex.fertigkeit'),
        ),
        migrations.CreateModel(
            name='GeschöpfFertigkeit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pool', models.PositiveSmallIntegerField(default=5, help_text='W6')),
                ('fertigkeit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dex.fertigkeit')),
                ('geschöpf', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dex.geschöpf')),
            ],
            options={
                'verbose_name': 'Fertigkeit (Geschöpf)',
                'verbose_name_plural': 'Fertigkeiten (Geschöpf)',
                'ordering': ['geschöpf', 'fertigkeit'],
            },
        ),
        migrations.AddField(
            model_name='geschöpf',
            name='fertigkeiten',
            field=models.ManyToManyField(through='dex.GeschöpfFertigkeit', to='dex.fertigkeit'),
        ),
        migrations.AddField(
            model_name='geschöpf',
            name='schaWI',
            field=models.ManyToManyField(to='dex.dice'),
        ),
    ]
