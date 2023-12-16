from django.db import migrations

rangs = [
  {
    "rang": 3,
    "hp": 1,
    "schadensWI": "1W4",
    "reaktionsbonus": 0,
    "angriffsbonus": 0
  },
  {
    "rang": 1,
    "hp": 1,
    "schadensWI": "1W2",
    "reaktionsbonus": 0,
    "angriffsbonus": 0
  },
  {
    "rang": 4,
    "hp": 2,
    "schadensWI": "1W4",
    "reaktionsbonus": 0,
    "angriffsbonus": 0
  },
  {
    "rang": 6,
    "hp": 3,
    "schadensWI": "1W4",
    "reaktionsbonus": 5,
    "angriffsbonus": 5
  },
  {
    "rang": 8,
    "hp": 4,
    "schadensWI": "1W4",
    "reaktionsbonus": 5,
    "angriffsbonus": 5
  },
  {
    "rang": 10,
    "hp": 5,
    "schadensWI": "1W6",
    "reaktionsbonus": 5,
    "angriffsbonus": 5
  },
  {
    "rang": 12,
    "hp": 6,
    "schadensWI": "1W6",
    "reaktionsbonus": 5,
    "angriffsbonus": 5
  },
  {
    "rang": 14,
    "hp": 7,
    "schadensWI": "1W6",
    "reaktionsbonus": 5,
    "angriffsbonus": 5
  },
  {
    "rang": 15,
    "hp": 7,
    "schadensWI": "1W8",
    "reaktionsbonus": 10,
    "angriffsbonus": 10
  },
  {
    "rang": 16,
    "hp": 8,
    "schadensWI": "1W8",
    "reaktionsbonus": 10,
    "angriffsbonus": 10
  },
  {
    "rang": 17,
    "hp": 8,
    "schadensWI": "2W4",
    "reaktionsbonus": 10,
    "angriffsbonus": 10
  },
  {
    "rang": 18,
    "hp": 9,
    "schadensWI": "2W4",
    "reaktionsbonus": 10,
    "angriffsbonus": 10
  },
  {
    "rang": 20,
    "hp": 10,
    "schadensWI": "1W10",
    "reaktionsbonus": 10,
    "angriffsbonus": 10
  },
  {
    "rang": 22,
    "hp": 11,
    "schadensWI": "1W10",
    "reaktionsbonus": 10,
    "angriffsbonus": 10
  },
  {
    "rang": 24,
    "hp": 12,
    "schadensWI": "1W10",
    "reaktionsbonus": 10,
    "angriffsbonus": 10
  },
  {
    "rang": 25,
    "hp": 12,
    "schadensWI": "1W6+1W4",
    "reaktionsbonus": 10,
    "angriffsbonus": 10
  },
  {
    "rang": 26,
    "hp": 13,
    "schadensWI": "1W6+1W4",
    "reaktionsbonus": 10,
    "angriffsbonus": 10
  },
  {
    "rang": 28,
    "hp": 14,
    "schadensWI": "2W6",
    "reaktionsbonus": 10,
    "angriffsbonus": 10
  },
  {
    "rang": 30,
    "hp": 15,
    "schadensWI": "2W6",
    "reaktionsbonus": 15,
    "angriffsbonus": 15
  },
  {
    "rang": 31,
    "hp": 15,
    "schadensWI": "2W6+1W2",
    "reaktionsbonus": 15,
    "angriffsbonus": 15
  },
  {
    "rang": 33,
    "hp": 15,
    "schadensWI": "2W6+1W4",
    "reaktionsbonus": 15,
    "angriffsbonus": 15
  },
  {
    "rang": 35,
    "hp": 20,
    "schadensWI": "3W6",
    "reaktionsbonus": 15,
    "angriffsbonus": 15
  },
  {
    "rang": 38,
    "hp": 20,
    "schadensWI": "2W8+1W6",
    "reaktionsbonus": 15,
    "angriffsbonus": 15
  },
  {
    "rang": 41,
    "hp": 25,
    "schadensWI": "3W8",
    "reaktionsbonus": 15,
    "angriffsbonus": 15
  },
  {
    "rang": 45,
    "hp": 25,
    "schadensWI": "2W10+1W6",
    "reaktionsbonus": 15,
    "angriffsbonus": 15
  },
  {
    "rang": 48,
    "hp": 25,
    "schadensWI": "2W10+1W8",
    "reaktionsbonus": 15,
    "angriffsbonus": 15
  },
  {
    "rang": 50,
    "hp": 30,
    "schadensWI": "3W10",
    "reaktionsbonus": 20,
    "angriffsbonus": 20
  },
  {
    "rang": 55,
    "hp": 30,
    "schadensWI": "3W12",
    "reaktionsbonus": 20,
    "angriffsbonus": 20
  },
  {
    "rang": 60,
    "hp": 35,
    "schadensWI": "2W12+2W6",
    "reaktionsbonus": 20,
    "angriffsbonus": 20
  },
  {
    "rang": 70,
    "hp": 40,
    "schadensWI": "2W12+3W6",
    "reaktionsbonus": 20,
    "angriffsbonus": 20
  },
  {
    "rang": 75,
    "hp": 40,
    "schadensWI": "2W12+3W6",
    "reaktionsbonus": 25,
    "angriffsbonus": 25
  },
  {
    "rang": 80,
    "hp": 45,
    "schadensWI": "3W12+2W6",
    "reaktionsbonus": 25,
    "angriffsbonus": 25
  },
  {
    "rang": 85,
    "hp": 45,
    "schadensWI": "2W12+3W10",
    "reaktionsbonus": 25,
    "angriffsbonus": 25
  },
  {
    "rang": 90,
    "hp": 45,
    "schadensWI": "3W12+3W8",
    "reaktionsbonus": 25,
    "angriffsbonus": 25
  },
  {
    "rang": 100,
    "hp": 50,
    "schadensWI": "3W20+1W6",
    "reaktionsbonus": 30,
    "angriffsbonus": 30
  },
  {
    "rang": 110,
    "hp": 50,
    "schadensWI": "3W20+1W8",
    "reaktionsbonus": 30,
    "angriffsbonus": 30
  },
  {
    "rang": 120,
    "hp": 60,
    "schadensWI": "3W20+1W10",
    "reaktionsbonus": 35,
    "angriffsbonus": 35
  },
  {
    "rang": 130,
    "hp": 60,
    "schadensWI": "3W20+1W12",
    "reaktionsbonus": 35,
    "angriffsbonus": 35
  },
  {
    "rang": 140,
    "hp": 60,
    "schadensWI": "3W20+2W8",
    "reaktionsbonus": 35,
    "angriffsbonus": 35
  },
  {
    "rang": 150,
    "hp": 70,
    "schadensWI": "4W20",
    "reaktionsbonus": 40,
    "angriffsbonus": 40
  },
  {
    "rang": 160,
    "hp": 70,
    "schadensWI": "4W20+1W6",
    "reaktionsbonus": 40,
    "angriffsbonus": 40
  },
  {
    "rang": 170,
    "hp": 70,
    "schadensWI": "4W20+2W6",
    "reaktionsbonus": 40,
    "angriffsbonus": 40
  },
  {
    "rang": 180,
    "hp": 80,
    "schadensWI": "4W20+2W8",
    "reaktionsbonus": 40,
    "angriffsbonus": 40
  },
  {
    "rang": 190,
    "hp": 80,
    "schadensWI": "4W20+3W6",
    "reaktionsbonus": 40,
    "angriffsbonus": 40
  },
  {
    "rang": 200,
    "hp": 80,
    "schadensWI": "5W20+1W6",
    "reaktionsbonus": 45,
    "angriffsbonus": 45
  },
  {
    "rang": 225,
    "hp": 80,
    "schadensWI": "5W20+1W10",
    "reaktionsbonus": 45,
    "angriffsbonus": 45
  },
  {
    "rang": 250,
    "hp": 90,
    "schadensWI": "5W20+3W6",
    "reaktionsbonus": 50,
    "angriffsbonus": 50
  },
  {
    "rang": 300,
    "hp": 90,
    "schadensWI": "6W20+1W6",
    "reaktionsbonus": 55,
    "angriffsbonus": 55
  },
  {
    "rang": 350,
    "hp": 90,
    "schadensWI": "6W20+2W6",
    "reaktionsbonus": 60,
    "angriffsbonus": 60
  },
  {
    "rang": 400,
    "hp": 100,
    "schadensWI": "7W20",
    "reaktionsbonus": 65,
    "angriffsbonus": 65
  },
  {
    "rang": 450,
    "hp": 110,
    "schadensWI": "7W20+1W6",
    "reaktionsbonus": 70,
    "angriffsbonus": 70
  },
  {
    "rang": 500,
    "hp": 120,
    "schadensWI": "1W100+3W20",
    "reaktionsbonus": 75,
    "angriffsbonus": 75
  },
  {
    "rang": 600,
    "hp": 130,
    "schadensWI": "1W100+8W8",
    "reaktionsbonus": 80,
    "angriffsbonus": 80
  },
  {
    "rang": 700,
    "hp": 140,
    "schadensWI": "1W100+4W20",
    "reaktionsbonus": 85,
    "angriffsbonus": 85
  },
  {
    "rang": 800,
    "hp": 160,
    "schadensWI": "1W100+7W12",
    "reaktionsbonus": 90,
    "angriffsbonus": 90
  },
  {
    "rang": 900,
    "hp": 180,
    "schadensWI": "2W100",
    "reaktionsbonus": 95,
    "angriffsbonus": 95
  },
  {
    "rang": 1000,
    "hp": 200,
    "schadensWI": "2W100+2W6",
    "reaktionsbonus": 100,
    "angriffsbonus": 100
  }
]


def populate_monster_rang(apps, schema_editor):
    Dice = apps.get_model('dex', 'Dice')
    Rang = apps.get_model('dex', 'MonsterRang')

    for rang in rangs:
        schadensWI = rang["schadensWI"]
        del rang["schadensWI"]
        rang_obj, _ = Rang.objects.get_or_create(rang=rang["rang"], defaults=rang)

        dices = []
        for dice_str in schadensWI.split("+"):
            [amount, kind] = dice_str.split("W")
            dice, _ = Dice.objects.get_or_create(amount=int(amount), type="W"+kind)
            dices.append(dice)
        rang_obj.schadensWI.add(*dices)



class Migration(migrations.Migration):

    dependencies = [
        ('dex', '0012_monsterrang'),
    ]

    operations = [
        migrations.RunPython(populate_monster_rang)
    ]
