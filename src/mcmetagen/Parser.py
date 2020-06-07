import os, yaml, json
from typing import List, Dict
from mcmetagen.TextureAnimation import TextureAnimation

class Parser:
	@classmethod
	def parse_animation_file(cls, path:str) -> Dict[str,TextureAnimation]:
		json = Parser.load_yaml_file(path)
		texture_animations = dict()
		for name, ta_json in json.items():
			texture_animations[name] = TextureAnimation.from_json(name, ta_json, texture_animations)

		return texture_animations

	@classmethod
	def get_animation_files_in_dir(cls, dir_path):
		for root, dirs, files in os.walk(dir_path):
			for file in files:
				if os.path.splitext(file)[1] == ".yml" and file.endswith(".animation.yml"):
					yield os.path.join(root, file)
					
	@classmethod
	def load_yaml_file(cls, path):
		with open(path) as file:
			return yaml.load(file, Loader=yaml.Loader)