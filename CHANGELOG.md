# Changelog

<!--next-version-placeholder-->

## v1.2.3 (2021-04-07)
### Fix
* Generate .mcmeta files in correct location ([`366dad8`](https://github.com/OrangeUtan/mcanitexgen/commit/366dad8500221d6b5c9cdc92bf30607352dd1dc1))

## v1.2.2 (2021-03-29)
### Fix
* Beet plugin creating correct output path for .mcmeta files ([`ed17fa1`](https://github.com/OrangeUtan/mcanitexgen/commit/ed17fa196958665f61f274fcd63714d2ad44dcf5))

## v1.2.1 (2021-03-29)
### Fix
* Incorrect imports in beet plugin ([`e2ed77b`](https://github.com/OrangeUtan/mcanitexgen/commit/e2ed77b5b49d7b22365f751ecbfd16ba265c8677))

## v1.2.0 (2021-03-28)
### Feature
* Can now take files or directories as input ([`fbea8e7`](https://github.com/OrangeUtan/mcanitexgen/commit/fbea8e7c8dac15e9af7c86056611c610cced89e2))
* Add beet plugin integration ([`63ef8a9`](https://github.com/OrangeUtan/mcanitexgen/commit/63ef8a992f6754f9fc9c6c5aa8c47cc4a3023e95))

## v1.1.0 (2021-03-28)
### Feature
* Replace --no-indent flag with --minify and --indent ([`1a4dd2f`](https://github.com/OrangeUtan/mcanitexgen/commit/1a4dd2f2c5caf097d3545e91366d4f370f882480))
* Change out argument to --out option ([`5042cc6`](https://github.com/OrangeUtan/mcanitexgen/commit/5042cc6ac58d35f534a579d5d0e8d48417569f7e))
* Add --dry flag ([`25e892f`](https://github.com/OrangeUtan/mcanitexgen/commit/25e892f1e50d7f2797732289fa47ca2a89be12d2))

## v1.0.5 (2021-03-28)
### Fix
* Added __future__.annotations ([`59c384a`](https://github.com/OrangeUtan/mcanitexgen/commit/59c384a5ededc348c92975a0e9ae389ba97596b7))

## v1.0.4 (2021-03-26)
Switched to pyton-semantic-release

## v1.0.3 - 2021-03-16
### Added
- Package can now be executed as a script (i.e. `mcanitexgen` instead of `python -m mcanitexgen`)
- Automatic version bumping using [tbump](https://github.com/TankerHQ/tbump)
- Added `--version` option to CLI
- Added arguments `test` and `bump` tasks

### Changed
- Better argument parsing/checking for subcommands

## v1.0.2 - 2021-03-14
### Added
- Consecutive frames with the same index are combined
### Fixed
- Frames in gifs only rendered the part that changed from last frame

## v1.0.1 - 2021-03-14
### Added
- Added `--no-indent` flag to `generate` subcommand
### Changed
- Coverage only executed if tests pass
### Fixed
- Background in gifs properly resets with each frame

## v1.0.0 - 2021-03-13
### Added
- `generate` CLI subcommand that generates .mcmeta files from animation files
- `gif` CLI subcommand that generates animated gifs from animation files
- Better CLI using [typer](https://typer.tiangolo.com/)
- Project is now a [Poetry](https://python-poetry.org/) project
- Formatting: [black](https://github.com/psf/black), [isort](https://pycqa.github.io/isort/)
- Checking: [pre-commit](https://pre-commit.com/), [mypy](http://mypy-lang.org/)
- Code Coverage
- tasks .py (Makefile equivalent using [invoke](http://www.pyinvoke.org/))
- 'test' Github Action
### Changed
- Animation files are now written in Python
- Animations are classes containing states and sequences
- Order of definition now matters for animations and sequences
- States and sequences beeing objects allows for minimalistic Syntax
### Removed
- Publishing through setuptools
- YAML animation files are no longer supported

## v0.0.9 - 2020-06-10
### Added
- Renamed project from **mcmetagen** to **mcanitexgen**
- PyPi Package
- Added argparse CLI that parses file and generates .mcmeta files

## v0.0.2 - 2020-06-09
### Added
- Github Actions
- Animation files written in YAML
- States, Sequences
- Reference texture in animation file
- Constants in animation file
- 'duration', 'start', 'end', 'weight', Time marks
- 'duration', 'start' and 'end' are Expressions
- 'end' of other animations can be referenced
- Marks of other animations can be referenced
