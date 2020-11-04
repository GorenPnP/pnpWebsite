
from django.db.models.signals import pre_save, pre_delete, post_save
from django.dispatch import receiver

from character.models import Spieler
from .models import Image, File, ModuleQuestion, SpielerSession, Module, module_state, Question, SpielerModule


# to save the old picture-name in answer_note, before changed (against cheating)
@receiver(pre_save, sender=Image)
@receiver(pre_save, sender=File)
def save_picture_name(sender, instance, **kwargs):
    # shouldn't ever happen
    if not instance:
        return
    old_instance = sender.objects.filter(id=instance.id)

    # fresh instance should old one not exist
    old_instance = None if old_instance.count() == 0 else old_instance[0]
    new_instance = instance

    # same saved again?
    if old_instance and ((sender == Image and old_instance.img == new_instance.img) or
                         (sender == File and old_instance.file == new_instance.file)):
        return

    # remove old Name-information and add new one
    if sender == Image:
        new_instance.name = new_instance.img.name if new_instance.img and new_instance.img.name else None
    else:
        new_instance.name = new_instance.file.name if new_instance.file and new_instance.file.name else None


# following: update module.max_points on:
#   add, delete of question-module relation
#   save of any question

# basically on new relation to module
@receiver(pre_save, sender=ModuleQuestion)
def update_max_points(sender, instance, **kwargs):
    # shouldn't ever happen
    if not instance:
        return

    old_instance = sender.objects.filter(id=instance.id)
    if not old_instance.exists():
        module = instance.module
        module.max_points += instance.question.points
        module.save()


@receiver(pre_delete, sender=ModuleQuestion)
def decrease_max_points(sender, instance, **kwargs):
    # shouldn't ever happen
    if not instance:
        return

    module = instance.module
    module.max_points -= instance.question.points
    module.save()


@receiver(pre_save, sender=Question)
def update_max_points_of_module(sender, instance, **kwargs):
    # shouldn't ever happen
    if not instance:
        return

    # is newly instantiated, cannot have a relation to a module
    old_instance = sender.objects.filter(id=instance.id)
    if not old_instance.exists():
        return

    mq = ModuleQuestion.objects.filter(question=instance)

    # no relation detected
    if not mq.exists():
        return

    for e in mq:
        e.module.max_points += instance.points - old_instance[0].points
        e.module.save()


@receiver(post_save, sender=SpielerSession)
def add_questions(sender, instance, **kwargs):
    if not kwargs["created"]:
        return

    for q in instance.spielerModule.module.questions.all():
        instance.questions.create(
            spieler=instance.spielerModule.spieler, question=q)


# works recursively, should a sp_mod's state be set from locked to unlocked
@receiver(post_save, sender=Module)
def add_spielermodules(sender, instance, **kwargs):

    modules = Module.objects.exclude(id=instance.id)
    sp_mods = []

    # create all missing sp_mods
    for p in Spieler.objects.all():

        sp_mod, _ = SpielerModule.objects.get_or_create(spieler=p, module=instance)
        sp_mods.append(sp_mod)

        for m in modules:
            sp_mod, created = SpielerModule.objects.get_or_create(spieler=p, module=m)
            if created:
                sp_mods.append(sp_mod)


    # as long as sp_mods' states need to update their state potentially...
    while sp_mods:
        sp_mod = sp_mods.pop(0)
        prerequisites = [SpielerModule.objects.get(spieler=sp_mod.spieler, module=m) for m in sp_mod.module.prerequisite_modules.all()]

        # test if all at least unlocked
        all_passed = True
        for p in prerequisites:
            if p.state != module_state[6][0]:
                all_passed = False
                break

        test_children = True
        # unlock module
        if all_passed and sp_mod.state == module_state[0][0]:
            sp_mod.state = module_state[1][0]
            sp_mod.save()

        # lock module if it was in the state of unlocked (no other, because that has been explicitly set by Floofy or by player actions)
        elif not all_passed and sp_mod.state == module_state[1][0]:
            sp_mod.state = module_state[0][0]
            sp_mod.save()
        else: test_children = False

        # if state has changed, add children to sp_mods
        if test_children:
            for child in SpielerModule.objects.filter(spieler=sp_mod.spieler):
                if child not in sp_mods and sp_mod.module in child.module.prerequisite_modules.all():
                    sp_mods.append(child)
