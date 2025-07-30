# Copyright (C) 2025 R Martin Fantini <martin.fantini@gmail.com>
# This file may be distributed under the terms of the GNU GPLv3 license

import importlib
import traceback
import sys
from argparse import ArgumentParser, SUPPRESS
from app.parser import Parser
from app.schema import *

def main() -> None:
    parser = ArgumentParser(prog='fix-converter-gen', description='FIX codec generator')
    parser.add_argument('--schema', help='path to xml schema', required=True)
    parser.add_argument('--destination', help='path to directory where codec will be written', required=True)
    parser.add_argument('--generator', help='choose generator (available: cpp, rust)', default='cpp', type=str)
    parser.add_argument('--package', help='override model name property', default='', type=str)

    args = parser.parse_args()

    try:
        module = importlib.import_module(f'app.generation.{args.generator}')
        Generator = getattr(module, 'Generator')
        schema = Parser.from_file(args.schema).get_schema()
        if len(args.package) != 0:
            schema.name = args.package
        generator = Generator(args.destination)
        generator.generate(schema)
    except Exception as e:
        sys.exit(traceback.format_exc())
        sys.exit(f'error: {e}')

if __name__ == '__main__':
    main()
