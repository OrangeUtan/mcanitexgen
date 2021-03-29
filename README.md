![](https://img.shields.io/github/license/orangeutan/mcanitexgen)
![](https://img.shields.io/badge/python-3.8|3.9-blue)
[![](https://img.shields.io/pypi/v/mcanitexgen)](https://pypi.org/project/mcanitexgen/)
![](https://raw.githubusercontent.com/OrangeUtan/mcanitexgen/6067435cfa656819bcef780415e36ff3e5f117bb/coverage.svg)
![](https://img.shields.io/badge/mypy-checked-green)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
![](https://img.shields.io/badge/pre--commit-enabled-green)
![](https://github.com/orangeutan/mcanitexgen/workflows/CLI/badge.svg)

# Animated-texture generator for Minecraft
Anitexgen is a generator for ".mcmeta" files that Minecraft uses to animate textures.<br>

It allows you to write texture animations in Python instead of json. Using a proper programming language enables you to create much more complex animations, like this model that uses 3 animated textures to create a moving dog.

<img src="https://raw.githubusercontent.com/OrangeUtan/mcanitexgen/master/examples/dog/dog.gif" width="400" style="image-rendering: pixelated; image-rendering: -moz-crisp-edges; image-rendering: crisp-edges;"/>

- [Installation](#Installation)
- [Usage](#Usage)
- [Getting started](#Getting-started)
  - [Create a simple animation](#Create-a-simple-animation)
  - [More examples](https://github.com/OrangeUtan/mcanitexgen/tree/main/examples)
- [Changelog](https://github.com/OrangeUtan/mcanitexgen/blob/main/CHANGELOG.md)

# Installation
```
pip install mcanitexgen
```

# Usage
Generate .mcmeta files for all animations in an animation file
```shell
$ mcanitexgen generate <animation_file>
    -o, --out       The output directory of the generated files
    -m, --minify    Minify generated files
    -i, --indent    Indentation used when generating files
    --dry           Dry run. Don't generate any files
```
Create gifs for all animations in an animation file
```shell
$ mcanitexgen gif <animation_file>
    -o, --out       The output directory of the generated files
```

# Getting started
## Create a simple animation
We are going to create this blinking Steve:<br>
<img src="https://raw.githubusercontent.com/OrangeUtan/mcanitexgen/master/examples/steve/steve.gif" width="100" style="image-rendering: pixelated; image-rendering: -moz-crisp-edges; image-rendering: crisp-edges;"/>


First we have to create the different states of the animation.
I created a simple **steve.png** file:<br>
<img src="https://raw.githubusercontent.com/OrangeUtan/mcanitexgen/master/examples/steve/steve.png" width="100" style="image-rendering: pixelated; image-rendering: -moz-crisp-edges; image-rendering: crisp-edges;"/>

Top to Bottom: Looking normal, blinking, wink with right eye, wink with left eye.<br>
Now we can create the animation file **steve.animation .py** that uses these states to create an animation:<br>
```python
from mcanitexgen.animation import animation, TextureAnimation, State, Sequence

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
Files overview:
```
resourcepack
  ⠇
  textures
    └╴ item
       ├╴steve.png
       └╴steve.animation.py
```

Passing the animation file to Anitexgen will create a **steve.png.mcmeta** file:
```shell
$ mcanitexgen generate steve.animation.py
```
```json
steve.png.mcmeta
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
```
resourcepack
  ⠇
  textures
    └╴ item
       ├╴ steve.png
       ├╴ steve.animation.py
       └╴ steve.png.mcmeta
```
