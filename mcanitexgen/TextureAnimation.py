from __future__ import annotations # Replaces all type annotations with strings. Fixes forward reference
import math
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Iterable, Any
from enum import Enum
import itertools
from mcanitexgen.Exceptions import *
from mcanitexgen.Utils import *

@dataclass
class TextureAnimation:
	name: str
	root_sequence: Sequence
	states: Dict[str,State]

	sequences: Dict[str,Sequence] = field(default_factory=list)
	constants: Dict[str, Any] = field(default_factory=dict)
	texture: Optional(str) = None
	interpolate: bool = False

	animation: AnimatedGroup = field(init=False)
	marks: Dict[str,AnimationMark] = field(init=False, default_factory=dict)

	def __post_init__(self):
		self.animation = self.root_sequence.to_animation(0, 0, self)
		self.animation.validate()

	@classmethod
	def from_json(cls, name:str, json: dict, texture_animations: Dict[str,TextureAnimation] = dict()) -> TextureAnimation:
		# Parse constants
		constants = dict()
		if "constants" in json:
			for name, expr in json.get("constants", {}).items():
				constants[name] = evaluate_expr(str(expr), {**texture_animations, **constants})		

		texture = json.get("texture")
		interpolate = json.get("interpolate",False)
		
		# Parse states
		if not "states" in json:
			raise MCAnitexgenException("Texture animation is missing 'states' parameter")
		states = {name:State(name, idx) for idx,name in enumerate(json["states"])}

		# Parse sequences
		sequence_names = json.get("sequences", {}).keys()
		sequences = dict()
		for entry_name,entries in json.get("sequences", {}).items():
			sequence = Sequence.from_json(entry_name, entries, states.keys(), sequence_names, {**texture_animations, **constants})
			sequences[entry_name] = sequence

		# Post init sequences
		for sequence in sequences.values():
			sequence.post_init(sequences)

		if not "animation" in json:
			raise MCAnitexgenException("Texture animation is missing 'animation' parameter")

		# Parse root sequence
		root = Sequence.from_json("", json["animation"], states.keys(), sequence_names, {**texture_animations, **constants})
		root.post_init(sequences)

		return TextureAnimation(name, root_sequence=root, states=states, texture=texture, interpolate=interpolate, sequences=sequences, constants=constants)

	def mark(self, mark_name:str, index:int = 0):
		if not mark_name in self.marks:
			raise MCAnitexgenException(f"TextureAnimation '{self.name}' doesn't have mark '{mark_name}'")
		return self.marks[mark_name][index]
		
	def add_mark(self, name:str, mark: AnimationMark):
		if not name in self.marks:
			self.marks[name] = [mark]
		else:
			self.marks[name].append(mark)

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

	def to_frames(self) -> Geneartor[Dict, None, None]:
		for entry in self.entries:
			for frame in entry.to_frames():
				yield frame
	
	def extend_until(self, time:int):
		if self.end < time:
			self.end = time
			if self.entries:
				self.entries[-1].extend_until(time)

	def validate(self):
		if self.entries:
			if not self.start == self.entries[0].start:
				raise MCAnitexgenException(f"AnimatedGroup does not start with its first entry: {self}'")
			if not self.end == self.entries[-1].end:
				raise MCAnitexgenException(f"AnimatedGroup does not end with its last entry: {self}'")

			for entry in self.entries:
				entry.validate()

@dataclass
class AnimatedState(AnimatedEntry):
	index: int

	def __init__(self, start:int, end:int, index:int):
		super(AnimatedState, self).__init__(start,end)
		self.index = index

	def to_frames(self) -> Generator[Dict, None, None]:
		yield {"index": self.index, "time": self.duration}

	def extend_until(self, time:int):
		if self.end < time:
			self.end = time

	def validate(self):
		pass

