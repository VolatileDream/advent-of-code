#!/usr/bin/env python-mr

from collections import defaultdict
from queue import PriorityQueue
from _.data.formatting.blocks import Block

class Grid:
  @staticmethod
  def parse(string):
    g = {}
    for row, line in enumerate(string):
      for col, v in enumerate(line):
        p = (row, col)
        g[p] = int(v)

    m = (row + 1, col + 1)
    return Grid(g, m)

  def __init__(self, pos, maximum):
    self._pos = pos
    self._max = maximum

  def neighbours(self, p):
    row, col = p
    yield (row - 1, col)
    yield (row + 1, col)
    yield (row, col - 1)
    yield (row, col + 1)

  def size(self):
    return self._max

  def __contains__(self, key):
    return key in self._pos

  def __getitem__(self, key):
    return self._pos[key]

  def __iter__(self):
    return iter(self._pos)

  def __str__(self):
    out = []
    height, width = self.size()
    for row in range(height):
      l = []
      for col in range(width):
        p = (row, col)
        if p not in self:
          l.append(".")
        else:
          l.append(str(self[p]))
      out.append("".join(l))

    return "\n".join(out)


class BiggerGrid:
  def __init__(self, grid, multiple):
    self._g = grid
    self._multiple = multiple

  def __str__(self):
    out = []
    height, width = self.size()
    for row in range(height):
      l = []
      for col in range(width):
        p = (row, col)
        if p not in self:
          l.append(".")
        else:
          l.append(str(self[p]))
      out.append("".join(l))

    return "\n".join(out)

  def get(self, key, default):
    row, col = key

    if row < 0 or col < 0:
      return default

    height, width = self._g.size()
    orow, ocol = row % height, col % width
    crow, ccol = row // height, col // width

    if crow >= self._multiple or ccol >= self._multiple:
      return default

    c = self._g[(orow, ocol)] + crow + ccol
    return (c - 1) % 9 + 1

  def __contains__(self, key):
    return self.get(key, None) is not None

  def __getitem__(self, key):
    val = self.get(key, None)
    if val is None:
      raise Exception()
    return val

  def size(self):
    height, width = self._g.size()
    return (height * self._multiple, width * self._multiple)

  def neighbours(self, p):
    row, col = p
    yield (row - 1, col)
    yield (row + 1, col)
    yield (row, col - 1)
    yield (row, col + 1)



def bfs(grid, start):
  costs = { start: 0 }
  visiting = set([])
  visit = PriorityQueue()
  for n in grid.neighbours(start):
    if n in grid:
      visit.put((grid[n], n))
      visiting.add(n)
  seen = set([start])

  while not visit.empty():
    priority, now = visit.get()
    visiting.discard(now)
    if now in seen:
      continue
    seen.add(now)

    cs = [costs[n] for n in grid.neighbours(now) if n in costs]
    costs[now] = grid[now] + min(cs)

    for n in grid.neighbours(now):
      if n in grid and n not in seen:
        visit.put((costs[now] + grid[n], n))
        visiting.add(n)

  return costs


LOAD = "content"
def REWRITE(lines):
  return Grid.parse(lines)


def PART1(inputs):
  print(inputs)
  print(inputs.size())
  costs = bfs(inputs, (0,0))
  r, c = inputs.size()
  return costs[(r - 1, c - 1)]


def PART2(inputs):
  bigger = BiggerGrid(inputs, 5)
  print(bigger)
  print(bigger.size())
  costs = bfs(bigger, (0,0))
  r, c = bigger.size()
  return costs[(r - 1, c - 1)]

