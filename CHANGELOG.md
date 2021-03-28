# Changelog

<!--next-version-placeholder-->

## v1.1.0 (2021-03-28)
### Feature
* Replace --no-indent flag with --minify and --indent ([`39d38ce`](https://github.com/OrangeUtan/mcanitexgen/commit/39d38ce693a832382ec776d5c1a437a4f0035128))
* Change out argument to --out option ([`6ed63ec`](https://github.com/OrangeUtan/mcanitexgen/commit/6ed63ec786422babf17b3d5f271019324eed3735))
* Add --dry flag ([`2c5310f`](https://github.com/OrangeUtan/mcanitexgen/commit/2c5310fcc4f7ce4c98dcad20259c600b3967eb66))

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
