from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver

from character.models import RelAttribut, RelFertigkeit, RelVorteil, RelNachteil, RelTalent

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
def apply_effect_on_rel_relation(sender, instance, created, **kwargs):
    if not created: return

    effect_qs = []
    if sender in [RelVorteil, RelNachteil]:
        effect_qs = instance.teil.effect_set.all()
    elif sender == RelTalent:
        effect_qs = instance.talent.effect_set.all()

    for effect in effect_qs:
        instance.releffect_set.create(
            target_fieldname=effect.target_fieldname,
            wertaenderung=effect.wertaenderung,
            target_char=instance.char,
            target_attribut=RelAttribut.objects.get(char=instance.char, attribut=effect.target_attribut) if getattr(effect, "target_attribut", None) else None,
            target_fertigkeit=RelFertigkeit.objects.get(char=instance.char, fertigkeit=effect.target_fertigkeit) if getattr(effect, "target_fertigkeit", None) else None,
        )