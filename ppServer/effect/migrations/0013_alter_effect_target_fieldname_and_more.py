# Generated by Django 4.2.8 on 2024-05-28 14:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('effect', '0012_alter_effect_target_fieldname_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='effect',
            name='target_fieldname',
            field=models.CharField(choices=[('character.RelAttribut.aktuellerWert', 'Attribut: Wert'), ('character.RelAttribut.aktuellerWert_fix', 'Attribut: Wert fix'), ('character.RelAttribut.aktuellerWert_bonus', 'Attribut: Bonus'), ('character.RelAttribut.maxWert', 'Attribut: Maximum'), ('character.RelAttribut.maxWert_fix', 'Attribut: Maximum fix'), ('character.RelFertigkeit.fp', 'Fertigkeit: FP'), ('character.RelFertigkeit.fp_bonus', 'Fertigkeit: Bonus'), ('character.Charakter.ap', 'Charakter: AP'), ('character.Charakter.ip', 'Charakter: IP'), ('character.Charakter.fp', 'Charakter: FP'), ('character.Charakter.fg', 'Charakter: FG'), ('character.Charakter.tp', 'Charakter: TP'), ('character.Charakter.sp', 'Charakter: SP'), ('character.Charakter.sp_fix', 'Charakter: SP fix'), ('character.Charakter.geld', 'Charakter: Geld'), ('character.Charakter. Konto', 'Charakter: neuer Kontostand (-> Geld)'), ('character.Charakter.prestige', 'Charakter: Prestige'), ('character.Charakter.verzehr', 'Charakter: Verzehr'), ('character.Charakter.sanität', 'Charakter: Sanität'), ('character.Charakter.glück', 'Charakter: Glück'), ('character.Charakter.sonstiger_manifestverlust', 'Charakter: Manifestverlust'), ('character.Charakter.manifest_fix', 'Charakter: Manifest fix'), ('character.Charakter.limit_k_fix', 'Charakter: Limit k fix'), ('character.Charakter.limit_g_fix', 'Charakter: Limit g fix'), ('character.Charakter.limit_m_fix', 'Charakter: Limit m fix'), ('character.Charakter.HPplus', 'Charakter: kHP plus'), ('character.Charakter.HPplus_fix', 'Charakter: kHP plus fix'), ('character.Charakter.HPplus_geistig', 'Charakter: gHP plus'), ('character.Charakter.rang', 'Charakter: Rang'), ('character.Charakter.crit_attack', 'Charakter: Crit-Angriff'), ('character.Charakter.crit_defense', 'Charakter: Crit-Verteidigung'), ('character.Charakter.wesenschaden_waff_kampf', 'Charakter: Schaden waffenloser Kampf'), ('character.Charakter.wesenschaden_andere_gestalt', 'Charakter: Schaden waffenloser Kampf (andere Form)'), ('character.Charakter.konzentration', 'Charakter: Konzentration'), ('character.Charakter.konzentration_fix', 'Charakter: Konzentration fix'), ('character.Charakter.initiative_bonus', 'Charakter: Initiative-Bonus'), ('character.Charakter.reaktion_bonus', 'Charakter: Reaktionsbonus'), ('character.Charakter.natürlicher_schadenswiderstand_bonus', 'Charakter: nat. SchaWi-Bonus'), ('character.Charakter.natürlicher_schadenswiderstand_rüstung', 'Charakter: nat. SchaWi Rüstung'), ('character.Charakter.natSchaWi_pro_erfolg_bonus', 'Charakter: nat. SchaWi/Erfolg -Bonus'), ('character.Charakter.natSchaWi_pro_erfolg_rüstung', 'Charakter: nat. SchaWi/Erfolg -Rüstung'), ('character.Charakter.rüstung_haltbarkeit', 'Charakter: Rüstung Haltbarkeit'), ('character.Charakter.astralwiderstand_bonus', 'Charakter: AsWi-Bonus'), ('character.Charakter.manaoverflow_bonus', 'Charakter: Manaoverflow-Bonus'), ('character.Charakter.nat_regeneration_bonus', 'Charakter: nat. Regeneration-Bonus'), ('character.Charakter.immunsystem_bonus', 'Charakter: Immunsystem-Bonus')]),
        ),
        migrations.AlterField(
            model_name='releffect',
            name='target_fieldname',
            field=models.CharField(choices=[('character.RelAttribut.aktuellerWert', 'Attribut: Wert'), ('character.RelAttribut.aktuellerWert_fix', 'Attribut: Wert fix'), ('character.RelAttribut.aktuellerWert_bonus', 'Attribut: Bonus'), ('character.RelAttribut.maxWert', 'Attribut: Maximum'), ('character.RelAttribut.maxWert_fix', 'Attribut: Maximum fix'), ('character.RelFertigkeit.fp', 'Fertigkeit: FP'), ('character.RelFertigkeit.fp_bonus', 'Fertigkeit: Bonus'), ('character.Charakter.ap', 'Charakter: AP'), ('character.Charakter.ip', 'Charakter: IP'), ('character.Charakter.fp', 'Charakter: FP'), ('character.Charakter.fg', 'Charakter: FG'), ('character.Charakter.tp', 'Charakter: TP'), ('character.Charakter.sp', 'Charakter: SP'), ('character.Charakter.sp_fix', 'Charakter: SP fix'), ('character.Charakter.geld', 'Charakter: Geld'), ('character.Charakter. Konto', 'Charakter: neuer Kontostand (-> Geld)'), ('character.Charakter.prestige', 'Charakter: Prestige'), ('character.Charakter.verzehr', 'Charakter: Verzehr'), ('character.Charakter.sanität', 'Charakter: Sanität'), ('character.Charakter.glück', 'Charakter: Glück'), ('character.Charakter.sonstiger_manifestverlust', 'Charakter: Manifestverlust'), ('character.Charakter.manifest_fix', 'Charakter: Manifest fix'), ('character.Charakter.limit_k_fix', 'Charakter: Limit k fix'), ('character.Charakter.limit_g_fix', 'Charakter: Limit g fix'), ('character.Charakter.limit_m_fix', 'Charakter: Limit m fix'), ('character.Charakter.HPplus', 'Charakter: kHP plus'), ('character.Charakter.HPplus_fix', 'Charakter: kHP plus fix'), ('character.Charakter.HPplus_geistig', 'Charakter: gHP plus'), ('character.Charakter.rang', 'Charakter: Rang'), ('character.Charakter.crit_attack', 'Charakter: Crit-Angriff'), ('character.Charakter.crit_defense', 'Charakter: Crit-Verteidigung'), ('character.Charakter.wesenschaden_waff_kampf', 'Charakter: Schaden waffenloser Kampf'), ('character.Charakter.wesenschaden_andere_gestalt', 'Charakter: Schaden waffenloser Kampf (andere Form)'), ('character.Charakter.konzentration', 'Charakter: Konzentration'), ('character.Charakter.konzentration_fix', 'Charakter: Konzentration fix'), ('character.Charakter.initiative_bonus', 'Charakter: Initiative-Bonus'), ('character.Charakter.reaktion_bonus', 'Charakter: Reaktionsbonus'), ('character.Charakter.natürlicher_schadenswiderstand_bonus', 'Charakter: nat. SchaWi-Bonus'), ('character.Charakter.natürlicher_schadenswiderstand_rüstung', 'Charakter: nat. SchaWi Rüstung'), ('character.Charakter.natSchaWi_pro_erfolg_bonus', 'Charakter: nat. SchaWi/Erfolg -Bonus'), ('character.Charakter.natSchaWi_pro_erfolg_rüstung', 'Charakter: nat. SchaWi/Erfolg -Rüstung'), ('character.Charakter.rüstung_haltbarkeit', 'Charakter: Rüstung Haltbarkeit'), ('character.Charakter.astralwiderstand_bonus', 'Charakter: AsWi-Bonus'), ('character.Charakter.manaoverflow_bonus', 'Charakter: Manaoverflow-Bonus'), ('character.Charakter.nat_regeneration_bonus', 'Charakter: nat. Regeneration-Bonus'), ('character.Charakter.immunsystem_bonus', 'Charakter: Immunsystem-Bonus')]),
        ),
    ]