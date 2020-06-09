import os, json
import ruamel.yaml as yaml
from typing import List, Dict, Iterable
from mcanitexgen.TextureAnimation import *

class Parser:
	@classmethod
	def generate_animations(cls, dir:str = "."):
		for path in Parser._get_animation_files_in_dir(dir):
			Parser.generate_animations_from_file(path)

	@classmethod
	def generate_animations_from_file(cls, path:str):
		for _,texture_animation in Parser._parse_animation_file(path).items():
			if texture_animation.texture:
				anim = Parser._animation_from_texture_animation(texture_animation)
				outfile = f"{os.path.join(os.path.dirname(path), texture_animation.texture)}.mcmeta"
				with open(outfile, "w+") as file:
					json.dump(anim, file, indent=4)

	@classmethod
	def _animation_from_texture_animation(cls, anim: TextureAnimation):
		frames = list(Parser._combine_consecutive_frames(anim.animation.to_frames()))
		return {
			"animation": {
				"interpolate": anim.interpolate,
				"frametime": 1,
				"frames": frames
			}
		}

	@classmethod
	def _combine_consecutive_frames(cls, frames:Iterable[Dict]) -> Dict:
		prev_frame = None
		for frame in frames:
			if prev_frame:
				if prev_frame["index"] == frame["index"]:
					prev_frame["time"] += frame["time"]
				else:
					yield prev_frame
					prev_frame = frame
			else:
				prev_frame = frame

		if prev_frame:
			yield prev_frame

	@classmethod
	def _get_animation_files_in_dir(cls, dir_path:str) -> Generator[str,None,None]:
		for root, dirs, files in os.walk(dir_path):
			animation_files = filter(lambda file: file.endswith(".animation.yml"), files)
			for file in map(lambda file: os.path.join(root, file), animation_files):
				yield file

	@classmethod
	def _parse_animation_file(cls, path:str) -> Dict[str,TextureAnimation]:
		json = Parser._load_yaml_file(path)
		texture_animations = dict()
		for name, ta_json in json.items():
			texture_animations[name] = TextureAnimation.from_json(name, ta_json, texture_animations)

		return texture_animations

	@classmethod
	def _load_yaml_file(cls, path):
		with open(path) as file:
			return yaml.load(file, Loader=yaml.Loader)