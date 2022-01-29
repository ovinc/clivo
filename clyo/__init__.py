"""Command line interface"""

from .cli import CommandLineInterface, Property, TimeInterval

from importlib_metadata import version

__author__ = "Olivier Vincent"
__version__ = version("clyo")
