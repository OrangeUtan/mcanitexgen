import argparse, sys
from mcanitexgen.Parser import Parser

parser = argparse.ArgumentParser(description='Generates .mcmeta files from .animation.yml files')
parser.add_argument('dir', type=str, nargs='?', default='.', help='Directory in where to search for animation files')
args = parser.parse_args(sys.argv[1:])

Parser.generate_animations(args.dir)