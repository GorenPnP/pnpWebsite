# Generated by Django 4.1.7 on 2023-12-16 18:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dex', '0011_monster_base_attackbonus_monster_base_reaktionsbonus_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MonsterRang',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('rang', models.PositiveSmallIntegerField(unique=True)),
                ('hp', models.PositiveSmallIntegerField(default=0)),
                ('reaktionsbonus', models.PositiveSmallIntegerField(default=0)),
                ('angriffsbonus', models.PositiveSmallIntegerField(default=0)),
                ('schadensWI', models.ManyToManyField(blank=True, to='dex.dice')),
            ],
            options={
                'verbose_name': 'Monster-Rang',
                'verbose_name_plural': 'Monster-Ränge',
                'ordering': ['rang'],
            },
        ),
    ]