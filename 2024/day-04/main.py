#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.data.structures.point import Point, EIGHTWAY
from _.games.advent_of_code.utils import read_numbers



LOAD = "content"
def REWRITE(lines):
  grid = defaultdict(lambda: ".")
  for y, line in enumerate(lines):
    for x, c in enumerate(line):
      grid[Point(x,y)] = c

  return grid

def TEST(inputs):
  pass

def search(grid, start, string):
  assert(grid[start] == string[0])

  # tuple(start, end)
  found = []

  for direction in EIGHTWAY:
    index = 1
    pos = start + direction
    while index < len(string) and grid[pos] == string[index]:
      index += 1
      pos += direction

    if index == len(string):
      found.append((start, pos - direction))

  return found

def PART1(inputs):
  print(inputs)
  xs = set()
  for key, value in inputs.items():
    if value == "X":
      xs.add(key)

  print(xs)
  count = 0
  for x in xs:
    f = search(inputs, x, "XMAS")
    count += len(f)

  # 2524
  return count

def isMAS(grid, p1, p2):
  l1, l2 = grid[p1], grid[p2]
  return l1 != l2 and l1 in "MS" and l2 in "MS"

def checkMAS(grid, start):
  assert(grid[start] == "A")

  # We assume only one of cross or plus can match.
  up = Point(0, 1)
  right = Point(1, 0)
  plus = isMAS(grid, start + up, start - up) and isMAS(grid, start + right, start - right)

  tr = up + right
  tl = up - right
  cross = isMAS(grid, start + tr, start - tr) and isMAS(grid, start + tl, start - tl)

  # ooooooh, this does not pass!
  #assert(not(plus and cross))

  # Oops, didn't need the plus check...
  return int(cross)


def PART2(grid):
  aaah = set()
  for key, value in grid.items():
    if value == "A":
      aaah.add(key)
 
  count = 0
  for a in aaah:
    count += checkMAS(grid, a)

  # attempt 1: 1904
  # attempt 2: 1873
  return count
  pass
