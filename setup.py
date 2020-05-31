from setuptools import setup

setup(
	name='mcmetagen',
	version='0.0.1',
	description='A texture animation generator for Minecraft .mcmeta files',
	py_modules=["mcmetagen"],
	package_dir={'': 'src'},
	classifiers=[
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"License :: MIT License"
	],
	extras_require = {
		"dev": [
			"pytest>=3.7"
		]
	}
)