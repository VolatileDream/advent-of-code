#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.data.structures.point import Point
from _.games.advent_of_code.utils import read_numbers

LOAD = "content"
def REWRITE(lines):
  start = None
  grid = {}
  for y, line in enumerate(lines):
    for x, c in enumerate(line):
      if c == ".":
        continue
      elif c == "^":
        start = Point(x,y)
      else:
        grid[Point(x,y)] = "#"

  return (start, grid, len(lines))

def TEST(inputs):
  pass


def display(grid, visit, size):
  lines = []
  for y in range(size):
    line = ""
    for x in range(size):
      p = Point(x, y)
      if p in visit:
        line += "X"
      else:
        line += grid.get(p, ".")
    lines.append(line)
  return "\n".join(lines)


FACING = [
  Point(0, -1),
  Point(1, 0),
  Point(0, 1),
  Point(-1, 0),
]

def rotate(direction):
  return (direction + 1) % len(FACING)

def outside(pos, size):
  return pos.x < 0 or pos.y < 0 or pos.x >= size or pos.y >= size

def cycle(grid, pos, size):
  # Index into facing.
  direction = 0
  been = set()
  visit = set()
  while not outside(pos, size) and (pos, direction) not in been:
    been.add((pos, direction,))
    visit.add(pos)
    npos = pos + FACING[direction]
    while npos in grid:
      direction = rotate(direction)
      npos = pos + FACING[direction]

    pos = npos

  return (not outside(pos, size) and (pos, direction,) in been, visit)


def PART1(inputs):
  #print(inputs)
  pos, grid, size = inputs

  # Index into facing.
  direction = 0
  visit = set()
  while not outside(pos, size):
    visit.add(pos)
    npos = pos + FACING[direction]
    while npos in grid:
      direction = rotate(direction)
      npos = pos + FACING[direction]

    pos = npos

  print(display(grid, visit, size))
  # 4602
  return len(visit)

def PART2(inputs):
  # Limit from part 1: 4602
  start, grid, size = inputs

  # It's not possible for the guard to intersect the spaces that they wouldn't otherwise visit.
  pos = start
  direction = 0
  visit = set()
  while not outside(pos, size):
    visit.add(pos)
    npos = pos + FACING[direction]
    while npos in grid:
      direction = rotate(direction)
      npos = pos + FACING[direction]
    pos = npos

  visit.remove(start)

  count = 0
  while visit:
    attempt = visit.pop()
    grid[attempt] = "O"
    c, seen = cycle(grid, start, size)
    if c:
      count += 1
      #print(display(grid, seen, size), "\n")
    del grid[attempt]

  # Attempt 1: 1704
  # Attempt 2: 1703 - lol forgot to remove the start as a spot to obstacle.
  return count

