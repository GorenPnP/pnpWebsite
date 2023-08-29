# Generated by Django 2.2.13 on 2020-12-19 12:05

from django.db import migrations, models

# enum with gate & temporal fissure types
from enum import Enum, IntEnum, unique

from django.apps import apps


@unique
class NodeType(IntEnum):

	# model name = made-up id to serialize node classes in db
	# (see: before / next / startNode fields)

	# zeitrisse (0-29)
	Linearriss = 0
	Liniendeletion = 1
	Splinter = 2
	Duplikator = 3
	Looper = 4
	Timelagger = 5
	Timedelayer = 6
	Runner = 7
	Metasplinter = 8

	# zeitannomalien (30-69)
	Consumer = 30
	Eraser = 31
	Blurr = 32
	Short = 33
	Traceback = 34

	# raumrisse (70-99)
	Raumfissur = 70
	Wurmloch = 71
	Raumloch = 72
	Kapselphänomen = 73
	Bizarrgebiet = 74

	# gatter, normal (100-129)
	Mirror = 100
	Inverter = 101
	Aktivator = 102		# Aktivator/Desaktivator
	Switch = 103
	Konverter = 104
	Barriere = 105

	# gatter, zeitanomalien (130-169)
	Manadegenerator = 130
	Manabombe = 131
	Supportgatter = 132
	Teleportgatter = 133

	# gatter, raumrisse (170-199)
	Sensorgatter = 170
	Tracinggatter = 171


	@classmethod
	def choices(cls):
		return [(key.value, key.name) for key in cls]

	def toModel(self):

		# model by name is the same as self.name
		for model in apps.get_app_config('time_space').get_models():
			if model.__name__ == self.name: return model

		return None

	@classmethod
	def fromModel(cls, model):
		choices = [c for c in NodeType.__dict__.keys()
			if c not in ["choices", "toModel", "fromModel"]]

		return NodeType[model.__name__] if model.__name__ in choices else None


@unique
class Signal(Enum):
	analyze = "//analyze"
	returns = "//return"
	crystallize = "//crystallize"
	normalize = "//normalize"
	drag = "//drag"
	drop = "//drop"
	naturalize = "//naturalize"
	delete = "//delete"
	forward = "//forward"
	inject = "//inject"
	skip = "//skip"
	mdv = "//mdv"
	bdv = "//bdv"
	mdbv = "//mdbv"
	restart = "//restart"


@unique
class LogLevel(IntEnum):
	DEBUG = 0
	LOG = 1
	WARN = 2
	ERROR = 3



class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Looper',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('before', models.TextField(default='[]')),
                ('next', models.TextField(default='[]')),
                ('nodeType', models.PositiveSmallIntegerField(choices=[(0, 'Linearriss'), (1, 'Liniendeletion'), (2, 'Splinter'), (3, 'Duplikator'), (4, 'Looper'), (5, 'Timelagger'), (6, 'Timedelayer'), (7, 'Runner'), (30, 'Consumer'), (31, 'Eraser'), (32, 'Blurr'), (33, 'Short'), (34, 'Traceback'), (70, 'Raumfissur'), (71, 'Wurmloch'), (72, 'Raumloch'), (73, 'Kapselphänomen'), (74, 'Bizarrgebiet'), (100, 'Mirror'), (101, 'Inverter'), (102, 'Aktivator'), (103, 'Switch'), (104, 'Konverter'), (105, 'Barriere'), (130, 'Manadegenerator'), (131, 'Manabombe'), (132, 'Supportgatter'), (133, 'Teleportgatter'), (170, 'Sensorgatter'), (171, 'Tracinggatter')], default=NodeType(4))),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Mirror',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('before', models.TextField(default='[]')),
                ('next', models.TextField(default='[]')),
                ('nodeType', models.PositiveSmallIntegerField(choices=[(0, 'Linearriss'), (1, 'Liniendeletion'), (2, 'Splinter'), (3, 'Duplikator'), (4, 'Looper'), (5, 'Timelagger'), (6, 'Timedelayer'), (7, 'Runner'), (30, 'Consumer'), (31, 'Eraser'), (32, 'Blurr'), (33, 'Short'), (34, 'Traceback'), (70, 'Raumfissur'), (71, 'Wurmloch'), (72, 'Raumloch'), (73, 'Kapselphänomen'), (74, 'Bizarrgebiet'), (100, 'Mirror'), (101, 'Inverter'), (102, 'Aktivator'), (103, 'Switch'), (104, 'Konverter'), (105, 'Barriere'), (130, 'Manadegenerator'), (131, 'Manabombe'), (132, 'Supportgatter'), (133, 'Teleportgatter'), (170, 'Sensorgatter'), (171, 'Tracinggatter')], default=NodeType(100))),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Net',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('startNodeId', models.IntegerField()),
            ],
        ),
    ]
