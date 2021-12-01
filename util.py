#!/usr/bin/env python-mr

import collections
import re
import sys
import typing

from _.command_line.app import APP
from _.command_line.flags import Flag

FLAG_input = Flag.str("input", short="i", default="/dev/stdin", description="Puzzle input file.")


def load_input(filename=None):
  if not filename:
    filename = FLAG_input.value

  contents = []
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip() # remove trailing newline
      contents.append(line)

  return contents


def load_groups(filename=None):
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


