# mcanitexgen (MC animated texture generator)
Mcanitexgen is a python generator for complex animated textures. It generates .mcmeta files from .animation.yml files.

## Install
`pip install mcanitexgen`

## Usage
`python -m anitexgen <dir>` where `dir` is the a directory containing animation files.
Parses all animation files (.animation.yml) in the directory and generates .mcmeta files from them.

## Example
More complex examples can be found in `/examples`. This is only a simple example.<br>
<br>
A simple animation where a head blinks, then winks with the left eye and then with the right eye.
```yaml
head:
  texture: "<rel_path>/head.png"
  states:
    - normal # Head looking normal
    - blink_both # Blinking with both eyes
    - wink_left # Blinking with only the left eye
    - wink_right # Blinking with only the right eye
  animation:
    - { state: normal, duration: 20 }
    - { state: blink, duration: 3 }
    - { state: normal, duration: 20 }
    - { state: blink, duration: 3 }
    - { state: normal, duration: 20 }
    - { state: wink_left, duration: 10 }
    - { state: normal, duration: 20 }
    - { state: blink, duration: 3 }
    - { state: normal, duration: 20 }
    - { state: wink_right, duration: 10 }
```
Mcmetagen then generates an animation for the texture "<rel_path>/head.png" => The output is "<rel_path>/head.png.mcmeta".
