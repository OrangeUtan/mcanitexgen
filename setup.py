from setuptools import setup

with open("README.md", "r") as file:
	long_description = file.read()

setup(
	name='mcanitexgen',
	version='0.0.4',
	author='OrangeUtan',
	author_email='oran9eutan@gmail.com',
	description='A texture animation generator for Minecraft .mcmeta files',
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/OrangeUtan/mcanitexgen",
	py_modules=["mcanitexgen"],
	package_dir={'': 'src'},
	classifiers=[
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.6",
		"Programming Language :: Python :: 3.7",
		"License :: OSI Approved :: MIT License"
	],
	install_requires=[
		'ruamel.yaml>=0.16.10'
	],
	extras_require = {
		"dev": [
			"pytest>=3.7"
		]
	}
)