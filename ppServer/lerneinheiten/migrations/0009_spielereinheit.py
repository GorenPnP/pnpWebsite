# Generated by Django 4.2.8 on 2024-04-28 13:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0144_remove_charakter_sonstiges_alchemie_and_more'),
        ('lerneinheiten', '0008_pageimage_spielerpage'),
    ]

    operations = [
        migrations.CreateModel(
            name='SpielerEinheit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('einheit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='lerneinheiten.einheit')),
                ('spieler', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.spieler')),
            ],
        ),
    ]