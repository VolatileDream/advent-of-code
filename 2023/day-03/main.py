#!/usr/bin/env python-mr

from collections import defaultdict
from typing import NamedTuple
from _.data.formatting.blocks import Block

import re

LOAD = "content"
def REWRITE(lines):
  return lines

def check(row, column, val, lines, fn):
  length = len(val)
  linelen = len(lines[0])

  for x in range(max(0, row - 1), min(row + 2, len(lines))):
    # :( i did an off-by-one here earlier.
    for y in range(max(0, column - 1), min(column + length + 1, linelen)):
      if fn(lines[x][y]):
        return True

  return False


def PART1(inputs):
  digits = re.compile("\d+")

  s = 0
  for idx, line in enumerate(inputs):
    matches = []
    for d in digits.finditer(line):
      pos = d.start()
      num = d.group()

      m = check(idx, pos, num, inputs, lambda x: x not in "0123456789 .")
      if m:
        matches.append(num)
        #print(num)
        s += int(num)
        #line = line.replace(num, "\033[31m" + num + "\033[39;49m")
        #line = line[:pos] + " " * len(num) + line[pos+len(num):]
        #print("match", idx, pos, num)
        pass
      else:
        #print("no", idx, pos, num)
        #line = line[:pos] + " " * len(num) + line[pos+len(num):]
        pass
    print(line, matches)

  return s

def adj_num(row, col, nums):
  # Since numbers have ids, it makes it easy to find the unique numbers adjacent
  # to any symbol. If we didn't have ids, we could never tell if two values were
  # the same number, or two numbers. :(
  numbers = set()
  for r in range(row - 1, row + 2):
    for c in range(col - 1, col + 2):
      if (r, c) in nums:
        numbers.add(nums[(r, c)])

  return [num for (num, i) in numbers]

def PART2(inputs):
  # For part two we search symbol -> numbers instead of number -> symbol.

  # Indexes (row, col) -> thing
  nums = {} # (row, col) -> (number, id)
  syms = {}

  c = 0

  digits = re.compile("\d+")
  symbols = re.compile("[^0-9 .]")
  for row, line in enumerate(inputs):
    for d in digits.finditer(line):
      c += 1
      start = d.start()
      num = int(d.group())
      l = len(d.group())

      for y in range(start, start + l):
        nums[(row,y)] = (num, c)

    for s in symbols.finditer(line):
      y = s.start()
      syms[(row, y)] = s.group()

  #print(nums)
  #print(syms)

  s = 0
  for (row, col), val in syms.items():
    if val != "*":
      continue

    # find adjacent numbers.
    adj = adj_num(row, col, nums)
    if len(adj) != 2:
      continue

    s += adj[0] * adj[1]

  return s
