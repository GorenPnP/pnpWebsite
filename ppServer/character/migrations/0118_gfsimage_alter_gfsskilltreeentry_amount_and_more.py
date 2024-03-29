# Generated by Django 4.1.7 on 2023-07-26 11:31

from django.db import migrations, models
import django.db.models.deletion
import django_resized.forms


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0117_remove_wesenkraft_min_rang_charakter_hpplus_geistig_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='GfsImage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('order', models.FloatField(default=1.0)),
                ('img', django_resized.forms.ResizedImageField(crop=None, force_format=None, keep_meta=True, quality=-1, scale=None, size=[1024, 1024], upload_to='')),
                ('text', models.TextField(blank=True, null=True)),
                ('gfs', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='character.gfs')),
            ],
            options={
                'verbose_name': 'Bild',
                'verbose_name_plural': 'Bilder',
                'ordering': ['gfs', 'order'],
            },
        ),
        migrations.AlterField(
            model_name='gfsskilltreeentry',
            name='amount',
            field=models.SmallIntegerField(blank=True, help_text='für AP, FP, FG, SP, IP, TP und Anz. Zauber-slots, WP in Speizis/Wissis, Fertigkeitsboni, Crit und HP', null=True),
        ),
        migrations.AlterField(
            model_name='gfsskilltreeentry',
            name='fertigkeit',
            field=models.ForeignKey(blank=True, help_text='für Bonus in Fertigkeit und  ggf. Vor-/Nachteile wie Spezialisiert, die eine Fertigkeit brauchen.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.fertigkeit'),
        ),
        migrations.AlterField(
            model_name='gfsskilltreeentry',
            name='operation',
            field=models.CharField(choices=[('a', 'AP'), ('f', 'FP'), ('F', 'FG'), ('p', 'SP'), ('i', 'IP'), ('t', 'TP'), ('z', 'Zauberslot/s'), ('v', 'neuer Vorteil'), ('n', 'neuer Nachteil'), ('e', 'neue Wesenkraft'), ('s', 'neue Spezialfertigkeit'), ('w', 'neue Wissensfertigkeit'), ('S', 'WP in Spezialfertigkeit'), ('W', 'WP in Wissensfertigkeit'), ('B', 'Bonus in Fertigkeit'), ('A', 'Crit-Angriff'), ('V', 'Crit-Verteidigung'), ('K', 'körperliche HP'), ('G', 'geistige HP'), ('k', 'HP Schaden waff. Kampf'), ('I', 'Initiative fix'), ('r', 'Reaktion'), ('N', 'natürlicher Schadenswiderstand'), ('T', 'Astral-Widerstand'), ('h', 'magisches Item'), ('R', 'Roleplay-Text')], default='R', help_text='wichtigstes Feld, bestimmt die Art des Eintrags und welche anderen Felder benötigt werden.', max_length=1),
        ),
        migrations.AlterField(
            model_name='gfsskilltreeentry',
            name='spezialfertigkeit',
            field=models.ForeignKey(blank=True, help_text='Für neue Spezi oder WP in einer Spezi', null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.spezialfertigkeit'),
        ),
        migrations.AlterField(
            model_name='gfsskilltreeentry',
            name='stufe',
            field=models.SmallIntegerField(blank=True, help_text='für Zauber-slots und Stufen von Items', null=True),
        ),
        migrations.AlterField(
            model_name='gfsskilltreeentry',
            name='text',
            field=models.TextField(blank=True, help_text='für Vor-/Nachteilnotizen und alles nicht-implementierbare, z. B. Bonuseffekte bei Angriffen', null=True),
        ),
        migrations.AlterField(
            model_name='gfsskilltreeentry',
            name='wissensfertigkeit',
            field=models.ForeignKey(blank=True, help_text='Für neue Wissi oder WP in einer Wissi', null=True, on_delete=django.db.models.deletion.SET_NULL, to='character.wissensfertigkeit'),
        ),
        migrations.DeleteModel(
            name='SkilltreeEntryGfs',
        ),
    ]
