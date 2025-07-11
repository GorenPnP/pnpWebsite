# Generated by Django 4.2.8 on 2025-07-06 11:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('combat', '0003_alter_playerstats_unique_together'),
    ]

    operations = [
        migrations.CreateModel(
            name='RelWeapon',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('player_stats', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='combat.playerstats')),
                ('weapon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='combat.weapon')),
            ],
        ),
        migrations.AddField(
            model_name='playerstats',
            name='weapons',
            field=models.ManyToManyField(through='combat.RelWeapon', to='combat.weapon'),
        ),
    ]
