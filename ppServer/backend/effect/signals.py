import math

from django.db.models.signals import pre_save, post_save, pre_delete, post_delete
from django.dispatch import receiver

from character.models.char import Charakter
from character.models.rel import RelAttribut, RelVorteil, RelNachteil, RelTalent, RelKlasse, RelKlasseAbility, RelGfsAbility
from character.models.relshop import RelBegleiter, RelMagische_Ausrüstung, RelRüstung, RelTechnik, RelEinbaute

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
@receiver(post_save, sender=RelTechnik)
@receiver(post_save, sender=RelEinbaute)
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
    elif sender in [RelBegleiter, RelMagische_Ausrüstung, RelRüstung, RelTechnik, RelEinbaute]:
        effect_qs = instance.item.effect_set.all()

    for effect in effect_qs:

        if not effect.has_custom_implementation:
            RelEffect.objects.create(
                effect=effect,
                target_char=instance.char,
            )
        else:
            if (sender == RelVorteil and effect.source_vorteil.titel == "Inselbegabung") or\
               (sender == RelNachteil and effect.source_nachteil.titel.startswith("Defizit")):
                RelEffect.create(
                    effect=effect,
                    target_char=instance.char,
                    target_attribut=RelAttribut.objects.get(char=instance.char, attribut=instance.attribut) if getattr(instance, "attribut", None) else None,
                )

            # HP durch Haustier-Fels
            if sender == RelBegleiter and effect.source_shopBegleiter.name == "Haustier-Fels":
                RelEffect.create(
                    effect=effect,
                    target_char=instance.char,
                    wertaenderung=effect.wertaenderung,
                    wertaenderung_str=effect.wertaenderung_str,
                )

                # apply_hp_effect_of_haustierfels(Charakter, instance.char)
                instance.char.save(update_fields=["HPplus_fix"])



########################## following: custom for Haustier-Fels #########################


@receiver(pre_save, sender=Charakter)
def apply_hp_effect_of_haustierfels(sender, instance, **kwargs):
    # not on create
    if instance.pk is None: return

    kHpPlus_fix_effects = instance.releffect_set.filter(is_active=True, effect__target_fieldname="character.Charakter.HPplus_fix")[:]
    first_effect = kHpPlus_fix_effects[0] if kHpPlus_fix_effects else None
    new_fix = None

    # Haustier-Fels is not / not the only one affecting the character's kHp plus fix
    if len(kHpPlus_fix_effects) != 1 or not getattr(first_effect.effect, "source_shopBegleiter", None) or first_effect.effect.source_shopBegleiter.name != "Haustier-Fels":
        new_fix = min([e.wert for e in kHpPlus_fix_effects]) if len(kHpPlus_fix_effects) else None

    # only Haustier-Fels
    else:
    
        # für jede char-Stufe oder 50 LARP-Ränge des Charakters 1 HP K.
        fels_hp = math.floor(instance.larp_rang / 50) if instance.larp else instance.ep_stufe

        # keep HPplus and add the benefit
        new_fix = instance.HPplus + fels_hp

        if fels_hp != first_effect.wert:
            fieldname = "wertaenderung_str" if first_effect.effect.target_fieldname.endswith("_str") else "wertaenderung"
            setattr(first_effect, fieldname, fels_hp)
            first_effect.save(update_fields=[fieldname])

    # update kHPplus_fix if changed
    if new_fix != instance.HPplus_fix:
        instance.HPplus_fix = new_fix
        instance.save(update_fields=["HPplus_fix"])

@receiver(post_delete, sender=RelEffect)
def deactivate_hp_effect_of_haustierfels_on_delete(sender, instance, **kwargs):
    if instance.effect.target_fieldname == "character.Charakter.HPplus_fix" and not instance.target_char.releffect_set.filter(effect__target_fieldname="character.Charakter.HPplus_fix").exists():

        # don't use char.save(update_fields=["HPplus_fix"]); char.save() here, because on char deletion the char/other char-relations are gone by now.
        # this query can execute even without an object selected by .filter()
        Charakter.objects.filter(pk=instance.target_char_id).update(HPplus_fix=None)