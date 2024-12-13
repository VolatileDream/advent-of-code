#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

import math

LOAD = "content"
def REWRITE(lines):
  return read_numbers(lines[0])
  return [int(l) for l in lines[0]]

def TEST(inputs):
  pass

def digits(num):
  return int(math.ceil(math.log10(num + 1)))

def explode_rock(rock, cycles, cache):
  key = (rock, cycles)
  if key in cache:
    return cache[key]

  if not cycles:
    cache[key] = 1
    return 1

  val = 0
  cycles -= 1
  if rock == 0:
    val += explode_rock(1, cycles, cache)
  elif (d := digits(rock)) % 2 == 0:
    splitter = math.pow(10, d / 2)
    r1, r2 = divmod(rock, splitter)
    val += explode_rock(r1, cycles, cache)
    val += explode_rock(r2, cycles, cache)
  else:
    val += explode_rock(rock * 2024, cycles, cache)

  cache[key] = val
  return val


def PART1(inputs):
  print(inputs)

  count = 0
  statecache = {}
  for rock in inputs:
    count += explode_rock(rock, 25, statecache)
  print(len(statecache))
  return count

def PART2(inputs):
  count = 0
  statecache = {}
  for rock in inputs:
    count += explode_rock(rock, 75, statecache)
  print(len(statecache))
  return count
