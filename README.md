![](https://img.shields.io/github/license/orangeutan/mcanitexgen)
![](https://img.shields.io/badge/python-3.8|3.9-blue)
[![](https://img.shields.io/pypi/v/mcanitexgen)](https://pypi.org/project/mcanitexgen/)
![](./coverage.svg)
![](https://img.shields.io/badge/mypy-checked-green)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![](https://img.shields.io/badge/pre--commit-enabled-green)
![](https://github.com/orangeutan/mcanitexgen/workflows/test/badge.svg)

# Minecraft animated texture generator
Mcanitexgen is a generator for ".mcmeta" files that Minecraft uses to animate textures.<br>

## The full power of Python
Mcanitexgen allows you to write texture animations in Python instead of json. Using a programming language allows you to create much more complex animations, like this dog that has 3 textures that are synchronised with each other.

<img src="https://raw.githubusercontent.com/OrangeUtan/mcanitexgen/master/examples/dog/dog.gif" width="400" style="image-rendering: pixelated; image-rendering: -moz-crisp-edges; image-rendering: crisp-edges;"/>

## Install
`pip install mcanitexgen`

## Usage
- `python -m mcanitexgen generate <animation_file> [out_dir]` generates .mcmeta files for all animations in an animation file
- `python -m mcanitexgen gif <animation_file> [out_dir]` creates gifs for all animations in an animation file

# Example
We are going to create this animation.<br>
<img src="https://raw.githubusercontent.com/OrangeUtan/mcanitexgen/master/examples/steve/steve.gif" width="100" style="image-rendering: pixelated; image-rendering: -moz-crisp-edges; image-rendering: crisp-edges;"/>


First we have to create the different states of the animation.
I created a simple "steve.png" file:<br>
<img src="https://raw.githubusercontent.com/OrangeUtan/mcanitexgen/master/examples/steve/steve.png" width="100" style="image-rendering: pixelated; image-rendering: -moz-crisp-edges; image-rendering: crisp-edges;"/>

Top to Bottom: Looking normal, blinking, wink with right eye, wink with left eye.<br>
Now we can create the animation file "steve.animation.py" that uses these states to create an animation:<br>
```python
from mcanitexgen import animation, TextureAnimation, State, Sequence

@animation("steve.png")
class Steve(TextureAnimation):
  NORMAL = State(0)  # Look normal
  BLINK = State(1)
  WINK_RIGHT = State(2)  # Wink with right eye
  WINK_LEFT = State(3)  # Wink with left eye

  # Look normal and blink shortly
  look_and_blink = Sequence(NORMAL(duration=60), BLINK(duration=2))

  # The main Sequence used to create the animation
  main = Sequence(
    3 * look_and_blink,  # Play "look_and_blink" Sequence 3 times
    NORMAL(duration=60),
    WINK_LEFT(duration=30),
    look_and_blink,
    NORMAL(duration=60),
    WINK_RIGHT(duration=30),
  )
```

Now run `python -m mcanitexgen steve.animation.py` and Mcanitexgen will create a "steve.png.mcmeta" file:
```json
{
  "animation": {
      "interpolate": false,
      "frametime": 1,
      "frames": [
        {"index": 0, "time": 60},
        {"index": 1, "time": 2},
        {"index": 0, "time": 60},
        {"index": 1, "time": 2},
        {"index": 0, "time": 60},
        {"index": 1, "time": 2},
        {"index": 0, "time": 60},
        {"index": 3, "time": 30},
        {"index": 0, "time": 60},
        {"index": 1, "time": 2},
        {"index": 0, "time": 60},
        {"index": 2, "time": 30}
      ]
  }
}
```

More complex examples can be found in the [here](https://github.com/OrangeUtan/mcanitexgen/tree/master/examples)
