from __future__ import annotations # Replaces all type annotations with strings. Fixes forward reference
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import itertools
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

		# Post init sequences
		for sequence in sequences.values():
			sequence.post_init(sequences)

		if not "animation" in json:
			raise McMetagenException("Texture animation is missing 'animation' parameter")

		root = Sequence.from_json("", json["animation"], states.keys(), sequence_names)
		root.post_init(sequences)

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
	fixed_duration: int = field(default=None,init=False) # Duration of the sequence unaffected by weight. Can be thought of as a 'minimum' duration

	@classmethod
	def from_json(cls, name: str, json: List[dict], state_names: List[str], sequence_names: List[str]) -> Sequence:
		total_weight = 0
		entries = []
		for entry_json in json:
			entry = SequenceEntry.from_json(entry_json)
			entry.validate_reference(name, state_names, sequence_names)
			total_weight += entry.weight
			entries.append(entry)

		return Sequence(name, entries, total_weight)		

	def post_init(self, sequences: Dict[str,Sequence]):
		""" Executes logic dependent on data that only exists after initialisation of the sequence """
		self.fixed_duration = self.calc_fixed_duration(sequences)

	def calc_fixed_duration(self, sequences: Dict[str,Sequence]) -> int:
		if not self.fixed_duration:
			self.fixed_duration = sum(map(lambda entry: entry.calc_fixed_duration(sequences), self.entries))
		return self.fixed_duration

	@property
	def is_weighted(self) -> bool:
		return self.total_weight > 0

	def to_animation(self, start: int, duration: Optional(int), states: Dict[str,State], sequences: Dict[str,Sequence]) -> AnimatedGroup:

		if self.is_weighted:
			if not duration:
				raise McMetagenException(f"Didn't pass duration to weighted sequence '{self.name}'")
			if duration <= self.fixed_duration:
				raise McMetagenException(f"Duration '{duration}' passed to sequence '{self.name}' is smaller than its fixed duration")
			entry_durations = distribute_duration(duration-self.fixed_duration, self.total_weight, self.entries)
		else:
			entry_durations = map(lambda entry: entry.duration, self.entries)

		animatedEntries = []
		currentTime = start
		for entry, entry_duration in zip(self.entries, entry_durations):
			if entry.has_weight:
				part_durations = distribute_duration(entry_duration, entry.weight*entry.repeat, [entry for i in range(entry.repeat)])
			else:
				part_durations = itertools.repeat(entry_duration, entry.repeat)

			for part_duration in part_durations:
				if part_duration <= 0:
					raise McMetagenException(f"Duration of '{duration}' exhausted while trying to distribute it over entries in weighted sequence '{self.name}'")

				animatedEntry = entry.to_animated_entry(currentTime, part_duration, states, sequences)
				animatedEntries.append(animatedEntry)
				currentTime += animatedEntry.duration

		return AnimatedGroup(start, currentTime, self.name, animatedEntries)

def distribute_duration(duration:int, total_weight:int, entries: List[SequenceEntry]):
	""" Distributes a duration over a collection of weighted SequenceEntries """

	remaining_duration = duration
	remaining_weight = total_weight
	for entry in entries:
		if entry.has_weight:
			weighted_duration = round_half_up((entry.weight*remaining_duration)/remaining_weight)
			remaining_duration -= weighted_duration
			remaining_weight -= entry.weight
			yield weighted_duration
		else:
			yield entry.duration

def round_half_up(num, decimals:int = 0) -> int:
    multiplier = 10 ** decimals
    return math.floor(num*multiplier + 0.5) / multiplier

@dataclass
class SequenceEntry:
	# Reference
	type: SequenceEntryType
	ref: str

	repeat: int = 1
	duration: Optional(int) = None
	weight: int = 0
	start: Optional(str) = None
	end: Optional(str) = None

	@property
	def has_weight(self) -> bool:
		""" Has the entry any weight to it and should be considered when distributing weighted duration """
		return self.weight > 0

	@classmethod
	def from_json(cls, json: Dict) -> SequenceEntry:
		if str(SequenceEntryType.SEQUENCE) in json:
			type = SequenceEntryType.SEQUENCE
			ref = json[str(SequenceEntryType.SEQUENCE)]
		elif str(SequenceEntryType.STATE) in json:
			type = SequenceEntryType.STATE
			ref = json[str(SequenceEntryType.STATE)]
		else:
			raise McMetagenException("Sequence entry is missing reference to state or sequence")

		repeat = json.get("repeat", 1)
		duration = json.get("duration", 1)
		weight = json.get("weight", 0)
		start = json.get("start")
		end = json.get("end")

		return SequenceEntry(type, ref, repeat, duration, weight, start, end)

	def to_animated_entry(self, start:int, duration:int, states: Dict[str,State], sequences: Dict[str,Sequence]) -> AnimatedEntry:
		if self.type == SequenceEntryType.STATE:
			return AnimatedState(start, start+duration, states[self.ref].index)
		else:
			return sequences[self.ref].to_animation(start, duration, states, sequences)

	def validate_reference(self, parent_sequence: str, state_names: List[str], sequence_names: List[str]):
		""" Checks if the reference of this entry is valid """

		if self.type == SequenceEntryType.STATE and not self.ref in state_names:
			raise InvalidReferenceException(parent_sequence, self.ref, self.type)
		if self.type == SequenceEntryType.SEQUENCE and not self.ref in sequence_names:
			raise InvalidReferenceException(parent_sequence, self.ref, self.type)

	def calc_fixed_duration(self, sequences: Dict[str,Sequence]) -> int:
		fixed_duration = 0
		if self.type == SequenceEntryType.STATE:
			if not self.has_weight:
				fixed_duration = self.duration*self.repeat
		elif self.type == SequenceEntryType.SEQUENCE:
			# Don't calculate fixed duration of nested weighted sequences here, because durations would be calculated more than once
			if not sequences[self.ref].is_weighted:
				fixed_duration = sequences[self.ref].calc_fixed_duration(sequences)*self.repeat

		return fixed_duration

class SequenceEntryType(Enum):
	STATE = 1
	SEQUENCE = 2

	def __str__(self) -> str:
		return self.name.lower()

class InvalidReferenceException(McMetagenException):
	def __init__(self, parent_sequence: str, ref_target: str, ref_type: SequenceEntryType):
		if ref_type == SequenceEntryType.STATE:
			super(InvalidReferenceException, self).__init__(f"Reference '{ref_target}' in sequence '{parent_sequence}' does not name a state")
		elif ref_type == SequenceEntryType.SEQUENCE:
			super(InvalidReferenceException, self).__init__(f"Reference '{ref_target}' in sequence '{parent_sequence}' does not name a sequence")