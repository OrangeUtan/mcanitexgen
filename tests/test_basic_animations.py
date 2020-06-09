import pytest
from mcanitexgen.TextureAnimation import *
from mcanitexgen.Exceptions import *

def assert_states(json: Dict, expected: Dict[str, AnimatedState]):
	parsedTextureAnimation = TextureAnimation.from_json("root",json)
	assert expected == parsedTextureAnimation.states

def assert_sequences(json: Dict, expected: Dict[str, Sequence]):
	parsedTextureAnimation = TextureAnimation.from_json("root",json)
	assert expected == parsedTextureAnimation.sequences

def assert_animation(json: Dict, expected: AnimatedGroup):
	parsedTextureAnimation = TextureAnimation.from_json("root",json)
	assert expected == parsedTextureAnimation.animation

def assert_exception(json: Dict, exception_type, message: Optional[str] = None):
	with pytest.raises(exception_type) as e_info:
		parsedTextureAnimation = TextureAnimation.from_json("root",json)
	assert type(e_info.value) == exception_type
	if message:
		assert message in str(e_info.value)

def test_references():
	# Reference non existant state in root
	assert_exception(
		{
			"states": [],
			"animation": [
				{ "state": "a" }
			]
		},
		InvalidReferenceException, str(InvalidReferenceException('', 'a', SequenceEntryType.STATE))
	)
	assert_exception(
		{
			"states": ["a","b","c"],
			"animation": [
				{ "state": "d" }
			]
		},
		InvalidReferenceException, str(InvalidReferenceException('', 'd', SequenceEntryType.STATE))
	)

	# Reference non existant state in sequence
	assert_exception(
		{
			"states": ["a","b","c"],
			"sequences": {
				"seq_a": [
					{ "state": "d" }
				]
			},
			"animation": [
				{ "sequence": "seq_a" }
			]
		},
		InvalidReferenceException, str(InvalidReferenceException('seq_a', 'd', SequenceEntryType.STATE))
	)

	# Reference non existant sequence in root
	assert_exception(
		{
			"states": ["a","b","c"],
			"animation": [
				{ "sequence": "seq_a" }
			]
		},
		InvalidReferenceException, str(InvalidReferenceException('', 'seq_a', SequenceEntryType.SEQUENCE))
	)
	assert_exception(
		{
			"states": ["a","b","c"],
			"sequences": {
				"seq_a": [
					{ "state": "a" }
				]
			},
			"animation": [
				{ "sequence": "seq_b" }
			]
		},
		InvalidReferenceException, str(InvalidReferenceException('', 'seq_b', SequenceEntryType.SEQUENCE))
	)

	# Reference non existant sequence in sequence
	assert_exception(
		{
			"states": ["a","b","c"],
			"sequences": {
				"seq_a": [
					{ "sequence": "seq_b" }
				]
			},
			"animation": [
				{ "sequence": "seq_a" }
			]
		},
		InvalidReferenceException, str(InvalidReferenceException('seq_a', 'seq_b', SequenceEntryType.SEQUENCE))
	)

def test_states():
	# Parse states correctly
	assert_states(
		{
			"states": ["a","b","c"],
			"animation": [
				{ "state": "a" }
			]
		}, 
		{ "a": State("a", 0), "b": State("b", 1), "c": State("c", 2) }
	)

	# Pass a duration to state
	assert_animation(
		{
			"states": ["a","b","c"],
			"sequences": {
				"seq_a": [
					{ "state": "b", "duration": 5 } # <-- duration in nested
				]
			},
			"animation": [
				{ "state": "c", "duration": 5 }, # <-- duration in root
				{ "sequence": "seq_a" }
			]
		}, 
		AnimatedGroup(0,10,"", [
			AnimatedState(0,5,2),
			AnimatedGroup(5,10,"seq_a", [
				AnimatedState(5,10,1)
			])
		])
	)

	# Pass no duration to state
	assert_animation(
		{
			"states": ["a","b","c"],
			"sequences": {
				"seq_a": [
					{ "state": "b" } # <-- no duration in nested
				]
			},
			"animation": [
				{ "state": "c" }, # <-- no duration in root
				{ "sequence": "seq_a" }
			]
		}, 
		AnimatedGroup(0,2,"", [
			AnimatedState(0,1,2),
			AnimatedGroup(1,2,"seq_a", [
				AnimatedState(1,2,1)
			])
		])
	)

def test_fixed_duration_sequences():
	# Nested
	assert_animation(
		{
			"states": ["a","b","c"],
			"sequences": {
				"seq_a": [
					{ "state": "a", "duration": 10 },
					{ "sequence": "seq_b" }
				],
				"seq_b": [
					{ "state": "b", "duration": 10 }
				]
			},
			"animation": [
				{ "sequence": "seq_a" }
			]
		},
		AnimatedGroup(0,20,"",[
			AnimatedGroup(0,20,"seq_a", [
				AnimatedState(0,10,0),
				AnimatedGroup(10,20,"seq_b", [
					AnimatedState(10,20,1)
				])
			])
		])
	)


def test_basic_weighted_sequence():
	assert_animation(
		{
			"states": ["a","b","c"],
			"sequences": {
				"seq_a": [
					{ "state": "b", "weight": 1 },
					{ "state": "a", "weight": 1 },
					{ "state": "b", "weight": 3 }
				]
			},
			"animation": [
				{ "sequence": "seq_a", "duration": 123 }
			]
		},
		AnimatedGroup(0,123,"", [
			AnimatedGroup(0,123,"seq_a", [
				AnimatedState(0,25,1),
				AnimatedState(25,50,0),
				AnimatedState(50,123,1)	
			])
		])
	)

def test_mixed_sequence():
	assert_animation(
		{
			"states": ["a","b","c"],
			"sequences": {
				"seq_a": [
					{ "state": "a", "duration": 5 },
					{ "state": "b", "weight": 1 },
					{ "state": "a", "duration": 5 },
					{ "state": "b", "weight": 3 }
				]
			},
			"animation": [
				{ "sequence": "seq_a", "duration": 123 }
			]
		},
		AnimatedGroup(0,123,"", [
			AnimatedGroup(0,123,"seq_a", [
				AnimatedState(0,5,0),
				AnimatedState(5,33,1),
				AnimatedState(33,38,0),
				AnimatedState(38,123,1)
			])
		])
	)

def test_pass_no_duration_to_weighted_sequences():
	assert_exception(
		{
			"states": ["a","b","c"],
			"sequences": {
				"seq_a": [
					{ "state": "a", "weight": 1 },
					{ "state": "b", "weight": 1 }
				]
			},
			"animation": [
				{ "sequence": "seq_a" } # <-- duration 1 not enough for weighted 2 entries
			]
		},
		MCAnitexgenException, "Duration of '1' exhausted"
	)
	assert_exception(
		{
			"states": ["a","b","c"],
			"sequences": {
				"seq_a": [
					{ "sequence": "seq_b", "weight": 1 },
					{ "sequence": "seq_b", "weight": 1 }
				],
				"seq_b": [
					{ "state": "b", "duration": 10 }
				]
			},
			"animation": [
				{ "sequence": "seq_a" } # <-- duration 1 not enough for weighted 2 entries
			]
		},
		MCAnitexgenException, "Sequence 'seq_a': Duration must be at least '20', but was '1'"
	)