@dataclass
class AnimationMark:
	start: int
	end: int

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
	def from_json(cls, name: str, json: List[dict], state_names: List[str], sequence_names: List[str], expr_locals: Dict[str, Any]) -> Sequence:
		total_weight = 0
		entries = []
		for entry_json in json:
			entry = SequenceEntry.from_json(entry_json, expr_locals)
			entry.validate_reference(name, state_names, sequence_names)
			total_weight += entry.weight
			entries.append(entry)

		return Sequence(name, entries, total_weight)		

	def post_init(self, sequences: Dict[str,Sequence]):
		""" Executes logic dependent on data that only exists after initialization of the sequence """
		self.fixed_duration = self.calc_fixed_duration(sequences)

	def calc_fixed_duration(self, sequences: Dict[str,Sequence]) -> int:
		"""
		Recursively calculates the sum of the durations of all entries.

		If a weighted sequence tries to distribute a duration, its possible that some of its entries are not weighted and already have a duration.
		Thus, some of the to be distributed duration is already taken by these entries.
		"""

		if not self.fixed_duration:
			self.fixed_duration = sum(map(lambda entry: entry.calc_fixed_duration(sequences), self.entries))
		return self.fixed_duration

	@property
	def is_weighted(self) -> bool:
		""" 
		Returns wether this sequence contains any weighted entries.

		Weighted sequences have to be passed a duration, which is then distribute to its entries, based on their weights.
		"""

		return self.total_weight > 0

	def to_animation(self, currentTime: int, duration: int, textureAnimation: TextureAnimation) -> AnimatedGroup:
		# Are there any weighted entries
		if self.is_weighted:
			if duration == 0:
				raise MCAnitexgenException(f"Didn't pass duration to weighted sequence '{self.name}'")
			if duration <= self.fixed_duration:
				raise MCAnitexgenException(f"Sequence '{self.name}': Duration must be at least '{self.fixed_duration}', but was '{duration}'")

			# Calculate times for weighted entries
			distributable_duration = duration-self.fixed_duration # Duration that can be distributed over the weighted entries
			weights_of_weighted_entries = map(lambda entry: entry.weight, filter(lambda entry: entry.has_weight, self.entries))
			weighted_durations = partition_by_weights(distributable_duration, self.total_weight, weights_of_weighted_entries)

		animatedEntries = []
		for i, entry in enumerate(self.entries):

			# Get duration of current entry
			entry_duration = next(weighted_durations) if entry.has_weight else entry.duration

			# Entry has 'start' property
			if entry.start:
				if currentTime == 0:
					raise MCAnitexgenException(f"Sequence '{self.name}': {i+1}. entry can't start at '{entry.start}', because there is no previous entry")
				if currentTime > entry.start:
					raise MCAnitexgenException(f"Sequence '{self.name}': {i+1}. entry can't start at '{entry.start}', because of previous entry")
				currentTime = entry.start

			# Entry has 'end' property
			if entry.end:
				if currentTime >= entry.end:
					raise MCAnitexgenException(f"Sequence '{self.name}': {i+1}. entry can't end at '{entry.end}', because of previous entry")
				entry_duration = entry.end - currentTime

			# Get the durations of each repetition of the current entry.
			if entry.has_weight:
				# Repetitions of weighted entries have to all fit within its (above) calculated duration. 
				# E.g.: An Entry with duration 20 and repeat 4, will generate 4 AnimatedEntries, each with a duration of 5.
				repetition_durations = partition_by_weights(entry_duration, entry.weight*entry.repeat, itertools.repeat(entry.weight, entry.repeat))
			else:
				# Unweighted entries just get repeatet with the same duration
				repetition_durations = itertools.repeat(entry_duration, entry.repeat)

			for repetition_duration in repetition_durations:
				if repetition_duration <= 0:
					raise MCAnitexgenException(f"Sequence '{self.name}': Duration of '{distributable_duration}' exhausted while trying to distribute it over entries")

				# Convert to AnimatedEntry
				animatedEntry = entry.to_animated_entry(currentTime, repetition_duration, textureAnimation)
				
				# Previous AnimatedEntry always has to end at the start of the new entry. Makes sure 'start' property can backpropagate
				if animatedEntries:
					animatedEntries[-1].extend_until(animatedEntry.start)

				# Add mark if any
				if entry.mark:
					textureAnimation.add_mark(entry.mark, AnimationMark(animatedEntry.start, animatedEntry.end))

				# Add entry
				animatedEntries.append(animatedEntry)
				currentTime = animatedEntry.end

		return AnimatedGroup(animatedEntries[0].start, currentTime, self.name, animatedEntries)

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
	mark: Optional(str) = None

	@property
	def has_weight(self) -> bool:
		""" Has the entry any weight to it and should be considered when distributing weighted duration """
		return self.weight > 0

	@classmethod
	def from_json(cls, json: Dict, expr_locals: Dict[str,Any]) -> SequenceEntry:
		if str(SequenceEntryType.SEQUENCE) in json:
			type = SequenceEntryType.SEQUENCE
			ref = json[str(SequenceEntryType.SEQUENCE)]
		elif str(SequenceEntryType.STATE) in json:
			type = SequenceEntryType.STATE
			ref = json[str(SequenceEntryType.STATE)]
		else:
			raise MCAnitexgenException("Sequence entry is missing reference to state or sequence")

		repeat = json.get("repeat", 1)
		weight = json.get("weight", 0)
		mark = json.get("mark")

		try:
			duration = int(evaluate_expr(str(json.get("duration", 1)), expr_locals))
		except Exception as e:
			raise MCAnitexgenException(f"Error while evaluating 'duration'") from e
		
		try:
			start = int(evaluate_expr(str(json.get('start')), expr_locals)) if 'start' in json else None
		except Exception as e:
			raise MCAnitexgenException(f"Error while evaluating 'start'") from e
				
		try:
			end = int(evaluate_expr(str(json.get('end')), expr_locals)) if 'end' in json else None
		except Exception as e:
			raise MCAnitexgenException(f"Error while evaluating 'end'") from e

		return SequenceEntry(type, ref, repeat, duration, weight, start, end, mark)

	def to_animated_entry(self, start:int, duration:int, textureAnimation: TextureAnimation) -> AnimatedEntry:
		if self.type == SequenceEntryType.STATE:
			return AnimatedState(start, start+duration, textureAnimation.states[self.ref].index)
		else:
			return textureAnimation.sequences[self.ref].to_animation(start, duration, textureAnimation)

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

