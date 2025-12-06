from django.contrib.auth import get_user_model
from django.db.models.signals import post_delete, pre_delete, pre_save, post_save
from django.dispatch import receiver

from character.models import Spieler
from webPush.models import *
from .models import Image, File, ModuleQuestion, RelQuiz, SpielerQuestion, SpielerSession, Module, module_state, Question, SpielerModule

User = get_user_model()

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


@receiver(post_save, sender=Spieler)
def create_relQuiz(sender, instance, **kwargs):
    if kwargs['created']:
        RelQuiz.objects.get_or_create(spieler=instance)

        # use post_save signal of Module to add all SpielerModules for new spieler
        module = Module.objects.all().first()
        if module: module.save()


# following: update module.max_points on:
#   save of every module
#   save or delete of any question
#   didn't work on Modulequestion since it resolves a m2m (between them)

@receiver(post_save, sender=Question)
@receiver(post_delete, sender=Question)
def update_max_points_of_module(sender, instance, **kwargs):
    # shouldn't ever happen
    if not instance: return

    # get related module
    modules = [mq.module for mq in ModuleQuestion.objects.filter(question=instance) if mq.module]

    # sum new max_points for each related module (trigger pre_save of Module)
    for m in modules: m.save()


@receiver(pre_save, sender=Module)
def update_max_points(sender, instance, **kwargs):
    # shouldn't ever happen
    if not instance: return

    sum = 0

    for mq in ModuleQuestion.objects.filter(module=instance):
        sum += mq.question.points

    instance.max_points = sum



# changed spielerModule -> add new Spielersession if state [seen, passed] ->
@receiver(pre_save, sender=SpielerModule)
def add_session(sender, instance, **kwargs):

    old_instance = SpielerModule.objects.filter(id=instance.id)
    if not old_instance.exists(): return

    if old_instance.first().state in [5, 6] and instance.state <= 2: # old: [seen, passed], new: [locked, unlocked, opened]
        SpielerSession.objects.create(spielerModule=instance)


# new session -> add SpielerQuestions TODO ordering with num
@receiver(post_save, sender=SpielerSession)
def add_spieler_questions(sender, instance, **kwargs):
    if not kwargs["created"]: return

    for mq in ModuleQuestion.objects.filter(module=instance.spielerModule.module).order_by("num"):

        sp_q = instance.questions.create(spieler=instance.spielerModule.spieler, question=mq.question)
        sp_q.moduleQuestions.add(mq)
        sp_q.save()

# create all missing sp_mods between all modules and all players
def add_missing_spielermodules():

    # create all missing sp_mods between all modules and all players
    for p in Spieler.objects.all():
        for m in Module.objects.all():
            SpielerModule.objects.get_or_create(spieler=p, module=m)


# works recursively, should a sp_mod's state be changed due to changes in prerequisites
@receiver(post_save, sender=Module)
@receiver(post_save, sender=SpielerModule)
def update_states_of_spielermodules(sender, instance, **kwargs):

    # make sure all SpielerModules exist
    if sender == Module:
        add_missing_spielermodules()

    # collect changed SpielerModule OR all SpielerModules of changed Module instance
    sp_mods = [instance] if sender == SpielerModule else list(SpielerModule.objects.filter(module=instance))

    # collect all theot dependants/children, too
    sp_mods_children = []
    for sp_mod in sp_mods:
        for child in SpielerModule.objects.filter(module__in=sp_mod.module.prerequisite_modules.all(), spieler=sp_mod.spieler).exclude(id=sp_mod.id):
            sp_mods_children.append(child)

    # get all of them together, eliminate duplicates
    sp_mods = list(set(sp_mods + sp_mods_children))

    # as long as sp_mods' states need to update their state potentially...
    while len(sp_mods):

        sp_mod = sp_mods.pop(0)
        prerequisites = [SpielerModule.objects.get(spieler=sp_mod.spieler, module=m) for m in sp_mod.module.prerequisite_modules.all()]

        # test if all at least unlocked
        all_passed = True
        for p in prerequisites:
            if not p.moduleFinished():
                all_passed = False
                break


        test_children = False    # true if state changed on the module. Then have to check its dependants/children for potential changes

        # unlock module
        if all_passed and sp_mod.state == module_state[0][0]:   # if SpielerModule is locked, but all prerequisites are met
            sp_mod.state = module_state[1][0]                   # set it to unlocked
            sp_mod.save(update_fields=["state"])
            test_children = True

            sp_mod.save()

        # prerequisites not met: unlocked or seen (not all to not disturb answering/correction/reviewing routine!)
        # -> locked (or plain passed if it has been optional)
        elif not all_passed and sp_mod.state in [1, 5]:
            test_children = True

            if sp_mod.optional:
                sp_mod.optional = False
                sp_mod.state = module_state[6][0]
            else:
                sp_mod.state = module_state[0][0]

            sp_mod.save(update_fields=["optional", "state"])

        # prerequisites not met: optional passed -> optional locked. Don't need to test children since it stays optional ^= it is still finished
        elif not all_passed and sp_mod.state == module_state[6][0] and sp_mod.optional:
            sp_mod.state = module_state[0][0]

            sp_mod.save(update_fields=["state"])


        if not test_children: continue

        # if state has changed, add children to sp_mods for checking
        for child in SpielerModule.objects.filter(spieler=sp_mod.spieler):

            # get all children-sp_mods and add them to list sp_mods (if they weren't in there before)
            if child not in sp_mods and sp_mod.module in child.module.prerequisite_modules.all():
                sp_mods.append(child)





