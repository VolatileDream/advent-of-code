#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.data.structures.point import Point
from _.games.advent_of_code.utils import read_numbers

LOAD = "content"
def REWRITE(lines):
  return lines

def TEST(inputs):

  assert list(rangedir(1, 4, DIRECTIONS["UP"])) == [1,2,3]
  assert list(rangedir(1, 4, DIRECTIONS["LEFT"])) == [1,2,3]
  assert list(rangedir(1, 4, DIRECTIONS["DOWN"])) == [3,2,1]
  assert list(rangedir(1, 4, DIRECTIONS["RIGHT"])) == [3,2,1]

  assert coord(2, 3, DIRECTIONS["UP"]) == Point(3, 2)
  assert coord(2, 3, DIRECTIONS["LEFT"]) == Point(2, 3)
  assert coord(2, 3, DIRECTIONS["DOWN"]) == Point(3, 2)
  assert coord(2, 3, DIRECTIONS["RIGHT"]) == Point(2, 3)
  pass

def load(rocks):
  maxrow, maxcol = len(rocks), len(rocks[0])
  total = 0
  for r in range(maxrow):
    c = rocks[r].count("O") * (maxrow - r)
    #print(c)
    total += c

  return total

def PART1(inputs):
  inputs = [list(l) for l in inputs]
  maxrow, maxcol = len(inputs), len(inputs[0])

  for c in range(maxcol):
    while True:
      changed = False
      for r in range(maxrow - 1):
        if inputs[r][c] == "." and inputs[r + 1][c] == "O":
          inputs[r][c] = "O"
          inputs[r + 1][c] = "."
          changed = True
      if not changed:
        break

  for l in inputs:
    #print("".join(l))
    pass

  # Attempt 1: 194150 - no.
  # Attempt 2: 108614 - after fixing math error in load.
  return load(inputs)


DIRECTIONS = {
  # Row, column - (0,0) in the top-left.
  "UP": Point(-1, 0),
  "DOWN": Point(+1, 0),
  "LEFT": Point(0, -1),
  "RIGHT": Point(0, +1)
}
AXIS = {
  "UP": "VERT",
  "DOWN": "VERT",
  "LEFT": "HORZ",
  "RIGHT": "HORZ",
}

def rangedir(lo, hi, direction):
  d = direction.x + direction.y
  assert d == 1 or d == -1
  if d < 0:
    return range(lo, hi, 1)
  return range(hi - 1, lo - 1, -1)

def coord(orth, slide, direction):
  if direction.y == 0:
    return Point(slide, orth)
  return Point(orth, slide)
  

@dataclass(unsafe_hash=True)
class RollingRocks:
  size: tuple
  rocks: dict

  def slide(self, direction):
    direction = DIRECTIONS[direction]

    cpy = RollingRocks(self.size, self.rocks)
    #print("sliding rocks:", direction)

    for orthogonal in range(1, cpy.size[0] - 1):
      for slide in rangedir(1, cpy.size[0] - 1, direction):
        p = coord(orthogonal, slide, direction)
        if cpy.rocks.get(p, ".") == "O":
          n = p
          while cpy.rocks.get(n + direction, ".") == ".":
            n = n + direction
          del cpy.rocks[p]
          cpy.rocks[n] = "O"
          #print("found rock", p, "placing", n)

    return cpy

  def load(self, direction):
    if direction != "UP":
      return NotImplemented

    # Recall there's a border of "#"!
    maxrow = self.size[0]
    total = 0
    for r in range(maxrow):
      mult = maxrow - r - 1
      for c in range(self.size[1]):
        p = Point(r, c)
        total += int(self.rocks.get(p, ".") == "O") * mult
    return total

  def __str__(self):
    b = Block()
    for row in range(self.size[0]):
      c = Block()
      for col in range(self.size[1]):
        p = Point(row, col)
        if p not in self.rocks:
          c += "."
        else:
          c += self.rocks[p]
      b |= c
    return str(b)

  @staticmethod
  def parse(lines):
    # Wrap the input in "#" to make math easier for sliding iteration.
    # Warning: this changes the load math!!
    col = len(lines[0])
    lines = (["#" * col]) + lines + (["#" * col])
    lines = ["#" + l + "#" for l in lines]

    size = (len(lines), len(lines[0]),)
    rocks = {}
    for row, line in enumerate(lines):
      for col, val in enumerate(line):
        if val == ".":
          continue
        rocks[Point(row, col)] = val
    return RollingRocks(size, rocks)


def PART2(inputs):
  # Now rotate in all directions, but do it 1000000000 times.
  #print(inputs)
  #print(load(inputs))
  rr = RollingRocks.parse(inputs)
  #rr = RollingRocks.parse("...\n.O.\n...".split("\n"))
  print(rr)
  #print(rr.size)
  #print(rr.load("UP"))
  #rs = rr.slide("UP")
  #print(rs)
  #print(rs.load("UP"))
  s = rr
  states = {}
  idx = 0
  limit = 1000000000
  while idx < limit:
    idx += 1
    for d in ("UP", "LEFT", "DOWN", "RIGHT",):
      s = s.slide(d)

    stringify = str(s)
    if stringify in states:
      start = states[stringify]
      cycleLength = idx - start
      remaining = limit - idx
      offset = remaining % cycleLength
      print("cycle", start, "->", idx, "len:", cycleLength, "offset", offset)
      # Turn off cycle detection.
      states = {}
      idx = limit - offset
      continue

    states[stringify] = idx

  # Attempt 1: 92201 - too low
  # Attempt 2: 99764 - after fixing rotation order. - too high
  # Attempt 3: 96447 - after fixing down & right sliding, and off-by-1 in cycle count.
  print(s)
  return s.load("UP")
