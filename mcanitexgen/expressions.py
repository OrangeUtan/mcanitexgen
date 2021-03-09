import math


def evaluate_int(expr: str, expr_locals: dict = dict()) -> int:
    return int(eval(expr, expression_globals, expr_locals))


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
