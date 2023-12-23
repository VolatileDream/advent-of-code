#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.data.structures.point import Point
from _.games.advent_of_code.utils import read_numbers

DIRECTIONS = {
  # Row, column - (0,0) in the top-left.
  "^": Point(-1, 0),
  "v": Point(+1, 0),
  "<": Point(0, -1),
  ">": Point(0, +1),
}

def grid_rock(grid, pos):
  return grid.get(pos, ".") == "#"

LOAD = "content"
def REWRITE(lines):
  grid = {}
  size = (len(lines), len(lines[0]))
  for row, l in enumerate(lines):
    for col, value in enumerate(l):
      p = Point(row, col)
      grid[p] = value

  # Stopper the start & stop
  grid[Point(-1, 1)] = "#"
  grid[Point(size[0], size[1] - 2)] = "#"
  return (size, grid)

def TEST(inputs):
  pass

def adjacent(grid, pos):
  items = []
  for d in DIRECTIONS.values():
    n = pos + d
    if not grid_rock(grid, n):
      items.append(n)
  return items

def dfs(grid, node, end, seen):
  if node == end:
    return 0

  assert node not in seen, f"found {node} in {seen}"
  seen.add(node)

  options = None
  if grid[node] == ".":
    options = adjacent(grid, node)
  else:
    n = node + DIRECTIONS[grid[node]]
    options = [n]

  mPath = 0
  for o in options:
    if o in seen:
      continue
    mPath = max(mPath, dfs(grid, o, end, seen))

  seen.remove(node)
  return mPath + 1


def PART1(inputs):
  size, grid = inputs

  start = Point(0, 1)
  end = Point(size[0] - 1, size[1] - 2)

  import sys
  sys.setrecursionlimit(1000 + size[0] * size[1])
  return dfs(grid, start, end, set())

def segment_compress(grid):
  # Collapse long runs of single options into a larger weight.

  # Point -> Point -> cost
  costed = defaultdict(dict)

  for pos in grid:
    if grid_rock(grid, pos):
      continue
    for n in adjacent(grid, pos):
      costed[pos][n] = 1

  for node, neighbours in costed.items():
    for n in neighbours:
      assert costed[n][node] == 1
      assert costed[node][n] == 1

  #print(costed)

  process = set(costed.keys())
  while process:
    # Pick a random point in the grid we haven't seen.
    # It's in a segment if it only has 2 neighbours.
    # The segment ends when one of the ends has more than two neighbours.
    node = process.pop()

    neighbours = costed[node]
    if len(neighbours) != 2:
      continue
    #print("rm", node, grid[node], neighbours)
    #print(">", list(adjacent(grid, node)))

    n1, n2 = neighbours
    #print(n1, costed[n1])
    #print(n2, costed[n2])
    costed[n1][n2] = costed[n1][node] + costed[node][n2]
    costed[n2][n1] = costed[n2][node] + costed[node][n1]
    del costed[n1][node]
    del costed[n2][node]
    del costed[node]

  for node in costed:
    for n in costed[node]:
      assert costed[n][node] == costed[node][n]

  #print(costed)
  return costed


def bfs(compressed, start, end):
  # BFS won't work because of the cycles in the graph.
  seen = set()
  process = [start]
  processing = set(process)

  distances = {}
  distances[start] = 0

  while process:
    print([(p, distances[p]) for p in process])
    node = process.pop(0)
    processing.remove(node)
    seen.add(node)

    if node == end:
      return distances[end]

    options = set(compressed[node].keys())
    sort = False
    for o in options:
      if o in seen:
        continue
      travel_cost = distances[node] + compressed[node][o]
      distances[o] = max(distances.get(o, 0), travel_cost)
      if o not in processing:
        processing.add(o)
        process.append(o)
        sort = True
    if sort:
      process.sort(key=lambda n: distances[n], reverse=True)

def compress_dfs(compressed, node, end, seen):
  if node == end:
    return 0

  assert node not in seen, f"found {node} in {seen}"
  seen.add(node)

  mPath = 0
  for o in compressed[node]:
    if o in seen:
      continue
    mPath = max(mPath, compressed[node][o] + compress_dfs(compressed, o, end, seen))

  seen.remove(node)
  return mPath

def PART2(inputs):
  size, grid = inputs

  start = Point(0, 1)
  end = Point(size[0] - 1, size[1] - 2)

  compressed = segment_compress(grid)
  print("decision points:", len(compressed))
  #print(dfs(grid, start, list(compressed[start])[0], set()))
  #print(compressed[start])
  #print(dfs(grid, end, list(compressed[end])[0], set()))
  #print(compressed[end])
  for c in compressed:
    print(c, compressed[c])

  # Attempt 1: 2946 - too low
  # Switch to exhaustive depth first search.
  # Attempt 2: 6921 - too high
  # Oh, w
  #return bfs(compressed, start, end)
  return compress_dfs(compressed, start, end, set())
