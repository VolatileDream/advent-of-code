#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.data.structures.point import Point
from _.games.advent_of_code.utils import read_numbers

LOAD = "content"
def REWRITE(lines):
  grid = {}
  for row, l in enumerate(lines):
    for col, c in enumerate(l):
      p = Point(row, col)
      grid[p] = c

  return ((len(lines), len(lines[0]),), grid)

def TEST(inputs):
  assert list(beamsplit("-", DIRECTIONS["RIGHT"])) == [DIRECTIONS["RIGHT"]]
  assert list(beamsplit("-", DIRECTIONS["LEFT"])) == [DIRECTIONS["LEFT"]]
  assert list(beamsplit("-", DIRECTIONS["UP"])) == [DIRECTIONS["LEFT"], DIRECTIONS["RIGHT"]]
  assert list(beamsplit("-", DIRECTIONS["DOWN"])) == [DIRECTIONS["LEFT"], DIRECTIONS["RIGHT"]]
  assert list(beamsplit("|", DIRECTIONS["UP"])) == [DIRECTIONS["UP"]]
  assert list(beamsplit("|", DIRECTIONS["DOWN"])) == [DIRECTIONS["DOWN"]]
  assert list(beamsplit("|", DIRECTIONS["LEFT"])) == [DIRECTIONS["UP"], DIRECTIONS["DOWN"]]
  assert list(beamsplit("|", DIRECTIONS["RIGHT"])) == [DIRECTIONS["UP"], DIRECTIONS["DOWN"]]

  assert MIRRORS["/"](DIRECTIONS["UP"]) == DIRECTIONS["RIGHT"]
  assert MIRRORS["/"](DIRECTIONS["RIGHT"]) == DIRECTIONS["UP"]
  assert MIRRORS["/"](DIRECTIONS["LEFT"]) == DIRECTIONS["DOWN"]
  assert MIRRORS["/"](DIRECTIONS["DOWN"]) == DIRECTIONS["LEFT"]

DIRECTIONS = {
  # Row, column - (0,0) in the top-left.
  "UP": Point(-1, 0),
  "DOWN": Point(+1, 0),
  "LEFT": Point(0, -1),
  "RIGHT": Point(0, +1),
}

MIRRORS = {
  "/": lambda p: Point(-p.y, -p.x),
  "\\": lambda p: Point(p.y, p.x),
}
def beamsplit(cell, direction):
  if cell == "-" and direction in (DIRECTIONS["LEFT"], DIRECTIONS["RIGHT"],):
    yield direction
  elif cell == "-":
    yield DIRECTIONS["LEFT"]
    yield DIRECTIONS["RIGHT"]
  elif cell == "|" and direction in (DIRECTIONS["UP"], DIRECTIONS["DOWN"],):
    yield direction
  elif cell == "|":
    yield DIRECTIONS["UP"]
    yield DIRECTIONS["DOWN"]
  

def beamtrace(grid, startp, startd):
  seen = set()
  states = set()
  process = set()
  process.add((startp, startd,))
  while len(process):
    point, direction = process.pop()
    if (point, direction) in states:
      continue
    states.add((point, direction))
    #print("processing", point, direction)

    while True:
      point = point + direction
      if grid.get(point, "#") != ".":
        break
      #print(" ", point)
      seen.add(point)

    cell = grid.get(point, "#")
    #print("interesting:", point, cell)
    if cell == "#":
      continue

    seen.add(point)
    # Process the interesting thing.
    if cell in ("\\", "/",):
      process.add((point, MIRRORS[cell](direction)))
    elif cell in ("-", "|",):
      for d in beamsplit(cell, direction):
        #print("adds", point, d)
        process.add((point, d))

    assert cell != "."

  return (seen, states)

def PART1(inputs):
  size, grid = inputs
  seen, _ = beamtrace(grid, Point(0, -1), DIRECTIONS["RIGHT"])
  print(seen)
  # Attempt 1: 7496 - yes.
  return len(seen)

def PART2(inputs):
  (maxrow, maxcol), grid = inputs

  # Do part 1, but a lot.
  energies = defaultdict(list)
  for row in range(maxrow):
    seen, _ = beamtrace(grid, Point(row, -1), DIRECTIONS["RIGHT"])
    energies[len(seen)].append(Point(row, 0))

    seen, _ = beamtrace(grid, Point(row, maxcol), DIRECTIONS["LEFT"])
    energies[len(seen)].append(Point(row, maxcol - 1))

  for col in range(maxcol):
    seen, _ = beamtrace(grid, Point(-1, col), DIRECTIONS["DOWN"])
    energies[len(seen)].append(Point(row, 0))

    seen, _ = beamtrace(grid, Point(maxrow, col), DIRECTIONS["UP"])
    energies[len(seen)].append(Point(maxrow - 1, col))

  return max(energies.keys())
