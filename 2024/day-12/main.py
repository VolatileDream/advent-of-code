#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.data.structures.inversion_list import InversionList
from _.data.structures.point import Point, CARDINAL
from _.games.advent_of_code.utils import to_grid, grid_display

LOAD = "content"
def REWRITE(lines):
  return to_grid(lines)

def TEST(inputs):
  pass

def connected(position, grid, seen):
  seen.add(position)
  letter = grid[position]

  for direction in CARDINAL:
    npos = position + direction
    if npos not in grid:
      continue
    if npos not in seen and grid[npos] == letter:
      connected(npos, grid, seen)
  return seen

def find_regions(grid):
  spaces = set(grid.keys())
  # Random point -> set of points
  # Verified we can't use the letters.
  regions = defaultdict(set)

  while spaces:
    start = spaces.pop()
    letter = grid[start]

    regions[start] = connected(start, grid, set())

    spaces.difference_update(regions[start])

  return regions

def region_surface(region, grid):
  sides = 0
  for p in region:
    letter = grid[p]
    for d in CARDINAL:
      if not same_region(p, grid, d):
        sides += 1
  return sides

def PART1(inputs):
  #print(inputs)
  grid, maxsize = inputs

  regions = find_regions(grid)
  #print(regions)

  price = 0
  for p, points in regions.items():
    area = len(points)
    surface = region_surface(points, grid)
    price += area * surface

  # 1573474
  return price

def same_region(point, grid, direction):
  return grid[point] == grid.get(point + direction)

def region_sides(region, grid, maxsize):
  # Err: this mishandles test cases like this:
  #    AAAAAA
  #    AAA  A
  #    AAA  A
  #    A  AAA
  #    A  AAA
  #    AAAAAA
  # by joining the inside sides together across the A-A diagonal corner.
  # Unfortunately this is intrinsic to the inversion list. :(

  # To compute the number of sides, we check adjacency on each point
  # and add points that have no neighboirs to the inversion list.
  xaxis = defaultdict(InversionList)
  yaxis = defaultdict(InversionList)
  for p in region:
    # Points increment down and to the right.
    if not same_region(p, grid, Point(0, -1)):
      yaxis[p.y] += p.x
    if not same_region(p, grid, Point(-1, 0)):
      xaxis[p.x] += p.y
    if not same_region(p, grid, Point(0, 1)):
      yaxis[p.y + 1] += p.x
    if not same_region(p, grid, Point(1, 0)):
      xaxis[p.x + 1] += p.y

  #print("region", region)
  def lookup(p):
    if p in region:
      return grid[p]

  # Count the segments in the inversion list to find the number of sides
  funny = False
  sides = 0
  for x, l in xaxis.items():
    sides += len(l.raw())
    #print("x", x, l.raw())
    for y, ly in yaxis.items():
      if x in ly and (x-1) in ly and (x+1) in ly and y in l:
        funny = True
  for y, l in yaxis.items():
    sides += len(l.raw())
    #print("y", y, l.raw())
    for x, lx in xaxis.items():
      if y in lx and (y-1) in lx and (y+1) in lx and x in l:
        funny = True

  if not funny:
    return sides

  # Funny shapes have side intersections inside themselves.
  # This often means things like this, that don't count properly:
  #    AAAAAA   
  #    AAA  A          AAA
  #    AAA  A    or    A.A
  #    A  AAA          AA.
  #    A  AAA
  #    AAAAAA
  #
  # Thankfully there are only a few of these shapes.
  print(grid_display(maxsize,lookup))
  #print("sides", sides)
  return sides

def region_sides(region, grid, maxsize):
  edges = set()
  for p in region:
    for d in CARDINAL:
      if not same_region(p, grid, d):
        edges.add((p, d,))

  #print("region", region)
  def lookup(p):
    if p in region:
      return grid[p]

  # This bit of cleverness was derived from r/adventofcode
  # For each edge, shift it parallel to the side it's on.
  # After doing this for all edges, remove the derived edges from
  # the full edge list.
  #
  # For each side it generates all the edges but one!

  shifted = {(pos + Point(d.y, d.x), d) for pos, d in edges}
  edges.difference_update(shifted)
  return len(edges)


def PART2(inputs):
  grid, maxsize = inputs

  regions = find_regions(grid)
  #print(regions)

  price = 0
  for p, points in regions.items():
    area = len(points)
    sides = region_sides(points, grid, maxsize)
    price += area * sides

  # Attempt 1: 956972 - too low
  # Attempt 2: 959057 - too low
  # 966476
  return price
