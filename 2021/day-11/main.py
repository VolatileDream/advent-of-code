#!/usr/bin/env python-mr

from collections import defaultdict
from _.data.formatting.blocks import Block

ADJACENT = [
  (-1, -1),
  (-1, 0),
  (-1, +1),
  (0, -1),
  # No zero zero.
  (0, +1),
  (+1, -1),
  (+1, 0),
  (+1, +1)
]

class OctopiGrid:
  @staticmethod
  def parse(lines):
    g = {}
    for row, line in enumerate(lines):
      for col, d in enumerate(line):
        p = (row, col)
        g[p] = int(d)
    return OctopiGrid(g)

  def __init__(self, grid):
    self._grid = grid
    self._flashes = 0
    self._nines = set([p for p, val in self._grid.items() if val > 9])

  def __str__(self):
    sz = 11
    out = []
    for row in range(sz):
      r = []
      for col in range(sz):
        p = (row, col)
        r.append(str(self._grid.get(p, "")))
      out.append("".join(r))
    return "\n".join(out)

  def neighbours(self, pos):
    row, col = pos
    for r, c in ADJACENT:
      yield (row + r, col + c)

  def increment(self, p):
    self._grid[p] += 1
    if self._grid[p] > 9:
      self._nines.add(p)

  def flash(self, pos):
    assert self._grid[pos] > 9
    self._flashes += 1
    self._nines.discard(pos)
    for n in self.neighbours(pos):
      if n not in self._grid:
        # Past the edge of the grid
        continue

      self.increment(n)

  def step(self):
    for p in self._grid:
      self.increment(p)

    flashed = set()
    while self._nines:
      p = self._nines.pop()
      if p in flashed:
        continue
      flashed.add(p)
      self.flash(p)

    for f in flashed:
      self._grid[f] = 0

    return len(flashed) == len(self._grid)


def PART1(inputs):
  inputs = OctopiGrid.parse(inputs)
  print(inputs)
  for _i in range(100):
    inputs.step()
  return inputs._flashes


def PART2(inputs):
  inputs = OctopiGrid.parse(inputs)
  steps = 1
  while not inputs.step():
    steps += 1

  return steps
