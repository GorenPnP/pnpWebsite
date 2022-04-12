from typing import Tuple
from .interfaces import Gate
from time_space.enums import Signal


class Mirror(Gate):

	def processSignal(self, signals) -> Tuple[Signal, str]:
		# TODO
		print("Processing Mirror:" , self.__str__(), signals)
		return signals[0] if len(signals) else None, ""


class Inverter(Gate):

	def processSignal(self, signals) -> Tuple[Signal, str]:
		# TODO
		print("Processing Inverter:" , self.__str__(), signals)
		return signals[0] if len(signals) else None, ""


class Aktivator(Gate):

	def processSignal(self, signals) -> Tuple[Signal, str]:
		# TODO
		print("Processing Activator:" , self.__str__(), signals)
		return signals[0] if len(signals) else None, ""


class Switch(Gate):

	def processSignal(self, signals) -> Tuple[Signal, str]:
		# TODO
		print("Processing Switch:" , self.__str__(), signals)
		return signals[0] if len(signals) else None, ""


class Konverter(Gate):

	def processSignal(self, signals) -> Tuple[Signal, str]:
		# TODO
		print("Processing Converter:" , self.__str__(), signals)
		return signals[0] if len(signals) else None, ""

class Barriere(Gate):

	def processSignal(self, signals) -> Tuple[Signal, str]:
		# TODO
		print("Processing Barrier:" , self.__str__(), signals)
		return signals[0] if len(signals) else None, ""



class Manadegenerator(Gate):

	def processSignal(self, signals) -> Tuple[Signal, str]:
		# TODO
		print("Processing ManaDegenerator:" , self.__str__(), signals)
		return signals[0] if len(signals) else None, ""

class Manabombe(Gate):

	def processSignal(self, signals) -> Tuple[Signal, str]:
		# TODO
		print("Processing Manabomb:" , self.__str__(), signals)
		return signals[0] if len(signals) else None, ""


class Supportgatter(Gate):

	def processSignal(self, signals) -> Tuple[Signal, str]:
		# TODO
		print("Processing Supportgatter:" , self.__str__(), signals)
		return signals[0] if len(signals) else None, ""


class Teleportgatter(Gate):

	def processSignal(self, signals) -> Tuple[Signal, str]:
		# TODO
		print("Processing Teleportgatter:" , self.__str__(), signals)
		return signals[0] if len(signals) else None, ""

class Sensorgatter(Gate):

	def processSignal(self, signals) -> Tuple[Signal, str]:
		# TODO
		print("Processing Sensorgatter:" , self.__str__(), signals)
		return signals[0] if len(signals) else None, ""


class Tracinggatter(Gate):

	def processSignal(self, signals) -> Tuple[Signal, str]:
		# TODO
		print("Processing Tracinggatter:" , self.__str__(), signals)
		return signals[0] if len(signals) else None, ""
