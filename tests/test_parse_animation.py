import pytest
from mcmetagen.TextureAnimation import *
from mcmetagen.Exceptions import *

def assert_states(json: Dict, expected: Dict[str, AnimatedState]):
	parsedTextureAnimation = TextureAnimation.from_json(json)
	assert expected == parsedTextureAnimation.states

def assert_sequences(json: Dict, expected: Dict[str, Sequence]):
	parsedTextureAnimation = TextureAnimation.from_json(json)
	assert expected == parsedTextureAnimation.sequences

def assert_animation(json: Dict, expected: AnimatedGroup):
	parsedTextureAnimation = TextureAnimation.from_json(json)
	assert expected == parsedTextureAnimation.animation

def assert_exception(json: Dict, exception_type, message: Optional[str] = None):
	with pytest.raises(exception_type) as e_info:
		parsedTextureAnimation = TextureAnimation.from_json(json)
	assert type(e_info.value) == exception_type
	if message:
		assert message in str(e_info.value)

def test_references():
	# Reference non existant state in root
	assert_exception(
		{
			"states": [],
			"animation": [
				{ "type": "state", "ref": "a" }
			]
		},
		InvalidReferenceException, str(InvalidReferenceException('', 'a', SequenceEntryType.STATE))
	)
	assert_exception(
		{
			"states": ["a","b","c"],
			"animation": [
				{ "type": "state", "ref": "d" }
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
					{ "type": "state", "ref": "d" }
				]
			},
			"animation": [
				{ "type": "sequence", "ref": "seq_a" }
			]
		},
		InvalidReferenceException, str(InvalidReferenceException('seq_a', 'd', SequenceEntryType.STATE))
	)

	# Reference non existant sequence in root
	assert_exception(
		{
			"states": ["a","b","c"],
			"animation": [
				{ "type": "sequence", "ref": "seq_a" }
			]
		},
		InvalidReferenceException, str(InvalidReferenceException('', 'seq_a', SequenceEntryType.SEQUENCE))
	)
	assert_exception(
		{
			"states": ["a","b","c"],
			"sequences": {
				"seq_a": [
					{ "type": "state", "ref": "a" }
				]
			},
			"animation": [
				{ "type": "sequence", "ref": "seq_b" }
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
					{ "type": "sequence", "ref": "seq_b" }
				]
			},
			"animation": [
				{ "type": "sequence", "ref": "seq_a" }
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
				{ "type": "state", "ref": "a" }
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
					{ "type": "state", "ref": "b", "duration": 5 } # <-- duration in nested
				]
			},
			"animation": [
				{ "type": "state", "ref": "c", "duration": 5 }, # <-- duration in root
				{ "type": "sequence", "ref": "seq_a" }
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
					{ "type": "state", "ref": "b" } # <-- no duration in nested
				]
			},
			"animation": [
				{ "type": "state", "ref": "c" }, # <-- no duration in root
				{ "type": "sequence", "ref": "seq_a" }
			]
		}, 
		AnimatedGroup(0,2,"", [
			AnimatedState(0,1,2),
			AnimatedGroup(1,2,"seq_a", [
				AnimatedState(1,2,1)
			])
		])
	)

def test_sequences():
	# Pass no duration to fixed duration sequence
	assert_animation(
		{
			"states": ["a","b","c"],
			"sequences": {
				"seq_a": [
					{ "type": "state", "ref": "a", "duration": 10 },
					{ "type": "sequence", "ref": "seq_b" }
				],
				"seq_b": [
					{ "type": "state", "ref": "b", "duration": 10 }
				]
			},
			"animation": [
				{ "type": "sequence", "ref": "seq_a" } # <-- no duration passed
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

	# Pass no duration to weighted sequence
	assert_exception(
		{
			"states": ["a","b","c"],
			"sequences": {
				"seq_a": [
					{ "type": "state", "ref": "a", "weight": 1 },
					{ "type": "state", "ref": "b", "weight": 1 }
				]
			},
			"animation": [
				{ "type": "sequence", "ref": "seq_a" } # <-- duration 1 not enough for weighted 2 entries
			]
		},
		McMetagenException, "Duration '1' is not enough"
	)

	
# def test_pass_duration_to_mixed_sequence():
# 	# Pass duration to mixed sequence
# 	assert_animation(
# 		{
# 			"states": ["a","b","c"],
# 			"sequences": {
# 				"seq_a": [
# 					{ "type": "state", "ref": "a", "weight": 1 },
# 					{ "type": "state", "ref": "b", "duration": 10 }
# 				]
# 			},
# 			"animation": [
# 				{ "type": "sequence", "ref": "seq_a", "duration": 11 } # <-- duration 1 not enough for weighted 2 entries
# 			]
# 		},
# 		AnimatedGroup(0,11,"", [
# 			AnimatedGroup(0,11,"seq_a",[
# 				AnimatedState(0,1,0),
# 				AnimatedState(1,11,1)
# 			])
# 		])
# 	)