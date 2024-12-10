import math

from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver

from character.models import RelAttribut, RelFertigkeit, RelVorteil, RelNachteil, RelTalent, RelKlasse, RelKlasseAbility, RelGfsAbility, RelBegleiter, RelMagische_Ausrüstung, RelRüstung, RelAusrüstung_Technik, RelEinbauten, Charakter

from .models import *


@receiver(pre_save, sender=RelEffect)
def de_activate_effect_on_save(sender, instance, **kwargs):
    old_instance = sender.objects.filter(id=instance.id).first()
    
    if (not old_instance and instance.is_active) or\
       (old_instance and not old_instance.is_active and instance.is_active):
        instance.activate(False)

    if old_instance and old_instance.is_active and not instance.is_active:
        instance.deactivate(False)


@receiver(pre_delete, sender=RelEffect)
def deactivate_effect_on_delete(sender, instance, **kwargs):
    if instance.is_active:
        instance.deactivate(False)


@receiver(post_save, sender=RelVorteil)
@receiver(post_save, sender=RelNachteil)
@receiver(post_save, sender=RelTalent)
@receiver(post_save, sender=RelGfsAbility)
@receiver(post_save, sender=RelKlasse)
@receiver(post_save, sender=RelKlasseAbility)
@receiver(post_save, sender=RelBegleiter)
@receiver(post_save, sender=RelMagische_Ausrüstung)
@receiver(post_save, sender=RelRüstung)
@receiver(post_save, sender=RelAusrüstung_Technik)
@receiver(post_save, sender=RelEinbauten)
def apply_effect_on_rel_relation(sender, instance, created, **kwargs):
    if not created or\
        ("effect_signals" in instance.char.processing_notes and instance.char.processing_notes["effect_signals"] == "ignore"):
         return

    effect_qs = []
    if sender in [RelVorteil, RelNachteil]:
        effect_qs = instance.teil.effect_set.all()
    elif sender == RelTalent:
        effect_qs = instance.talent.effect_set.all()
    elif sender in [RelGfsAbility, RelKlasseAbility]: 
        effect_qs = instance.ability.effect_set.all()
    elif sender == RelKlasse: 
        effect_qs = instance.klasse.effect_set.all()
    elif sender in [RelBegleiter, RelMagische_Ausrüstung, RelRüstung, RelAusrüstung_Technik, RelEinbauten]:
        effect_qs = instance.item.effect_set.all()

    for effect in effect_qs:

        if not effect.has_custom_implementation:
            instance.releffect_set.create(
                target_fieldname=effect.target_fieldname,
                wertaenderung=effect.wertaenderung,
                target_char=instance.char,
                target_attribut=RelAttribut.objects.get(char=instance.char, attribut=effect.target_attribut) if getattr(effect, "target_attribut", None) else None,
                target_fertigkeit=RelFertigkeit.objects.get(char=instance.char, fertigkeit=effect.target_fertigkeit) if getattr(effect, "target_fertigkeit", None) else None,
            )
        else:
            if sender == RelNachteil and effect.source_nachteil.titel.startswith("Defizit"):
                instance.releffect_set.create(
                    target_fieldname=effect.target_fieldname,
                    wertaenderung=effect.wertaenderung,
                    target_char=instance.char,
                    target_attribut=RelAttribut.objects.get(char=instance.char, attribut=instance.attribut) if getattr(instance, "attribut", None) else None,
                    target_fertigkeit=RelFertigkeit.objects.get(char=instance.char, fertigkeit=effect.target_fertigkeit) if getattr(effect, "target_fertigkeit", None) else None,
                )

            if sender == RelVorteil and effect.source_vorteil.titel == "Inselbegabung":
                instance.releffect_set.create(
                    target_fieldname=effect.target_fieldname,
                    wertaenderung=effect.wertaenderung,
                    target_char=instance.char,
                    target_attribut=RelAttribut.objects.get(char=instance.char, attribut=instance.attribut) if getattr(instance, "attribut", None) else None,
                    target_fertigkeit=RelFertigkeit.objects.get(char=instance.char, fertigkeit=effect.target_fertigkeit) if getattr(effect, "target_fertigkeit", None) else None,
                )

            # HP durch Haustier-Fels
            if sender == RelBegleiter and effect.source_shopBegleiter.name == "Haustier-Fels":
                instance.releffect_set.create(
                    target_fieldname=effect.target_fieldname,
                    wertaenderung=effect.wertaenderung,
                    target_char=instance.char,
                    target_attribut=RelAttribut.objects.get(char=instance.char, attribut=effect.target_attribut) if getattr(effect, "target_attribut", None) else None,
                    target_fertigkeit=RelFertigkeit.objects.get(char=instance.char, fertigkeit=effect.target_fertigkeit) if getattr(effect, "target_fertigkeit", None) else None,
                )

                # apply_hp_effect_of_haustierfels(Charakter, instance.char)
                instance.char.save(update_fields=["HPplus_fix"])


            # wertaenderung = item-Stufe
            if sender == RelMagische_Ausrüstung and effect.source_shopMagischeAusrüstung.name in ["Astralblocker", "Magiefokus", "Spruchzaubereifokus", "Dunkelmagiefokus", "Ritualfokus", "Antimagiefokus", "Alchemiefokus"]:
                instance.releffect_set.create(
                    target_fieldname=effect.target_fieldname,
                    wertaenderung=instance.stufe,
                    target_char=instance.char,
                    target_attribut=RelAttribut.objects.get(char=instance.char, attribut=effect.target_attribut) if getattr(effect, "target_attribut", None) else None,
                    target_fertigkeit=RelFertigkeit.objects.get(char=instance.char, fertigkeit=effect.target_fertigkeit) if getattr(effect, "target_fertigkeit", None) else None,
                )

            # wertaenderung = 2* min(item-Stufe, 5)
            if sender == RelEinbauten and effect.source_shopEinbauten.name == "Panzerimplantate":
                instance.releffect_set.create(
                    target_fieldname=effect.target_fieldname,
                    wertaenderung=2* min(instance.stufe, 5),
                    target_char=instance.char,
                    target_attribut=RelAttribut.objects.get(char=instance.char, attribut=effect.target_attribut) if getattr(effect, "target_attribut", None) else None,
                    target_fertigkeit=RelFertigkeit.objects.get(char=instance.char, fertigkeit=effect.target_fertigkeit) if getattr(effect, "target_fertigkeit", None) else None,
                )

            # wertaenderung = min(item-Stufe, 10)
            if sender == RelEinbauten and effect.source_shopEinbauten.name == "Sense-KIT":
                instance.releffect_set.create(
                    target_fieldname=effect.target_fieldname,
                    wertaenderung=min(instance.stufe, 10),
                    target_char=instance.char,
                    target_attribut=RelAttribut.objects.get(char=instance.char, attribut=effect.target_attribut) if getattr(effect, "target_attribut", None) else None,
                    target_fertigkeit=RelFertigkeit.objects.get(char=instance.char, fertigkeit=effect.target_fertigkeit) if getattr(effect, "target_fertigkeit", None) else None,
                )

            # wertaenderung = min(item-Stufe, 3)
            if sender == RelEinbauten and effect.source_shopEinbauten.name in ["Motivationsbooster", "Hirnbooster", "Hormonpumpe", "Reflexbeschleuniger"]:
                instance.releffect_set.create(
                    target_fieldname=effect.target_fieldname,
                    wertaenderung=min(instance.stufe, 3),
                    target_char=instance.char,
                    target_attribut=RelAttribut.objects.get(char=instance.char, attribut=effect.target_attribut) if getattr(effect, "target_attribut", None) else None,
                    target_fertigkeit=RelFertigkeit.objects.get(char=instance.char, fertigkeit=effect.target_fertigkeit) if getattr(effect, "target_fertigkeit", None) else None,
                )

            # wertaenderung = 10 * min(item-Stufe, 3)
            if sender == RelEinbauten and effect.source_shopEinbauten.name == "Manareservator":
                instance.releffect_set.create(
                    target_fieldname=effect.target_fieldname,
                    wertaenderung=10 * min(instance.stufe, 3),
                    target_char=instance.char,
                    target_attribut=RelAttribut.objects.get(char=instance.char, attribut=effect.target_attribut) if getattr(effect, "target_attribut", None) else None,
                    target_fertigkeit=RelFertigkeit.objects.get(char=instance.char, fertigkeit=effect.target_fertigkeit) if getattr(effect, "target_fertigkeit", None) else None,
                )


