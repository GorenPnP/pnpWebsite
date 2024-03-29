# Generated by Django 4.1.7 on 2023-07-19 12:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0095_charakter_processing_notes'),
    ]

    operations = [
        migrations.CreateModel(
            name='GfsAbility',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, default=None, max_length=100, null=True, verbose_name='Fähigkeit')),
                ('beschreibung', models.TextField(blank=True, default=None, max_length=2000, null=True, verbose_name='Beschreibung')),
                ('needs_implementation', models.BooleanField(default=False)),
                ('has_choice', models.BooleanField(default=False)),
                ('notizen', models.TextField(blank=True, null=True)),
            ],
            options={
                'verbose_name': 'Gfs-Fähigkeit',
                'verbose_name_plural': 'Gfs-Fähigkeiten',
                'ordering': ['name'],
                'unique_together': {('name',)},
            },
        ),
        migrations.AddField(
            model_name='gfsstufenplan',
            name='ability',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.gfsability'),
        ),
    ]
