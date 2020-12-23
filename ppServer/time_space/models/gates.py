from .interfaces import Gate
from time_space.enums import Signal


class Mirror(Gate):

	def processSignal(self, signals) -> Signal:
		# TODO
		print("Processing Mirror:" , self.__str__(), signals)
		return signals[0] if len(signals) else None
