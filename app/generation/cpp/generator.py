# Copyright (C) 2025 Roberto Martin Fantini <martin.fantini@gmail.com>
# This file may be distributed under the terms of the GNU GPLv3 license

from app.generator import GeneratorBase

from jinja2 import Environment, FileSystemLoader
import pathlib
import os

class Generator(GeneratorBase):
    def __init__(self, path: str) -> None:
        self.path = path
        self.env = Environment(
            loader = FileSystemLoader(f'{pathlib.Path(__file__).parent.resolve()}/templates'),
            autoescape = False,
            trim_blocks = True,
            lstrip_blocks = True,
            keep_trailing_newline = True
        )

    def _generate_impl(self, schema: dict) -> None:
        return None