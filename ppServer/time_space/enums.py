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
	analyze = 0


@unique
class LogLevel(IntEnum):
	DEBUG = 0
	LOG = 1
	WARN = 2
	ERROR = 3
