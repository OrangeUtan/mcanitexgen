from __future__ import annotations # Replaces all type annotations with strings. Fixes forward reference
import math
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
from mcmetagen.Exceptions import *

@dataclass
class TextureAnimation:

	states: Dict[str,State]
	sequences: Dict[str,Sequence]
	animation: AnimatedGroup

	@classmethod
	def from_json(cls, json: dict) -> TextureAnimation:
		# Parse states
		if not "states" in json:
			raise McMetagenException("Texture animation is missing 'states' parameter")
		states = {name:State(name, idx) for idx,name in enumerate(json["states"])}

		# Parse sequences
		sequence_names = json.get("sequences", {}).keys()
		sequences = dict()
		for name,entries in json.get("sequences", {}).items():
			sequence = Sequence.from_json(name, entries, states.keys(), sequence_names)
			sequences[name] = sequence

		if not "animation" in json:
			raise McMetagenException("Texture animation is missing 'animation' parameter")

		root = Sequence.from_json("", json["animation"], states.keys(), sequence_names)

		animation = root.to_animation(0, None, states, sequences)

		return TextureAnimation(states, sequences, animation)

@dataclass
class AnimatedEntry:
	start: int
	end: int

	def __init__(self, start:int, end:int):
		self.start = int(start)
		self.end = int(end)

		if self.duration <= 0:
			raise ValueError("Duration of AnimatedEntry must at least be 1")

	@property
	def duration(self):
		return self.end-self.start

@dataclass
class AnimatedGroup(AnimatedEntry):
	name: str
	entries: List(AnimatedEntry)

	def __init__(self, start:int, end:int, name:str, entries:List[AnimatedEntry]):
		super(AnimatedGroup, self).__init__(start,end)
		self.name = name
		self.entries = entries

@dataclass
class AnimatedState(AnimatedEntry):
	index: int

	def __init__(self, start:int, end:int, index:int):
		super(AnimatedState, self).__init__(start,end)
		self.index = index

@dataclass
class State:
	"""
	Class that represents one frame of the texture the animation is based on.
	
	Attributes:
	-----------
	name: str
	    A custom name that can be used to reference this staten\n
	index: int
	    The offset of this state inside the texture
	"""

	name: str
	index: int

@dataclass
class Sequence:
	"""
	A sequence of states and nested sequences that can be used to create an animation.

	Attributes:
	-----------
	name: str
	    A custom name that can be used to referenced this Sequence\n
	entries: List[SequenceEntry]
		List of states and sequences this sequence consists of
	"""

	name: str
	entries: List[SequenceEntry]

	total_weight: int

	@property
	def is_weighted(self):
		return self.total_weight > 0

	@classmethod
	def from_json(cls, name: str, json: List[dict], state_names: List[str], sequence_names: List[str]) -> Sequence:
		total_weight = 0
		entries = []
		for entry_json in json:
			entry = SequenceEntry.from_json(entry_json)
			entry.validate_reference(name, state_names, sequence_names)

			if entry.weight != None:
				total_weight += entry.weight
			entries.append(entry)

		return Sequence(name, entries, total_weight)

	def to_animation(self, start: int, duration: Optional(int), states: Dict[str,State], sequences: Dict[str,Sequence]) -> AnimatedGroup:
		animatedEntries = []

		if self.is_weighted:
			if not duration:
				raise McMetagenException(f"Didn't pass duration to weighted sequence '{self.name}'")
			fixed_duration = self.calc_fixed_duration(sequences)
			if duration <= fixed_duration:
				raise McMetagenException(f"Duration passed to weighted sequence {self.name} is smaller than its fixed duration")
			time_bank = WeightedTimeBank(start, duration-fixed_duration, self.total_weight)

		currentTime = start
		for entry in self.entries:
			if entry.type == SequenceEntryType.STATE:
				if entry.is_weighted(sequences):
					state_duration = time_bank.take(entry.weight)
				else:
					state_duration = entry.duration * entry.repeat

				animatedState = AnimatedState(currentTime, currentTime+state_duration, states[entry.ref].index)
				animatedEntries.append(animatedState)
				currentTime += animatedState.duration
			if entry.type == SequenceEntryType.SEQUENCE:
				referenced_sequence = sequences[entry.ref]

				for i in range(entry.repeat):
					if self.is_weighted and entry.is_weighted(sequences):
						seq_duration = time_bank.take(entry.weight)
						animatedGroup = referenced_sequence.to_animation(currentTime, seq_duration, states, sequences)
						animatedEntries.append(animatedGroup)
					else:
						animatedGroup = referenced_sequence.to_animation(currentTime, entry.duration, states, sequences)
						animatedEntries.append(animatedGroup)
					currentTime += animatedGroup.duration

		return AnimatedGroup(start, currentTime, self.name, animatedEntries)

	def calc_fixed_duration(self, sequences):
		return sum(map(lambda entry: entry.calc_fixed_duration(sequences), self.entries))

