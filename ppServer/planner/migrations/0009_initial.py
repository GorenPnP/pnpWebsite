# Generated by Django 3.2.16 on 2022-11-19 13:07

import datetime
from django.db import migrations, models
import django.db.models.deletion
import planner.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('character', '0064_gfsstufenplanbase_tp'),
        ('planner', '0008_auto_20221119_1407'),
    ]

    operations = [
        migrations.CreateModel(
            name='Appointment',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('start', models.TimeField(default=datetime.datetime.now, unique=True)),
            ],
            options={
                'verbose_name': 'Termin',
                'verbose_name_plural': 'Termine',
            },
        ),
        migrations.CreateModel(
            name='AppointmentNegotiation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.datetime.today, unique=True)),
                ('open_for_participation', models.BooleanField(default=True)),
                ('appointment', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='planner.appointment')),
            ],
            options={
                'verbose_name': 'Terminabsprache',
                'verbose_name_plural': 'Terminabsprachen',
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='BlockedTime',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=200, null=True)),
                ('date', models.DateField(default=datetime.datetime.today, unique=True)),
                ('start', models.TimeField(default=planner.models.min_time)),
                ('end', models.TimeField(default=planner.models.max_time)),
            ],
            options={
                'verbose_name': 'Blockierter Zeitraum',
                'verbose_name_plural': 'Blockierte Zeiträume',
                'ordering': ['date'],
            },
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True)),
            ],
            options={
                'verbose_name': 'Tag',
                'verbose_name_plural': 'Tags',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Weekday',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField(unique=True)),
                ('name', models.CharField(max_length=20, unique=True)),
                ('short_name', models.CharField(max_length=2, unique=True)),
            ],
            options={
                'verbose_name': 'Wochentag',
                'verbose_name_plural': 'Wochentage',
                'ordering': ['order'],
            },
        ),
        migrations.CreateModel(
            name='Proposal',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.PositiveSmallIntegerField()),
                ('start', models.TimeField(default=planner.models.default_time)),
                ('note', models.TextField(blank=True, null=True)),
                ('appointment_negotiation', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='planner.appointmentnegotiation')),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.spieler')),
            ],
            options={
                'verbose_name': 'Terminvorschlag',
                'verbose_name_plural': 'Terminvorschläge',
            },
        ),
        migrations.AddField(
            model_name='appointmentnegotiation',
            name='players',
            field=models.ManyToManyField(through='planner.Proposal', to='character.Spieler'),
        ),
        migrations.AddField(
            model_name='appointment',
            name='tags',
            field=models.ManyToManyField(to='planner.Tag'),
        ),
    ]
