# Changelog

## [Unreleased]

## [1.0.3] - 2021-03-16
### Added
- Package can now be executed as a script (i.e. `mcanitexgen` instead of `python -m mcanitexgen`)
- Automatic version bumping using [tbump](https://github.com/TankerHQ/tbump)
- Added `--version` option to CLI
- Added arguments `test` and `bump` tasks

### Changed
- Better argument parsing/checking for subcommands

## [1.0.2] - 2021-03-14
### Added
- Consecutive frames with the same index are combined
### Fixed
- Frames in gifs only rendered the part that changed from last frame

## [1.0.1] - 2021-03-14
### Added
- Added `--no-indent` flag to `generate` subcommand
### Changed
- Coverage only executed if tests pass
### Fixed
- Background in gifs properly resets with each frame

## [1.0.0] - 2021-03-13
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

## [0.0.9] - 2020-06-10
### Added
- Renamed project from **mcmetagen** to **mcanitexgen**
- PyPi Package
- Added argparse CLI that parses file and generates .mcmeta files

## [0.0.2] - 2020-06-09
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
