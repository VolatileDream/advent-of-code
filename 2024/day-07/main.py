#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from itertools import repeat, product
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

import math

LOAD = "content"
def REWRITE(lines):
  result = []
  for l in lines:
    target, nums = l.split(": ")
    result.append((int(target), tuple([int(n) for n in nums.split(" ")]),))
  return result

def TEST(inputs):
  print(concatenate(15, 6))
  assert(156 == concatenate(15, 6))
  pass

def all_combos(iterable, length):
  return product(iterable, repeat=length)

def concatenate(x, y):
  # This is the fastest way to do this.
  # Faster than the string operations, and faster than log. :(
  if y < 10:
    return x * 10 + y
  if y < 100:
    return x * 100 + y
  if y < 1000:
    return x * 1000 + y

  #return int(f"{x}{y}")
  # +1 because ceil(log10(100)) == 2, ceil(log10(101)) == 3
  digits = math.ceil(math.log10(y + 1))
  return int(x * math.pow(10, digits)) + y

OPERATORS = [
  lambda x, y: x + y,
  lambda x, y: x * y,
  concatenate,
]

def domath(target, nums, operations):
  ops = len(nums) - 1
  count = 0
  for combination in all_combos(operations, ops):
    start = nums[0]
    for op, n in zip(combination, nums[1:]):
      start = OPERATORS[op](start, n)
      # optimization.
      if start > target:
        break

    if start == target:
      #print(target, start, nums, combination)
      count += 1
      # we're not counting how many today, just if.
      return 1

  return 0

def PART1(inputs):
  print(inputs)

  count = 0
  for target, nums in inputs:
    if domath(target, nums, [0, 1]) > 0:
      count += target

  # Attempt 1: 3044488433868 - too low / bad combo generation
  # Attempt 2: 4555081946288
  return count

def PART2(inputs):
  count = 0
  for target, nums in inputs:
    if domath(target, nums, [0,1,2]) > 0:
      count += target

  # 227921760109726
  return count
