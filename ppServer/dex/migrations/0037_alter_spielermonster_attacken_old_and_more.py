# Generated by Django 4.2.8 on 2023-12-29 15:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dex', '0036_rename_attacken_spielermonster_attacken_old'),
    ]

    operations = [
        migrations.AlterField(
            model_name='spielermonster',
            name='attacken_old',
            field=models.ManyToManyField(related_name='attacken_old', to='dex.attacke'),
        ),
        migrations.CreateModel(
            name='SpielerMonsterAttack',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cost', models.PositiveSmallIntegerField()),
                ('attacke', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dex.attacke')),
                ('spieler_monster', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='dex.spielermonster')),
            ],
            options={
                'verbose_name': 'Attacke',
                'verbose_name_plural': 'Attacken',
                'unique_together': {('attacke', 'spieler_monster')},
            },
        ),
        migrations.AddField(
            model_name='spielermonster',
            name='attacken',
            field=models.ManyToManyField(through='dex.SpielerMonsterAttack', to='dex.attacke'),
        ),
    ]
