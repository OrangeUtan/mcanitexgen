from setuptools import setup

with open("README.md", "r") as file:
	long_description = file.read()

setup(
	name='mcmetagen',
	version='0.0.2',
	description='A texture animation generator for Minecraft .mcmeta files',
	long_description=long_description,
	long_description_content_type="text/markdown",
	py_modules=["mcmetagen"],
	package_dir={'': 'src'},
	classifiers=[
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"License :: OSI Approved :: MIT License"
	],
	extras_require = {
		"dev": [
			"pytest>=3.7"
		]
	}
)