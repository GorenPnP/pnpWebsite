from .interfaces import TemporalFissure
from time_space.enums import Signal


class Looper(TemporalFissure):

	def processSignal(self, signals) -> Signal:
		# TODO
		print("Processing Looper:", self.__str__(), signals)
		return signals[0] if len(signals) else None
