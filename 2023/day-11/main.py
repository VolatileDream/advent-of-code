#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

import math

LOAD = "content"
def REWRITE(lines):
  for l in lines:
    print(l)
  universe = set()
  for row, line in enumerate(lines):
    for col, val in enumerate(line):
      if val == "#":
        universe.add((row,col))

  # (size, universe)
  return ((len(lines), len(lines[0])), universe)

def print_universe(size, universe):
  maxrow, maxcol = size
  for row in range(maxrow):
    line = ""
    for col in range(maxcol):
      if (row, col) in universe:
        line += "#"
      else:
        line += "."
    print(line)

def expand_dict(empties, maxsize, distmul=2):
  # splat the list into an array of deltas.
  empties = list(empties)
  empties.sort()
  #print(empties)
  diff = {}
  c = 0
  i = 0
  while len(empties):
    n = empties.pop(0)
    while c < n:
      diff[c] = i
      c += 1
    i += (distmul - 1)
  while c < maxsize:
    diff[c] = i
    c += 1
  #print(diff) 
  return diff


def expand(size, universe, distmul=2):
  maxrows, maxcols = size
  seenrow = set()
  seencol = set()
  for p in universe:
    r, c = p
    seenrow.add(r)
    seencol.add(c)

  #print("seen", seenrow, seencol)
  emptyrows = []
  for r in range(maxrows):
    if r not in seenrow:
      emptyrows.append(r)
  emptycols = []
  for c in range(maxcols):
    if c not in seencol:
      emptycols.append(c)
  #print(emptyrows, emptycols)

  rowdiff = expand_dict(emptyrows, maxrows, distmul)
  coldiff = expand_dict(emptycols, maxcols, distmul)

  #print(rowdiff, coldiff)

  # Rewrite points with expansion.
  expanded = set()
  for (r, c) in universe:
    r2 = rowdiff[r] + r
    c2 = coldiff[c] + c
    print("expanding", (r,c), "to", (r2,c2))
    expanded.add((r2, c2))

  return expanded


def total_distances(universe):
  # path lengths for all pairs of points.
  # Paths are conveniently on the grid, no diagonals, so it's just coordinate deltas.

  def dist(g, o):
    r1, c1 = g
    r2, c2 = o
    return int(math.fabs(r1 - r2) + math.fabs(c1 - c2))

  total_dist = 0
  galaxies = list(universe)
  for idx, g in enumerate(galaxies):
    for jdx, o in enumerate(galaxies[idx + 1:]):
      total_dist += dist(g, o)

  return total_dist


def PART1(inputs):
  size, universe = inputs
  #print(inputs)
  universe = expand(size, universe)
  #print(universe)

  # Attempt 1: coordinate deltas.
  return total_distances(universe)

def PART2(inputs):
  size, universe = inputs
  #print(inputs)
  #print_universe(size, universe)
  universe = expand(size, universe, distmul=1000000)
  #print_universe((size[0] * 10, size[1] * 10), universe)
  #print(universe)

  # Attempt 1: 328042392820 - coordinate deltas.
  # Attempt 2: 483844716556 - coordinate deltas, after fixing off by one in expand.
  return total_distances(universe)
