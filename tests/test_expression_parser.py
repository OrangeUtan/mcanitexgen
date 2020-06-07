from typing import Dict, List
from mcmetagen.TextureAnimation import TextureAnimation, AnimationMark

def assert_marks(json: Dict, expected: Dict[str, List[AnimationMark]]):
	parsedTextureAnimation = TextureAnimation.from_json("root", json)
	assert expected == parsedTextureAnimation.marks

def test_marks_in_state_and_sequence():
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

def test_marks_in_repeated_entries():
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

def test_multiple_references_to_seq_with_mark():
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