########################## following: custom for Haustier-Fels #########################


@receiver(pre_save, sender=Charakter)
def apply_hp_effect_of_haustierfels(sender, instance, **kwargs):
    # not on create
    if instance.pk is None: return

    kHpPlus_fix_effects = instance.releffect_set.filter(is_active=True, target_fieldname="character.Charakter.HPplus_fix")

    # Haustierfels is the only one affecting the character's kHp plus fix?
    if kHpPlus_fix_effects.count() != 1 or not getattr(kHpPlus_fix_effects.first(), "source_shopBegleiter", None) or getattr(kHpPlus_fix_effects.first(), "source_shopBegleiter", None).item.name != "Haustier-Fels":
        return
    
    #  für alle 1.000 EP oder 10 LARP-Ränge des Charakters +1% HP K (max. 100%).
    factor: float = min(math.floor(instance.ep / 1000) / 100, 1) + min(math.floor(instance.larp_rang / 10) / 100, 1)

    kHp_without_fels = sum([
        int(instance.relattribut_set.get(attribut__titel="ST").aktuell() * 5),
        int(math.floor(instance.larp_rang / 20) if instance.larp else instance.ep_stufe * 2),
        int(math.floor(instance.rang / 10)),
        int(instance.HPplus),
    ])

    # keep HPplus and add the benefit by factor
    new_fix = instance.HPplus + int(math.floor(kHp_without_fels * factor + 0.5))
    if new_fix != instance.HPplus_fix:
        instance.HPplus_fix = new_fix
        instance.save(update_fields=["HPplus_fix"])

@receiver(post_delete, sender=RelEffect)
def deactivate_hp_effect_of_haustierfels_on_delete(sender, instance, **kwargs):
    if instance.target_fieldname == "character.Charakter.HPplus_fix" and not instance.target_char.releffect_set.filter(target_fieldname="character.Charakter.HPplus_fix").exists():

        # don't use char.save(update_fields=["HPplus_fix"]); char.save() here, because on char deletion the char/other char-relations are gone by now.
        # this query can execute even without an object selected by .filter()
        Charakter.objects.filter(pk=instance.target_char_id).update(HPplus_fix=None)