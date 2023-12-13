#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

import functools

@dataclass
class LogEntry:
  bits: str
  runs: list

  @staticmethod
  def parse(line):
    bits, nums = line.split(" ")
    return LogEntry(bits, [int(i) for i in nums.split(",")])


LOAD = "content"
def REWRITE(lines):
  return [LogEntry.parse(l) for l in lines]
 
def TEST(inputs):
  assert valid_opts("?", tuple()) == 1
  assert valid_opts(".", tuple()) == 1
  assert valid_opts("#", tuple()) == 0
  assert valid_opts(".", (1,)) == 0
  assert valid_opts("#", (1,)) == 1
  assert valid_opts("?", (1,)) == 1
  assert valid_opts("???", (1,)) == 3
  assert valid_opts("????", (1, 1)) == 3

  assert valid_opts(".###......##", (3,2,1)) == 0
  # examples:
  assert valid_opts("???.###", (1,1,3)) == 1
  assert valid_opts(".??..??...?##.", (1,1,3)) == 4
  assert valid_opts("?#?#?#?#?#?#?#?", (1,3,1,6)) == 1
  assert valid_opts("????.#...#...", (4,1,1)) == 1
  assert valid_opts("????.######..#####.", (1,6,5)) == 4
  assert valid_opts("?###????????", (3,2,1)) == 10


#def valid_opts(bits, runs, **kwargs):
#  return valid_opts(bits, tuple(runs))

def PART1(inputs):
  s = 0
  for entry in inputs:
    opts = valid_opts(entry.bits, tuple(entry.runs))
    #print(entry, opts)
    s += opts

  print("cache", valid_opts.cache_info())
  return s


# This is the fast implementation...
# The other implementation I made was too clever and implemented
# caching incorrectly, and was therefore slow. :(
@functools.cache
def valid_opts(bits, runs, need_dot=False):
  if len(bits) == 0:
    return int(len(runs) == 0)

  if len(runs) == 0:
    if "#" in bits:
      return 0
    return 1

  if bits[0] == ".":
    return valid_opts(bits[1:], runs)

  if bits[0] == "#" and need_dot:
    # bad format.
    return 0

  if bits[0] == "#":
    if not runs:
      return 0
    next_run, runs = runs[0], tuple(runs[1:])
    if len(bits) < next_run or "." in bits[:next_run]:
      return 0
    return valid_opts(bits[next_run:], runs, True)

  assert bits[0] == "?"

  if need_dot:
    return valid_opts("." + bits[1:], runs)

  return valid_opts("#" + bits[1:], runs) + valid_opts("." + bits[1:], runs)


def PART2(inputs):
  s = 0
  for entry in inputs:
    bits, runs = entry.bits, entry.runs
    bits = "?".join([bits] * 5)
    runs = runs * 5
    opts = valid_opts(bits, tuple(runs))
    #print(entry, "*5", opts)
    s += opts

  print("cache", valid_opts.cache_info())
  # Attempt 1: 61545797684239268183 too high
  # Attempt 2: 4968620679637 - Yes! 79m after i started running my p1 solution...
  return s
