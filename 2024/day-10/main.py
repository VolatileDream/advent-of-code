#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.data.structures.point import Point, CARDINAL
from _.games.advent_of_code.utils import to_grid, grid_display

LOAD = "content"
def REWRITE(lines):
  return to_grid(lines, discard=".", transform=int)

def TEST(inputs):
  pass

def index(grid):
  starts = set()
  for pos, value in grid.items():
    if value == 0:
      starts.add(pos)
  return starts

def reachable(current, grid, hits):
  height = grid[current]
  if height == 9:
    hits.add(current)
    return hits

  paths = 0
  for direction in CARDINAL:
    # Is it a place we can go?
    pos = current + direction
    if pos in grid and grid[pos] == height + 1:
      reachable(pos, grid, hits)

  return hits


def count_paths(current, grid, cache):
  height = grid[current]
  if height == 9:
    assert(current in cache)
    assert(cache[current] == 1)
    return 1

  if current in cache:
    return cache[current]

  paths = 0
  for direction in CARDINAL:
    # Is it a place we can go?
    pos = current + direction
    if pos in grid and grid[pos] == height + 1:
      paths += count_paths(pos, grid, cache)

  cache[current] = paths
  return paths

def PART1(inputs):
  #print(inputs)
  grid, size = inputs
  starts = index(grid)

  pathscache = {}
  for pos, value in grid.items():
    if value == 9:
      pathscache[pos] = 1

  count = 0
  for pos in starts:
    r = reachable(pos, grid, set())
    
    #score = count_paths(pos, grid, cache=dict(pathscache))
    #print(pos, len(r))
    count += len(r)

  # 694
  return count

def PART2(inputs):
  grid, size = inputs
  starts = index(grid)

  pathscache = {}
  for pos, value in grid.items():
    if value == 9:
      pathscache[pos] = 1

  count = 0
  for pos in starts:
    score = count_paths(pos, grid, cache=dict(pathscache))
    #print(pos, score)
    count += score

  return count
