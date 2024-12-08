#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.data.structures.point import Point
from _.games.advent_of_code.utils import read_numbers, to_grid, grid_display

import math

LOAD = "content"
def REWRITE(lines):
  grid, size = to_grid(lines, ".")

  # Index the kind of antenna to it's position
  # kind -> set
  antennas = defaultdict(set)
  for pos, kind in grid.items():
    antennas[kind].add(pos)

  return (size, grid, antennas)

def TEST(inputs):
  pass

def antinode_pos(p1, p2, candidate):
  d1 = candidate - p1
  d2 = candidate - p2
  # magnitude to compare to find the larger.
  if abs(d1.x) > abs(d2.x):
    return d1.x == 2 * d2.x and d1.y == 2 * d2.y
  return d1.x * 2 == d2.x and d1.y * 2 == d2.y

def calcantinodes(size, positions):
  def inbounds(p):
    return 0 <= p.x < size and 0 <= p.y < size
  # Copy!
  positions = set(positions)
  nodes = set()
  while len(positions) >= 2:
    first = positions.pop()

    for second in positions:
      # Much faster, only need 2 points!
      delta = first - second
      p1 = first + delta
      p2 = second - delta
      if inbounds(p1):
        nodes.add(p1)
      if inbounds(p2):
        nodes.add(p2)

      continue

      # Horribly naive, speed this up. ~700ms runtime
      for y in range(size):
        for x in range(size):
          candidate = Point(x ,y)
          if antinode_pos(first, second, candidate):
            nodes.add(candidate)
  return nodes

def PART1(inputs):
  #print(inputs)
  size, grid, index = inputs

  allantinodes = set()
  antinodes = {}
  for kind, positions in index.items():
    antinodes[kind] = calcantinodes(size, positions)
    allantinodes.update(antinodes[kind])

  def lookup(pos):
    if pos in allantinodes:
      return "#"
    elif pos in grid:
      return grid[pos]
  #print(grid_display(size, lookup, default="."))

  # Attempt 1: 336 - too high - counting non-unique antinodes
  # Attempt 2: 313
  return len(allantinodes)

def cast(point, direction):
  while True:
    yield point
    point += direction

def calc2(size, positions):
  # copy!
  positions = set(positions)

  def inbounds(p):
    return 0 <= p.x < size and 0 <= p.y < size

  nodes = set()
  while len(positions) >= 2:
    first = positions.pop()
    n = set()

    for second in positions:
      delta = first - second

      # Usage of cast always guarantees the presence of
      # first + second in the output.
      for pos in cast(first, delta):
        if not inbounds(pos):
          break
        n.add(pos)

      for pos in cast(first, -delta):
        if not inbounds(pos):
          break
        n.add(pos)

    nodes.update(n)

  return nodes

def PART2(inputs):
  size, grid, index = inputs

  antinodes = set()
  for kind, positions in index.items():
    antinodes.update(calc2(size, positions))

  def lookup(pos):
    if pos in antinodes:
      return "#"
    elif pos in grid:
      return grid[pos]
  #print(grid_display(size, lookup, default="."))
  # 1064
  return len(antinodes)