class InvalidReferenceException(MCAnitexgenException):
	def __init__(self, parent_sequence: str, ref_target: str, ref_type: SequenceEntryType):
		if ref_type == SequenceEntryType.STATE:
			super(InvalidReferenceException, self).__init__(f"Reference '{ref_target}' in sequence '{parent_sequence}' does not name a state")
		elif ref_type == SequenceEntryType.SEQUENCE:
			super(InvalidReferenceException, self).__init__(f"Reference '{ref_target}' in sequence '{parent_sequence}' does not name a sequence")

######################
# Expression parsing #
######################

def evaluate_expr(expr:str, expr_locals: Dict = dict()) -> Any:
	return eval(expr, expression_globals, expr_locals)

expression_globals = {
	# Constants
	"e": math.e,
	"pi": math.pi,

	# Trigonometry
	"deg": math.degrees,
	"rad": math.radians,
	"sin": math.sin,
	"sinh": math.sinh,
	"asinh": math.asin,
	"asinh": math.asinh,
	"cos": math.cos,
	"cosh": math.cosh,
	"acos": math.acos,
	"acosh": math.acosh,
	"tan": math.tan,
	"tanh": math.tanh,
	"atan": math.atan,
	"atan2": math.atan2,
	"atanh": math.atanh,

	# Math
	"pow": math.pow,
	"mod": math.fmod,
	"log": math.log,
	"sqrt": math.sqrt,
	"exp": math.exp,
	"factorial": math.factorial,
	"ceil": math.ceil,
	"floor": math.floor,
	"gcd": math.gcd,
}