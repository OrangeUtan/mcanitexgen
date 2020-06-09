import pytest
from typing import Any
from mcanitexgen.TextureAnimation import *

def assert_animation(json: Dict, expected: AnimatedGroup, texture_animations: Dict[str,TextureAnimation] = dict()):
	parsedTextureAnimation = TextureAnimation.from_json("root",json, texture_animations)
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

def assert_constants(json: Dict, expected: Dict[str, Any]):
	parsedTextureAnimation = TextureAnimation.from_json("root",json)
	assert expected == parsedTextureAnimation.constants

def assert_expr_evaluation(expr:str, expected:Any, expr_locals: Dict[str,Any] = dict()):
	assert expected == evaluate_expr(expr, expr_locals)

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

class TestArithmeticExpressions:
	def test_values(self):
		assert_expr_evaluation("3894793745", 3894793745)
		assert_expr_evaluation("'a string'", "a string")
		assert_expr_evaluation("[1,2,3]", [1,2,3])

	def test_basic_arithmetic(self):
		assert_expr_evaluation("(4+5)-(1+2+3)", 3)
		assert_expr_evaluation("(7*4)/2", 14)

	def test_arithmetic_functions(self):
		assert_expr_evaluation("e", math.e)
		assert_expr_evaluation("pi", math.pi)
		assert_expr_evaluation("pow(3,3)", 27)
		assert_expr_evaluation("mod(230,100)", 30)
		assert_expr_evaluation("log(e)+log(100,10)", 1+2)
		assert_expr_evaluation("sqrt(4)", 2)
		assert_expr_evaluation("exp(log(3453))", pytest.approx(3453))
		assert_expr_evaluation("factorial(12)", 479001600)
		assert_expr_evaluation("ceil(12.1123574687456)", 13)
		assert_expr_evaluation("floor(34.992329923)", 34)
		assert_expr_evaluation("gcd(234,123)", 3)

	def test_trigonometry(self):
		assert_expr_evaluation("sin(pi)", pytest.approx(0))
		assert_expr_evaluation("cos(0)", 1)

class TestVariables:
	def test_basic(self):
		assert_constants(
			{
				"constants": {
					"x": "(4+5)-(1+2+3)",
					"y": "pow(3,3)"
				},
				"states": ["a", "b", "c"],
				"animation": [
					{ "state": "a", "duration": 10 }
				]
			},
			{
				"x": 3,
				"y": 27
			}
		)

	def test_reference_const_in_const(self):
		assert_constants(
			{
				"constants": {
					"x": "pow(3,3)",
					"y": "x*2"
				},
				"states": ["a", "b", "c"],
				"animation": [
					{ "state": "a", "duration": 10 }
				]
			},
			{
				"x": 27,
				"y": 54
			}
		)

	def test_reference_const_in_sequence(self):
		assert_animation(
			{
				"constants": {
					"seq_a_duration": 20,
					"state_a": 42
				},
				"states": ["a","b","c"],
				"sequences": {
					"seq_a": [
						{ "state": "b", "weight": 1 },
					]
				},
				"animation": [
					{ "state": "a", "end": "state_a" },
					{ "sequence": "seq_a", "duration": "seq_a_duration" }
				]
			},
			AnimatedGroup(0,62,"", [
				AnimatedState(0,42,0),
				AnimatedGroup(42,62,"seq_a",[
					AnimatedState(42,62,1)
				])
			])
		)

class TestEndExpr:
	texture_animations = {
		"ta1": TextureAnimation.from_json("ta1",
			{
				"states": ["a", "b", "c"],
				"sequences": {
					"seq_a": [
						{ "state": "a", "duration": 5, "mark": "in seq_a" }
					],
					"seq_b": [
						{ "state": "b", "duration": 5, "mark": "in seq_b" }
					]
				},
				"animation": [
					{ "sequence": "seq_a", "mark": "seq_a"},
					{ "sequence": "seq_b", "mark": "seq_b"}
				]
			}
		)
	}

	def test_basic(self):
		assert_animation(
			{
				"states": ["a","b","c"],
				"animation": [
					{ "state": "a", "end": "(12/4)+2-3" },
					{ "state": "a", "end": "ceil(30/4)" },
					{ "state": "b", "end": "floor(45/4)" },
					{ "state": "c", "end": "pow(3,3)" },
					{ "state": "a", "end": "mod(230,100)" },
					{ "state": "b", "end": "30 + 10*sin(rad(20))" }
				]
			},
			AnimatedGroup(0,33,"", [
				AnimatedState(0,2,0),
				AnimatedState(2,8,0),
				AnimatedState(8,11,1),
				AnimatedState(11,27,2),
				AnimatedState(27,30,0),
				AnimatedState(30,33,1)
			])
		)

	def test_basic_nested(self):
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

	def test_already_reached(self):
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
			MCAnitexgenException, "Sequence '': 2. entry can't end at '95'"
		)

	def test_already_reached_nested(self):
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
			MCAnitexgenException, "Sequence 'seq_a': 1. entry can't end at '95'"
		)

	def test_with_mark_reference(self):
		assert_animation(
			{
				"states": ["a","b","c"],
				"animation": [
					{ "state": "a", "end": "ta1.mark('seq_b').end" }
				]
			},
			AnimatedGroup(0,10,"", [
				AnimatedState(0,10,0)
			]),
			self.texture_animations
		)

class TestStartExpr:

	def test_basic(self):
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

	def test_basic_nested(self):
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

	def test_with_no_previous_entry(self):
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
			MCAnitexgenException, "there is no previous entry"
		)

	def test_with_no_previous_entry_nested(self):
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
			MCAnitexgenException, "there is no previous entry"
		)

class TestDurationExpr:
	def test_basic_duration_expr(self):
		assert_animation(
			{
				"states": ["a","b","c"],
				"animation": [
					{ "state": "a", "duration": "(12/4)+2-3" },
					{ "state": "a", "duration": "ceil(30/4)" },
					{ "state": "b", "duration": "floor(45/4)" },
					{ "state": "c", "duration": "pow(3,3)" },
					{ "state": "a", "duration": "mod(230,100)" },
					{ "state": "b", "duration": "30 + 10*sin(rad(20))" }
				]
			},
			AnimatedGroup(0,111,"", [
				AnimatedState(0,2,0),
				AnimatedState(2,10,0),
				AnimatedState(10,21,1),
				AnimatedState(21,48,2),
				AnimatedState(48,78,0),
				AnimatedState(78,111,1)
			])
		)