class WeightedTimeBank:
	remaining_time: int
	remaining_weight: int

	def __init__(self, start:int, duration: int, total_weight: int):
		self.remaining_time = duration
		self.remaining_weight = total_weight

	def take(self, weight: int) -> int:
		if self.remaining_time <= 1:
			raise Exception("Cant't take time from empty time bank")

		weighted_time = round_half_up((weight*self.remaining_time)/self.remaining_weight)
		self.remaining_time -= weighted_time
		self.remaining_weight -= weight

		return weighted_time

def round_half_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.floor(n*multiplier + 0.5) / multiplier

@dataclass
class SequenceEntry:
	# Reference
	type: SequenceEntryType
	ref: str

	repeat: int = 1
	duration: Optional(int) = None
	weight: Optional(int) = None
	start: Optional(str) = None
	end: Optional(str) = None

	@classmethod
	def from_json(cls, json: Dict):
		if "sequence" in json:
			type = SequenceEntryType.SEQUENCE
			ref = json["sequence"]
		elif "state" in json:
			type = SequenceEntryType.STATE
			ref = json["state"]
		else:
			raise McMetagenException("Sequence entry is missing reference to state or sequence")

		repeat = json.get("repeat", 1)
		duration = json.get("duration")
		weight = json.get("weight")
		start = json.get("start")
		end = json.get("end")

		if weight == None and duration == None:
			duration = 1

		return SequenceEntry(type, ref, repeat, duration, weight, start, end)

	def validate_reference(self, parent_sequence: str, state_names: List[str], sequence_names: List[str]):
		""" Checks if the reference of this entry is valid """

		if self.type == SequenceEntryType.STATE and not self.ref in state_names:
			raise InvalidReferenceException(parent_sequence, self.ref, self.type)
		if self.type == SequenceEntryType.SEQUENCE and not self.ref in sequence_names:
			raise InvalidReferenceException(parent_sequence, self.ref, self.type)

	def is_weighted(self, sequences: Dict[str,Sequence]) -> bool:
		if self.type == SequenceEntryType.STATE:
			return self.weight != None and self.weight > 0
		elif self.type == SequenceEntryType.SEQUENCE:
			if self.weight != None and self.weight > 0:
				return True
			else:
				return sequences[self.ref].is_weighted

	def calc_fixed_duration(self, sequences):
		fixed_duration = 0
		if self.type == SequenceEntryType.STATE:
			if not self.is_weighted(sequences):
				fixed_duration = self.duration*self.repeat
		elif self.type == SequenceEntryType.SEQUENCE:
			# Don't calculate fixed duration of nested weighted sequences here, because durations would be calculated more than once
			if not sequences[self.ref].is_weighted:
				fixed_duration = sequences[self.ref].calc_fixed_duration(sequences)*self.repeat

		return fixed_duration

class SequenceEntryType(Enum):
	STATE = 1
	SEQUENCE = 2

	@classmethod
	def from_string(cls, str: str) -> SequenceEntryType:
		if str == "state":
			return SequenceEntryType.STATE
		elif str == "sequence":
			return SequenceEntryType.SEQUENCE
		else:
			raise ValueError(f"'{str}' cannot be mapped to a reference type")

class InvalidReferenceException(McMetagenException):
	def __init__(self, parent_sequence: str, ref_target: str, ref_type: SequenceEntryType):
		if ref_type == SequenceEntryType.STATE:
			super(InvalidReferenceException, self).__init__(f"Reference '{ref_target}' in sequence '{parent_sequence}' does not name a state")
		elif ref_type == SequenceEntryType.SEQUENCE:
			super(InvalidReferenceException, self).__init__(f"Reference '{ref_target}' in sequence '{parent_sequence}' does not name a sequence")