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


def validate(bits, runs):
  #print("validate", bits, runs)
  rbits, rruns = check_seq(bits, runs)
  #print(">", rbits, rruns)
  if rbits is None:
    return False
  if len(rruns) == 0:
    rruns = (0,)
  return len(rruns) == 1 and len(rbits) == rruns[0]


def check_seq(bits, runs):
  #print("check_seq", bits, runs)
  runs = list(runs)
  idx = 0
  while idx < len(bits):
    count = 0
    while idx < len(bits) and bits[idx] == ".":
      idx += 1
      count += 1

    #print(".", count)

    if idx >= len(bits):
      break

    count = 0
    while idx < len(bits) and bits[idx] == "#":
      idx += 1
      count += 1

    #print("#", count)

    if len(runs) and count > runs[0]:
      return (None, None)

    if idx >= len(bits) or bits[idx] == "?":
      # Return the last group, because runs could be longer than it.
      return (bits[idx-count:], runs)

    # bits[idx] == . so keep matching.
    if len(runs) == 0 or runs.pop(0) != count:
      # Fails to validate.
      return (None, None)

  return (bits[idx:], runs)

def valid_opts(bits, runs, memo=None, agg=""):
  r = valid_opts2(bits, runs, memo, agg)
  if "?" not in bits:
    #print("valid_opts", agg + bits, runs, ">", r)
    pass
  return r

# I think this tried to be clever, and resulted in lots of cache misses.
def valid_opts2(bits, runs, memo=None, agg=""):
  state = (bits, tuple(runs))
  if memo is None:
    memo = defaultdict(int)
  if state in memo:
    memo["_hit"] += 1
    return memo[state]
  memo["_miss"] += 1

  if "?" not in bits:
    r = int(validate(bits, runs))
    memo[state] = r
    return r

  # Some combo of {#, ?, .} and runs.

  # prefix holds constant.
  rbits, rruns = check_seq(bits, runs)

  if rbits is None:
    memo[state] = 0
    return 0

  if not rruns:
    if "#" in rbits:
      memo[state] = 0
      return 0 # not valid.
    memo[state] = 1
    return 1 # all ? = .

  if not rbits:
    memo[state] = int(len(rruns) == 0)
    return memo[state]

  # rbits contains some number of # and at least 1 ?

  agg = agg + bits[:len(bits) - len(rbits)]

  o1 = rbits.replace("?", ".", 1)
  o2 = rbits.replace("?", "#", 1)
  r = valid_opts(o1, rruns, memo, agg) + valid_opts(o2, rruns, memo, agg)
  memo[state] = r
  return r

 
def TEST(inputs):
  assert validate("#", [1])
  assert validate("..#..", [1])
  assert not validate(".", [1])

  assert check_seq("#", [1]) == ("#", [1])
  assert check_seq(".", [1]) == ("", [1])
  assert check_seq("..#..", [1]) == ("", [])
  assert check_seq("?", [1]) == ("?", [1])
  assert check_seq(".", [1]) == ("", [1])
  assert check_seq("..##?..", [1]) == (None, None)
  assert check_seq("..##?..", [3]) == ("##?..", [3])

  assert valid_opts("?", []) == 1
  assert valid_opts(".", []) == 1
  assert valid_opts("#", []) == 0
  assert valid_opts(".", [1]) == 0
  assert valid_opts("#", [1]) == 1
  assert valid_opts("?", [1]) == 1
  assert valid_opts("???", [1]) == 3
  opts = valid_opts("????", [1, 1])
  assert valid_opts("????", [1, 1]) == 3, f"{opts} == 3"

  assert valid_opts(".###......##", [3,2,1]) == 0
  # examples:
  assert valid_opts("???.###", [1,1,3]) == 1
  assert valid_opts(".??..??...?##.", [1,1,3]) == 4
  assert valid_opts("?#?#?#?#?#?#?#?", [1,3,1,6]) == 1
  assert valid_opts("????.#...#...", [4,1,1]) == 1
  assert valid_opts("????.######..#####.", [1,6,5]) == 4
  opts = valid_opts("?###????????", [3,2,1])
  assert valid_opts("?###????????", [3,2,1]) == 10, f"{opts} == 10"


#def valid_opts(bits, runs, **kwargs):
#  return p2(bits, tuple(runs))

def PART1(inputs):
  s = 0
  m = defaultdict(int)
  for entry in inputs:
    opts = valid_opts(entry.bits, entry.runs, m)
    print(entry, opts)
    s += opts

  hit, miss = m["_hit"], m["_miss"]
  print("cache", "hit", hit, "miss", miss, "=", hit / (hit + miss), "size", len(m))

  return s


# This is the fast implementation...
# The other one is too clever and slow... :(
@functools.cache
def p2(bits, runs, need_dot=False):
  if len(bits) == 0:
    return int(len(runs) == 0)

  if len(runs) == 0:
    if "#" in bits:
      return 0
    return 1

  if bits[0] == ".":
    return p2(bits[1:], runs)

  if bits[0] == "#" and need_dot:
    # bad format.
    return 0

  if bits[0] == "#":
    if not runs:
      return 0
    next_run, runs = runs[0], tuple(runs[1:])
    if len(bits) < next_run or "." in bits[:next_run]:
      return 0
    return p2(bits[next_run:], runs, True)

  assert bits[0] == "?"

  if need_dot:
    return p2("." + bits[1:], runs)

  return p2("#" + bits[1:], runs) + p2("." + bits[1:], runs)


def PART2(inputs):
  s = 0
  for entry in inputs:
    bits, runs = entry.bits, entry.runs
    bits = "?".join([bits] * 5)
    runs = runs * 5
    opts = p2(bits, tuple(runs))
    #print(entry, "*5", opts)
    s += opts

  print("cache", p2.cache_info())
  # Attempt 1: 61545797684239268183 too high
  # Attempt 2: 4968620679637 - Yes! 79m after i started running my p1 solution...
  return s
