# Minecraft animated texture generator
Mcanitexgen is a generator for ".mcmeta" files that Minecraft uses to animate textures.<br>

## The full power of Python
Mcanitexgen allows you to write texture animations in Python instead of json. Using a programming language allows you to create much more complex animations, like this dog that has 3 textures that are synchronised with each other.

<img src="examples/dog/dog.gif" width="400" style="image-rendering: pixelated; image-rendering: -moz-crisp-edges; image-rendering: crisp-edges;"/>

Features:
- Synchronise multiple animations with each other
-

## Install
`pip install mcanitexgen`

## Usage
- `python -m mcanitexgen <animation_file> [out_dir]` generates ".mcmeta" for all animations in the animation file

# Example
We are going to create an animation in which Steve blinks, then winks with his left eye and finally winks with his right eye.<br>
First we have to create the different states of the animation.
I created a simple "steve.png" file:<br>
<img src="img/anim_example.png" width="100" style="image-rendering: pixelated; image-rendering: -moz-crisp-edges; image-rendering: crisp-edges;"/>
Top to Bottom: Looking normal, blinking, wink with right eye, wink with left eye.<br>


Now we can create the animation file "steve.animation.py" that uses these states to create an animation:<br>
```python
from mcanitexgen import animation, TextureAnimation, State, Sequence

@animation("steve.png")
class Steve(TextureAnimation):
  NORMAL = State(0)     # Look normal
  BLINK = State(1)
  WINK_RIGHT = State(2) # Wink with right eye
  WINK_LEFT = State(3)  # Wink with left eye

  # Look normal and blink shortly
  look_and_blink = Sequence(
    NORMAL(duration=20),
    BLINK(duration=3)
  )

  # The main Sequence used to create the animation
  main = Sequence(
    3 * look_and_blink, # Play "look_and_blink" Sequence 3 times
    WINK_LEFT(duration=10),
    look_and_blink,
    NORMAL(duration=20),
    WINK_RIGHT(duration=10)
  )
```

Now run `python -m mcanitexgen steve.animation.py` and Mcanitexgen will create a "steve.png.mcmeta" file:
```json
{
  "animation": {
    "interpolate": false,
    "frametime": 1,
    "frames": [
      {"index": 0, "time": 20},
      {"index": 1, "time": 3},
      {"index": 0, "time": 20},
      {"index": 1, "time": 3},
      {"index": 0, "time": 20},
      {"index": 1, "time": 3},
      {"index": 3, "time": 10},
      {"index": 0, "time": 20},
      {"index": 1, "time": 3},
      {"index": 0, "time": 20},
      {"index": 2, "time": 10}
    ]
  }
}
```
<br>
More complex examples can be found in [examples](https://github.com/OrangeUtan/mcanitexgen/tree/master/examples).
