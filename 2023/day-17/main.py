#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from functools import cache
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.data.structures.point import Point
from _.games.advent_of_code.utils import read_numbers

import math
import sys


@dataclass(unsafe_hash=True, frozen=True)
class StrDict:
  size: tuple
  content: str

  @staticmethod
  def parse(lines):
    # newline for printing
    c = "\n".join(lines)
    return StrDict((len(lines), len(lines[0])), c)

  def __contains__(self, val):
    assert type(val) == Point
    if val.x < 0 or val.y < 0:
      return False
    if val.x >= self.size[0] or val.y >= self.size[0]:
      return False
    return True

  def __getitem__(self, val):
    if val not in self:
      raise KeyError
    return self.content[val.x * (1 + self.size[0]) + val.y]

  def __str__(self):
    return self.content

LOAD = "content"
def REWRITE(lines):
  return StrDict.parse(lines)

DIRECTIONS = {
  # Row, column - (0,0) in the top-left.
  "UP": Point(-1, 0),
  "DOWN": Point(+1, 0),
  "LEFT": Point(0, -1),
  "RIGHT": Point(0, +1)
}

# Had to go to r/aoc for this, but they
# suggested removing the "moves count" and
# making items "adjacent" up to 3 moves away!
#
# This means that at any point in the graph, our
# only choice is to turn, and never go straight!
def moves(grid, pos, curdir):
  assert curdir.x == 0 or curdir.y == 0
  # use two ifs to ensure Point(0, 0) works.
  if curdir.x == 0:
    cost = 0
    for n in range(1, 4):
      npos = pos + Point(n, 0)
      cost += gridcost(grid, npos)
      yield (cost, npos, Point(1, 0))
    cost = 0
    for n in range(1, 4):
      npos = pos + Point(-n, 0)
      cost += gridcost(grid, npos)
      yield (cost, npos, Point(-1, 0))
  if curdir.y == 0:
    cost = 0
    for n in range(1, 4):
      npos = pos + Point(0, n)
      cost += gridcost(grid, npos)
      yield (cost, npos, Point(0, 1))
    cost = 0
    for n in range(1, 4):
      npos = pos + Point(0, -n)
      cost += gridcost(grid, npos)
      yield (cost, npos, Point(0, -1))

def TEST(inputs):
  pass

# Cache str -> int...
@cache
def gridcost(grid, pos):
  if pos not in grid:
    return grid.size[0] * grid.size[1] * 1000
  return int(grid[pos])

def bfs(grid, movefn):
  cache = dict()
  end = Point(grid.size[0] - 1, grid.size[1] - 1)

  # all (point, dir) -> thing
  lowestcost = {}
  seen = set()
  # these mirror each other to avoid duplicates.
  processing = set()
  process = list()

  start = (Point(0, 0), Point(0, 0))
  lowestcost[start] = 0
  process.append(start)
  processing.add(start)

  while process:
    n = process.pop(0)
    processing.remove(n)
    assert n not in seen
    seen.add(n)

    #print(n)

    p, curdir = n
    herecost = lowestcost[n]

    options = list(movefn(grid, p, curdir))
    options.sort(key=lambda x: x[0])
    sort = False
    for movecost, endpos, direction in options:
      if endpos not in grid:
        continue
      key = (endpos, direction)
      if key not in lowestcost or lowestcost[key] > herecost + movecost:
        lowestcost[key] = herecost + movecost
        #print(n, key, lowestcost[key])
        sort = True
      if key not in seen and key not in processing:
        sort = True
        processing.add(key)
        process.append(key)

    if sort:
      process.sort(key = lambda k: lowestcost[k])
      #print(process)


  #print(lowestcost)
  return min(lowestcost[(end, Point(1, 0))], lowestcost[(end, Point(0, 1))])


def PART1(inputs):
  grid = inputs
  return bfs(grid, moves)

def move_ultracrucible(grid, pos, curdir):
  assert curdir.x == 0 or curdir.y == 0
  # use two ifs to ensure Point(0, 0) works.
  if curdir.x == 0:
    cost = 0
    for n in range(1, 4):
      npos = pos + Point(n, 0)
      cost += gridcost(grid, npos)
    for n in range(4, 11):
      npos = pos + Point(n, 0)
      cost += gridcost(grid, npos)
      yield (cost, npos, Point(1, 0))
    cost = 0
    for n in range(1, 4):
      npos = pos + Point(-n, 0)
      cost += gridcost(grid, npos)
    for n in range(4, 11):
      npos = pos + Point(-n, 0)
      cost += gridcost(grid, npos)
      yield (cost, npos, Point(-1, 0))
  if curdir.y == 0:
    cost = 0
    for n in range(1, 4):
      npos = pos + Point(0, n)
      cost += gridcost(grid, npos)
    for n in range(4, 11):
      npos = pos + Point(0, n)
      cost += gridcost(grid, npos)
      yield (cost, npos, Point(0, 1))
    cost = 0
    for n in range(1, 4):
      npos = pos + Point(0, -n)
      cost += gridcost(grid, npos)
    for n in range(4, 11):
      npos = pos + Point(0, -n)
      cost += gridcost(grid, npos)
      yield (cost, npos, Point(0, -1))

def PART2(inputs):
  grid = inputs
  # Attempt 1: 270 - too low
  # fixed costs in move_ultracrucible
  # Attempt 2: 993
  return bfs(grid, move_ultracrucible)
