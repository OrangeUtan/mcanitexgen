import os, yaml, json
from typing import List, Dict, Iterable
from mcmetagen.TextureAnimation import *

class Parser:
	@classmethod
	def _parse_animation_file(cls, path:str) -> Dict[str,TextureAnimation]:
		json = Parser._load_yaml_file(path)
		texture_animations = dict()
		for name, ta_json in json.items():
			texture_animations[name] = TextureAnimation.from_json(name, ta_json, texture_animations)

		return texture_animations

	@classmethod
	def _animated_entry_to_frames(cls, entry: AnimatedEntry) -> Generator[Dict, None, None]:
		return Parser._combine_consecutive_frames(entry.to_frames())

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
	def _load_yaml_file(cls, path):
		with open(path) as file:
			return yaml.load(file, Loader=yaml.Loader)