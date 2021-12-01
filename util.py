#!/usr/bin/env python-mr

import collections
import re
import sys
import typing

from _.command_line.app import APP
from _.command_line.flags import Flag

FLAG_input = Flag.str("input", short="i", default="/dev/stdin", description="Puzzle input file.")


def load_input(filename):
  contents = []
  with open(filename, 'r') as f:
    for line in f:
      yield line.strip() # remove trailing newline


def load_groups(filename):
  # because some files follow this format instead.
  contents = []
  acc = [] 
  for line in load_file(filename):
    if line:
      acc.append(line)
    else:
      contents.append(acc)
      acc = []

  if acc:
    contents.append(acc)

  return contents


