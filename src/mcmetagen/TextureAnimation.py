from __future__ import annotations # Replaces all type annotations with strings. Fixes forward reference
from dataclasses import dataclass
from typing import List, Dict, Optional
from enum import Enum
from mcmetagen.Exceptions import *

@dataclass
class TextureAnimation:

	states: Dict[str,State]
	sequences: Dict[str,Sequence]

	@classmethod
	def from_json(cls, json: dict) -> TextureAnimation:
		# Parse states
		if not "states" in json:
			raise ParsingException("Texture animation is missing 'states' parameter")
		states = {name:State(name, idx) for idx,name in enumerate(json["states"])}

		# Parse Sequences
		sequences = {name:Sequence.from_json(name, entries) for name,entries in json.get("sequences", {}).items()}

		# Validate Sequences
		for sequence in sequences.values():
			sequence.validate_references(states, sequences)

		if not "animation" in json:
			raise ParsingException("Texture animation is missing 'states' parameter")

		root = Sequence.from_json("", json["animation"])
		root.validate_references(states, sequences)

		animation = root.to_animation(0, states, sequences)
		print(animation)

		return TextureAnimation(states, sequences)

@dataclass
class AnimatedEntry:
	start: int
	end: int

	def __post_init__(self):
		if self.duration <= 0:
			raise ValueError("Duration of AnimatedEntry must at least be 1")

	@property
	def duration(self):
		return self.end-self.start

@dataclass
class AnimatedGroup(AnimatedEntry):
	name: str
	entries: List(AnimatedEntry)

@dataclass
class AnimatedState(AnimatedEntry):
	index: int

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

	is_weighted: bool = False
	total_weight: int = 0

	@classmethod
	def from_json(cls, name: str, json: List[dict]) -> Sequence:
		total_weight = 0
		is_weighted = False
		entries = []
		for entry_json in json:
			entry = SequenceEntry.from_json(entry_json)
			if entry.weight:
				is_weighted = True
				total_weight += entry.weight
			entries.append(entry)

		return Sequence(name, entries, is_weighted, total_weight)

	def validate_references(self, states: Dict[str,State], sequences: Dict[str,Sequence]):
		""" Checks if all references inside this sequence are valid """

		try:
			for entry in self.entries:
				entry.validate_references(states, sequences)
		except ParsingException as e:
			if self.name == "":
				print(f"Exception while validating root sequence")
			else:
				print(f"Exception while validating sequence '{self.name}'")
			raise e

	def to_animation(self, start: int, states: Dict[str,State], sequences: Dict[str,Sequence]) -> AnimatedGroup:
		animatedEntries = []

		currentTime = start
		for entry in self.entries:
			if entry.type == SequenceEntryType.STATE:
				animatedState = AnimatedState(currentTime, currentTime+entry.duration, states[entry.ref].index)
				animatedEntries.append(animatedState)
				currentTime += animatedState.duration
			if entry.type == SequenceEntryType.SEQUENCE:
				referenced_sequence = sequences[entry.ref]
				animatedGroup = referenced_sequence.to_animation(currentTime, states, sequences)
				animatedEntries.append(animatedGroup)
				currentTime += animatedGroup.duration

		return AnimatedGroup(start, currentTime, self.name, animatedEntries)

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
		if not "type" in json:
			raise ParsingException("Reference is missing 'type' attribute")
		type = SequenceEntryType.from_string(json["type"])
		
		if not "ref" in json:
			raise ParsingException("Reference is missing 'ref' attribute")
		ref = json["ref"]

		repeat = json.get("repeat", 1)
		duration = json.get("duration")
		weight = json.get("weight")
		start = json.get("start")
		end = json.get("end")

		return SequenceEntry(type, ref, repeat, duration, weight, start, end)

	def validate_references(self, states: Dict[str,State], sequences: Dict[str,Sequence]):
		""" Checks if the reference of this entry is valid """

		if self.type == SequenceEntryType.STATE and not self.ref in states:
			raise ParsingException(f"'{self.ref}' does not reference a state")
		if self.type == SequenceEntryType.SEQUENCE and not self.ref in sequences:
			raise ParsingException(f"'{self.ref}' does not reference a sequence")

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