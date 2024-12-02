#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

LOAD = "content"
def REWRITE(lines):
  return [read_numbers(l) for l in lines]

def TEST(inputs):
  pass

def sign(n):
  if n < 0:
    return -1
  elif n > 0:
    return 1
  else:
    return 0

def check(nums):
  s = sign(nums[0])
  for n in nums:
    if sign(n) != s:
      return False
    if not (1 <= abs(n) <= 3):
      return False
  return True

def PART1(inputs):
  # Let's be fancy!

  count = 0
  for levels in inputs:
    # convert to deltas.
    deltas = [a - b for (a, b) in zip(levels, levels[1:])]
    if check(deltas):
      count += 1
  return count

def PART2(inputs):
  unsafe = []
  count = 0
  for levels in inputs:
    # convert to deltas.
    deltas = [a - b for (a, b) in zip(levels, levels[1:])]
    if check(deltas):
      count += 1
    else:
      unsafe.append(levels)

  for levels in unsafe:
    for i in range(len(levels)):
      smaller = levels[0:i] + levels[i+1:]
      deltas = [a - b for (a, b) in zip(smaller, smaller[1:])]
      if check(deltas):
        count += 1
        break

  return count