#       deleting model instances        #


# delete all Media on delete of Question
@receiver(pre_delete, sender=Question)
def delete_its_media(sender, instance, **kwargs):
    media = [
        instance.images,
        instance.files,
    ]
    for type in media:
        if type is None: continue

        for m in type:
            if m is not None:
                m.delete()


# delete all SpielerModules on delete of Module
@receiver(pre_delete, sender=Module)
def delete_its_spieler_modules(sender, instance, **kwargs):
    if instance.icon:
        instance.icon.delete()

    for sp_mo in SpielerModule.objects.filter(module=instance):
        sp_mo.delete()


# delete all SpielerSessions on delete of SpielerModule
@receiver(pre_delete, sender=SpielerModule)
def delete_its_sessions(sender, instance, **kwargs):
    for session in SpielerSession.objects.filter(spielerModule=instance):
        session.delete()


# delete SpielerQuestions of SpielerSession on its delete
@receiver(pre_delete, sender=SpielerSession)
def delete_its_spieler_questions(sender, instance, **kwargs):
    for sp_q in instance.questions.all():
        sp_q.delete()


# delete all media of SpielerQuestion on its delete
@receiver(pre_delete, sender=SpielerQuestion)
def delete_its_media(sender, instance, **kwargs):
    media = [
        instance.answer_img,
        instance.answer_file,
        instance.correct_img,
        instance.correct_file
    ]
    for m in media:
        if m is not None: m.delete()


@receiver(pre_delete, sender=Image)
def delete_its_filesystem_img(sender, instance, **kwargs):
    if instance.img is not None: instance.img.delete()


@receiver(pre_delete, sender=File)
def delete_its_filesystem_file(sender, instance, **kwargs):
    if instance.file is not None: instance.file.delete()




#       Pushies        #


@receiver(pre_save, sender=SpielerModule)
def send_pushies_on_update_of_spielermodule_state(sender, instance, **kwargs):
    old_instance = SpielerModule.objects.filter(pk=instance.pk)
    
    new_state = instance.state
    old_state = old_instance.first().state if old_instance.exists() else 0
    if old_state == new_state: return

    message = instance.module.title

    # message to spieler [opened, corrected]
    if new_state in [2, 4]:
        users = User.objects.filter(username=instance.spieler.name)
        title = "Quiz: neues Modul freigegeben!" if new_state == 2 else "Quiz: Modul korrigiert"

        return PushSettings.send_message(users, title, message, PushTag.quiz)
    
    # message to spielleitung [answered, seen]
    if new_state in [3, 5]:
        title = "Quiz: Modul beantwortet" if new_state == 3 else "Quiz: Modul angesehen"
        message = f"{instance.spieler} hat {message} " + ("beantwortet" if new_state == 3 else "angesehen")

        return PushSettings.send_message(User.objects.all(), title, message, PushTag.quiz_control)
