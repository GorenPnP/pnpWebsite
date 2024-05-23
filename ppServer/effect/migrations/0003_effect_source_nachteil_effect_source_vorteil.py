# Generated by Django 4.2.8 on 2024-05-21 16:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0145_spieler_language_daemonisch'),
        ('effect', '0002_alter_effect_target_attribut_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='effect',
            name='source_nachteil',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='character.nachteil'),
        ),
        migrations.AddField(
            model_name='effect',
            name='source_vorteil',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='character.vorteil'),
        ),
    ]
