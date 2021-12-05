#!/usr/bin/env python-mr

import collections
import inspect
import importlib
import os
import re
import sys
import typing

from _.command_line.app import APP
from _.command_line.flags import Flag
from _.repo.python.location import REPO_LOCATION

FLAG_input = Flag.str("input", short="i", description="Puzzle input file.")
FLAG_test = Flag.bool("test", description="Use test input instead of real input.")
FLAG_year = Flag.int("year", short="Y")
FLAG_day = Flag.int("day", short="D")


def load_input(filename=None):
  if not filename:
    filename = FLAG_input.value
  if not filename:
    year, day = str(FLAG_year.value), "day-{:02}".format(FLAG_day.value)
    dirname = os.path.join(REPO_LOCATION, "games", "advent-of-code", year, day)
    if FLAG_test.value:
      filename = os.path.join(dirname, "test.txt")
    else:
      filename = os.path.join(dirname, "input.txt")

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
  for line in load_input(filename):
    if line:
      acc.append(line)
    else:
      contents.append(acc)
      acc = []

  if acc:
    contents.append(acc)

  return contents


def find_module():
  year = FLAG_year.value
  day = FLAG_day.value
  return "_.games.advent_of_code.{}.day-{:02}.main".format(year, day)


class AdventRunner:
  LOAD = {
    "content": load_input,
    "groups": load_groups,
  }

  def _load(self, module):
    choice = "content"
    if hasattr(module, "LOAD"):
      choice = module.LOAD
    return AdventRunner.LOAD[choice]()

  def _rewrite(self, module):
    if hasattr(module, "REWRITE"):
      return module.REWRITE
    return lambda x: x

  def __main(self):
    module = find_module()
    m = importlib.import_module(module)

    raw = self._load(m)
    rewrite = self._rewrite(m)
    if isinstance(rewrite, list):
      assert len(raw) == len(rewrite), "Mismatch in group size & rewrites"
      data = [fn(r) for fn, r in zip(rewrite, raw)]
    else:
      data = rewrite(raw)
    
    if hasattr(m, "PART1"):
      r1 = m.PART1(data)
      print("Part 1:", r1)

    if hasattr(m, "PART2"):
      sig = inspect.signature(m.PART2)
      if len(sig.parameters) == 2:
        r2 = m.PART2(data, r1)
      else:
        r2 = m.PART2(data)
      print("Part 2:", r2)
    
  def run(self):
    APP.run(self.__main)


if __name__ == "__main__":
  ar = AdventRunner()
  ar.run()
