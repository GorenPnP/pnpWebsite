# Generated by Django 4.2.8 on 2024-10-27 18:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0155_remove_spieler_language_daemonisch'),
    ]

    operations = [
        migrations.CreateModel(
            name='Klasse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('titel', models.CharField(default='', max_length=30)),
                ('beschreibung', models.TextField()),
            ],
            options={
                'verbose_name': 'Klasse',
                'verbose_name_plural': 'Klassen',
                'ordering': ['titel'],
            },
        ),
        migrations.AlterModelOptions(
            name='gfs',
            options={'ordering': ['titel'], 'verbose_name': 'Gfs/Genere', 'verbose_name_plural': 'Gfs/Genere'},
        ),
        migrations.CreateModel(
            name='RelKlasse',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stufe', models.PositiveSmallIntegerField(default=1)),
                ('char', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.charakter')),
                ('klasse', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.klasse')),
            ],
            options={
                'verbose_name': 'Klasse',
                'verbose_name_plural': 'Klassen',
                'ordering': ['char', 'klasse'],
                'unique_together': {('char', 'klasse')},
            },
        ),
    ]