from random import choice, randint
from typing import List, Tuple

from django.db import models


from .interfaces import TemporalFissure
from time_space.enums import Signal


class Linearriss(TemporalFissure):

	_output = {
		"always": ["Growth accelerated. Manainput stabilized. Increasing size for further division."],
		"killed": ["Growth has been corrupted. Stabilization failed."]
	}
	_required_input = [Signal.returns, Signal.crystallize, Signal.normalize]


class Liniendeletion(TemporalFissure):

	_output = {
		"always": [
			"Target not found.",
			"No event existing.",
			"There is nothing.",
			"We are wasting energy.",
			"No.",
			"Time is a state of mind.",
			"Reach out.",
			"Unidentified object found.",
			"Restarting...",
			"Program not ready.",
			"Initializing...",
			"Please restart.",
			"Converting splinter.",
			"What am I?"
		]
	}
	_required_input = [Signal.analyze, Signal.drag, Signal.drop, Signal.naturalize]


class Splinter(TemporalFissure):

	def _get_output(self, _):

		# Update this to include code point ranges to be sampled
		include_ranges = [
			( 0x0021, 0x0021 ),
			( 0x0023, 0x0026 ),
			( 0x0028, 0x007E ),
			( 0x00A1, 0x00AC ),
			( 0x00AE, 0x00FF ),
			( 0x0100, 0x017F ),
			( 0x0180, 0x024F ),
			( 0x2C60, 0x2C7F ),
			( 0x16A0, 0x16F0 ),
			( 0x0370, 0x0377 ),
			( 0x037A, 0x037E ),
			( 0x0384, 0x038A ),
			( 0x038C, 0x038C ),
		]

		alphabet = [
			chr(code_point) for current_range in include_ranges
				for code_point in range(current_range[0], current_range[1] + 1)
		]
		return ''.join(choice(alphabet) for _ in range(randint(3, 50)))


class Metasplinter(Splinter):
	pass


class Duplikator(TemporalFissure):

	_output = {
		"always": ["Mana has been detected", "More mana is needed", "Gathering more mana"],
		"hit": ["Input has been blocked", "Currently no power input", "A critical error occurred"],
		"killed": ["Maintaining manaflow failed", "Stabilization failed", "Dew point too high"]
	}
	_required_input = [Signal.crystallize, Signal.normalize, Signal.returns]

	def processSignal(self, signals) -> Tuple[Signal, str]:
		index = self.next_required_input_at
		output_1 = self._get_output(signals)

		self.next_required_input_at = index
		self.save()

		output_2 = self._get_output(signals)

		return None, "#{}: {} {}".format(self.net_id, output_1, output_2)


class Looper(TemporalFissure):

	outputs = models.JSONField(default=list, blank=True)

	_output = {
		"always": ["Mana in a spiral", "Circulating more energy", "Power ramped up"],
		"hit": ["Dizzyness", "Eastward it goes", "Getting down"],
		"killed": ["Mana falling down", "Leaving the circle", "Outer space"]
	}
	_required_input = [Signal.analyze, Signal.drag, Signal.delete, Signal.naturalize]

	def processSignal(self, signals) -> Tuple[Signal, str]:
		_, o = super().processSignal(signals)
		nr, new_output = o.split(":")
		self.outputs.append(new_output.strip())
		self.save()

		return None, "{}: {}".format(nr, ". ".join(self.outputs))


class Timelagger(TemporalFissure):

	_output = {
		"always": [None],
		"hit": ["it says", "I guess", "maybe", "it shouldn't be", "I assume"]
	}
	_required_input = [Signal.analyze, Signal.drag, Signal.drop, Signal.normalize]

	def processSignal(self, signals) -> Tuple[Signal, str]:
		super().processSignal(signals)
		return None, None

	def postprocessSignal(self, outputs: List[str]) -> List[str]:
		prev_output = outputs[-1].split(": ")[1]
		own_output = ". " + choice(self._output["hit"]) if self.next_required_input_at > 0 else ""
		return outputs + ["#{}: {}{}".format(self.net_id, prev_output, own_output)]


class Timedelayer(TemporalFissure):

	prev_output = models.TextField(default="", blank=True)

	_output = {
		"always": ["No", "Wrong", "Incorrect", "Yesn't", "Don't", "Is not"],
		"hit": ["Yes", "Right", "Hurt", "Wow", "Betrayal", "Unfair"],
		"killed": ["Murderer", "Killer", "No time for that", "Out of existence"]
	}
	_required_input = [Signal.forward, Signal.inject, Signal.normalize]

	def processSignal(self, signals) -> Tuple[Signal, str]:
		_, o = super().processSignal(signals)
		prev = self.prev_output

		nr, new_output = o.split(":")
		self.prev_output = new_output.strip()
		self.save()

		return None, "{}: {}".format(nr, prev) if prev else None


class Runner(TemporalFissure):

	_output = {
		"always": ["Yes", "More power", "POW", "Module established", "More mana is needed"],
		"hit": ["Mana has been blocked", "A critical error occurred", "Target not found", "Run"],
		"killed": ["Stormy", "Awaiting input", "Stopped running", "I stopped working"]
	}
	_required_input = [Signal.crystallize, Signal.returns, Signal.normalize]

	def processSignal(self, signals) -> Tuple[Signal, str]:
		super().processSignal(signals)
		return None, None

	def postprocessSignal(self, outputs: List[str]) -> List[str]:
		output = ""

		# killed
		if self.next_required_input_at >= len(self._required_input):
			# self.destroy()
			output = choice(self._output["killed"]) if "killed" in self._output else choice(self._output["always"]) # "killed"

		# hit
		if not output and self.next_required_input_at != 0:
			output = choice(self._output["hit"]) if "hit" in self._output else choice(self._output["always"]) #  "hit"

		# missed
		if not output:
			output = choice(self._output["always"]) #"missed"

		return ["#{}: {}".format(self.net_id, output)] + outputs
