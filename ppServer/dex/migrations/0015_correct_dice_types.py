from django.db import migrations


def correct_dice_types(apps, schema_editor):
    Dice = apps.get_model('dex', 'Dice')

    faulty_dice = Dice.objects.prefetch_related("attacke_set", "monster_set").filter(type__contains="w")
    for fd in faulty_dice:
      correct_dice, _ = Dice.objects.get_or_create(type=fd.type.upper(), amount=fd.amount)
      correct_dice.monster_set.add(*fd.monster_set.all())
      correct_dice.attacke_set.add(*fd.attacke_set.all())
    faulty_dice.delete()



class Migration(migrations.Migration):

    dependencies = [
        ('dex', '0014_alter_dice_type'),
    ]

    operations = [
        migrations.RunPython(correct_dice_types)
    ]
