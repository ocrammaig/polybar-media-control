import argparse
import sys
from typing import Callable

from colorama import Fore, init
from ruamel import yaml

init()  # colorama initialization


def open_output(file) -> Callable:
    output = open(file, mode = 'w+', encoding = 'utf-8')
    return output.write


def read_config(file) -> dict:
    with open(file, mode = 'r', encoding = 'utf-8') as f:
        dct = yaml.safe_load(file)
    if 'media' not in dct:
        print(Fore.RED + 'Required argument media not found' + Fore.RESET)
        sys.exit(1)
    return dct


def ask_config() -> dict:
    while (media := input("Select media: ")) not in []:
        print("Wrong input")


parser = argparse.ArgumentParser()
parser.add_argument(
    'output',
    type = str,
    help = "output file",
    dest = 'output'
)
parser.add_argument(
    '-c',
    '--config',
    type = str,
    help = "config file to use",
    dest = 'config'
)
args = parser.parse_args()
print("Welcome to the build script!")
if args.config is not None:
    print(f"Reading the config file {args.config}")
    CONFIG = read_config(args.config)
else:
    CONFIG = ask_config()
output = open_output(args.output)
output(f"#!{CONFIG['interpreter']}")  # interpreter path TODO

