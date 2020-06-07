import pytest
from mcmetagen.TextureAnimation import *

def assert_animation(json: Dict, expected: AnimatedGroup):
	parsedTextureAnimation = TextureAnimation.from_json("root",json)
	assert expected == parsedTextureAnimation.animation

def assert_exception(json: Dict, exception_type, message: Optional[str] = None):
	with pytest.raises(exception_type) as e_info:
		parsedTextureAnimation = TextureAnimation.from_json("root",json)
	assert type(e_info.value) == exception_type
	if message:
		assert message in str(e_info.value)

def assert_marks(json: Dict, expected: Dict[str, AnimationMark]):
	parsedTextureAnimation = TextureAnimation.from_json("root",json)
	assert expected == parsedTextureAnimation.marks

class TestMarks:

	def test_marks_in_state_and_sequence(self):
		assert_marks(
			{
				"states": ["a", "b", "c"],
				"sequences": {
					"seq_a": [
						{ "state": "c", "duration": 10, "mark": "in seq_a" }
					]
				},
				"animation": [
					{ "state": "a", "duration": 10, "mark": "state a" },
					{ "state": "b", "duration": 10, "mark": "state b" },
					{ "sequence": "seq_a", "mark": "seq_a" }
				]
			},
			{
				"state a": [AnimationMark(0,10)],
				"state b": [AnimationMark(10,20)],
				"seq_a": [AnimationMark(20,30)],
				"in seq_a": [AnimationMark(20,30)]
			}
		)

	def test_marks_in_repeated_entries(self):
		assert_marks(
			{
				"states": ["a", "b", "c"],
				"sequences": {
					"seq_a": [
						{ "state": "a", "duration": 5, "mark": "in seq_a" }
					]
				},
				"animation": [
					{ "state": "a", "duration": 10, "mark": "state a", "repeat": 3 },
					{ "sequence": "seq_a", "mark": "seq_a", "repeat": 3 }
				]
			},
			{
				"state a": [
					AnimationMark(0,10),
					AnimationMark(10,20),
					AnimationMark(20,30)
				],
				"seq_a": [
					AnimationMark(30,35),
					AnimationMark(35,40),
					AnimationMark(40,45)
				],
				"in seq_a": [
					AnimationMark(30,35),
					AnimationMark(35,40),
					AnimationMark(40,45)
				]
			}
		)

	def test_multiple_references_to_seq_with_mark(self):
		assert_marks(
			{
				"states": ["a", "b", "c"],
				"sequences": {
					"seq_a": [
						{ "state": "a", "duration": 5, "mark": "in seq_a" }
					]
				},
				"animation": [
					{ "sequence": "seq_a"},
					{ "sequence": "seq_a"}
				]
			},
			{
				"in seq_a": [
					AnimationMark(0,5),
					AnimationMark(5,10),
				]
			}
		)

class TestBasicExpressions:
	def test_basic_end_expr(self):
		assert_animation(
			{
				"states": ["a","b","c"],
				"animation": [
					{ "state": "a", "duration": 5 },
					{ "state": "b", "end": "95" },
					{ "state": "a", "duration": 5 }
				]
			},
			AnimatedGroup(0,100,"", [
				AnimatedState(0,5,0),
				AnimatedState(5,95,1),
				AnimatedState(95,100,0)
			])
		)

	def test_basic_nested_end_expr(self):
		assert_animation(
			{
				"states": ["a","b","c"],
				"sequences": {
					"seq_a": [
						{ "state": "b", "end": 95 }
					]
				},
				"animation": [
					{ "state": "a", "duration": 5 },
					{ "sequence": "seq_a"},
					{ "state": "a", "duration": 5 }
				]
			},
			AnimatedGroup(0,100,"", [
				AnimatedState(0,5,0),
				AnimatedGroup(5,95,"seq_a",[
					AnimatedState(5,95,1)
				]),
				AnimatedState(95,100,0)
			])
		)

	def test_end_already_reached(self):
		""" An entry has its 'end' property set, but a previous entry already reaches that time.
			'end' works by setting the duration of the current entry to the time needed to reach that end time.
			If a previous entry already reached that time, the current entrys duration would be 0, thus invalid. 
		"""

		assert_exception(
			{
				"states": ["a","b","c"],
				"animation": [
					{ "state": "a", "duration": 95 },
					{ "state": "b", "end": 95 }, # <--
					{ "state": "a", "duration": 5 }
				]
			},
			McMetagenException, "Sequence '': 2. entry can't end at '95'"
		)

	def test_end_already_reached_nested(self):
		assert_exception(
			{
				"states": ["a","b","c"],
				"sequences": {
					"seq_a": [
						{ "state": "b", "end": 95 } # <--
					]
				},
				"animation": [
					{ "state": "a", "duration": 95 },
					{ "sequence": "seq_a"},
					{ "state": "a", "duration": 5 }
				]
			},
			McMetagenException, "Sequence 'seq_a': 1. entry can't end at '95'"
		)

	def test_basic_start_expr(self):
		assert_animation(
			{
				"states": ["a","b","c"],
				"animation": [
					{ "state": "a", "duration": 5 },
					{ "state": "b", "start": 85, "duration": 10 }, # <--
					{ "state": "a", "duration": 5 }
				]
			},
			AnimatedGroup(0,100,"", [
				AnimatedState(0,85,0),
				AnimatedState(85,95,1),
				AnimatedState(95,100,0)
			])
		)

	def test_basic_nested_start_expr(self):
		assert_animation(
			{
				"states": ["a","b","c"],
				"sequences": {
					"seq_a": [
						{ "state": "b", "start": 85, "duration": 10 } # <--
					]
				},
				"animation": [
					{ "state": "a", "duration": 5 },
					{ "sequence": "seq_a" },
					{ "state": "a", "duration": 5 }
				]
			},
			AnimatedGroup(0,100,"", [
				AnimatedState(0,85,0),
				AnimatedGroup(85,95,"seq_a", [
					AnimatedState(85,95,1)
				]),
				AnimatedState(95,100,0)
			])
		)

	def test_start_with_no_previous_entry(self):
		""" An entry has its 'start' attribute set, but there is no previous entry.

			'start' works by extending the duration of the previous entry until the start of the current one.
			Of course thats impossible if there is no previous entry. 
		"""

		assert_exception(
			{
				"states": ["a","b","c"],
				"animation": [
					{ "state": "b", "start": 85, "duration": 10 },
					{ "state": "a", "duration": 5 }
				]
			},
			McMetagenException, "there is no previous entry"
		)

	def test_start_with_no_previous_entry_nested(self):
		assert_exception(
			{
				"states": ["a","b","c"],
				"sequences": {
					"seq_a": [
						{ "state": "b", "start": 85, "duration": 10 }
					]
				},
				"animation": [
					{ "sequence": "seq_a" }, # <-- tries to start at 85, but no previous
					{ "state": "a", "duration": 5 }
				]
			},
			McMetagenException, "there is no previous entry"
		)

ta1 = TextureAnimation.from_json("ta1",
	{
		"states": ["a", "b", "c"],
		"sequences": {
			"seq_a": [
				{ "state": "a", "duration": 5, "mark": "in seq_a" }
			]
		},
		"animation": [
			{ "sequence": "seq_a"},
			{ "sequence": "seq_a"}
		]
	}
)