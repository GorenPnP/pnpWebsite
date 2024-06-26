# Generated by Django 4.2.8 on 2024-05-24 12:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('character', '0145_spieler_language_daemonisch'),
        ('effect', '0005_alter_releffect_options_alter_releffect_is_active'),
    ]

    operations = [
        migrations.AddField(
            model_name='effect',
            name='source_talent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='character.talent'),
        ),
        migrations.AddField(
            model_name='releffect',
            name='source_talent',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='character.reltalent'),
        ),
        migrations.AlterField(
            model_name='effect',
            name='target_fieldname',
            field=models.CharField(choices=[('character.RelAttribut.aktuellerWert', 'Attribut: Wert'), ('character.RelAttribut.aktuellerWert_fix', 'Attribut: Wert fix'), ('character.RelAttribut.aktuellerWert_bonus', 'Attribut: Bonus'), ('character.RelAttribut.maxWert', 'Attribut: Maximum'), ('character.RelAttribut.maxWert_fix', 'Attribut: Maximum fix'), ('character.RelFertigkeit.fp', 'Fertigkeit: FP'), ('character.RelFertigkeit.fp_bonus', 'Fertigkeit: Bonus'), ('character.Charakter.ap', 'Charakter: AP'), ('character.Charakter.ip', 'Charakter: IP'), ('character.Charakter.fp', 'Charakter: FP'), ('character.Charakter.fg', 'Charakter: FG'), ('character.Charakter.tp', 'Charakter: TP'), ('character.Charakter.sp', 'Charakter: SP'), ('character.Charakter.geld', 'Charakter: Geld'), ('character.Charakter.prestige', 'Charakter: Prestige'), ('character.Charakter.verzehr', 'Charakter: Verzehr'), ('character.Charakter.sanität', 'Charakter: Sanität'), ('character.Charakter.glück', 'Charakter: Glück'), ('character.Charakter.sonstiger_manifestverlust', 'Charakter: Manifest'), ('character.Charakter.HPplus', 'Charakter: kHP plus'), ('character.Charakter.HPplus_fix', 'Charakter: kHP plus fix'), ('character.Charakter.HPplus_geistig', 'Charakter: gHP plus'), ('character.Charakter.rang', 'Charakter: Rang'), ('character.Charakter.crit_attack', 'Charakter: Crit-Angriff'), ('character.Charakter.crit_defense', 'Charakter: Crit-Verteidigung'), ('character.Charakter.initiative_bonus', 'Charakter: Initiative-Bonus'), ('character.Charakter.reaktion_bonus', 'Charakter: Reaktionsbonus'), ('character.Charakter.natürlicher_schadenswiderstand_bonus', 'Charakter: nat. SchaWi-Bonus'), ('character.Charakter.astralwiderstand_bonus', 'Charakter: AsWi-Bonus'), ('character.Charakter.manaoverflow_bonus', 'Charakter: Manaoverflow-Bonus')]),
        ),
        migrations.AlterField(
            model_name='releffect',
            name='target_fieldname',
            field=models.CharField(choices=[('character.RelAttribut.aktuellerWert', 'Attribut: Wert'), ('character.RelAttribut.aktuellerWert_fix', 'Attribut: Wert fix'), ('character.RelAttribut.aktuellerWert_bonus', 'Attribut: Bonus'), ('character.RelAttribut.maxWert', 'Attribut: Maximum'), ('character.RelAttribut.maxWert_fix', 'Attribut: Maximum fix'), ('character.RelFertigkeit.fp', 'Fertigkeit: FP'), ('character.RelFertigkeit.fp_bonus', 'Fertigkeit: Bonus'), ('character.Charakter.ap', 'Charakter: AP'), ('character.Charakter.ip', 'Charakter: IP'), ('character.Charakter.fp', 'Charakter: FP'), ('character.Charakter.fg', 'Charakter: FG'), ('character.Charakter.tp', 'Charakter: TP'), ('character.Charakter.sp', 'Charakter: SP'), ('character.Charakter.geld', 'Charakter: Geld'), ('character.Charakter.prestige', 'Charakter: Prestige'), ('character.Charakter.verzehr', 'Charakter: Verzehr'), ('character.Charakter.sanität', 'Charakter: Sanität'), ('character.Charakter.glück', 'Charakter: Glück'), ('character.Charakter.sonstiger_manifestverlust', 'Charakter: Manifest'), ('character.Charakter.HPplus', 'Charakter: kHP plus'), ('character.Charakter.HPplus_fix', 'Charakter: kHP plus fix'), ('character.Charakter.HPplus_geistig', 'Charakter: gHP plus'), ('character.Charakter.rang', 'Charakter: Rang'), ('character.Charakter.crit_attack', 'Charakter: Crit-Angriff'), ('character.Charakter.crit_defense', 'Charakter: Crit-Verteidigung'), ('character.Charakter.initiative_bonus', 'Charakter: Initiative-Bonus'), ('character.Charakter.reaktion_bonus', 'Charakter: Reaktionsbonus'), ('character.Charakter.natürlicher_schadenswiderstand_bonus', 'Charakter: nat. SchaWi-Bonus'), ('character.Charakter.astralwiderstand_bonus', 'Charakter: AsWi-Bonus'), ('character.Charakter.manaoverflow_bonus', 'Charakter: Manaoverflow-Bonus')]),
        ),
    ]
