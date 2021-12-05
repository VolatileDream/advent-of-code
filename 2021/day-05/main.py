#!/usr/bin/env python-mr

from collections import defaultdict
from _.data.formatting.blocks import Block

def point(string):
  col,row = string.split(",")
  return (int(row), int(col))


def sign(value):
  if value > 0:
    return 1
  elif value < 0:
    return -1
  else:
    return 0


class Grid:
  def __init__(self):
    self._max_row = 0
    self._max_col = 0
    self._grid = defaultdict(int)

  def point(self, point):
    self._grid[point] += 1
    row, col = point
    self._max_row = max(self._max_row, row)
    self._max_col = max(self._max_col, col)

  def line(self, p1, p2, with_diag=False):
    r1, c1 = p1
    r2, c2 = p2
    if (r1 != r2 and c1 != c2) and not with_diag:
      raise ValueError("Lines must match in x or y coordinate.")

    r_move, c_move = (r1 - r2, c1 - c2)
    if abs(r_move) != abs(c_move) and r_move != 0 and c_move != 0:
      raise ValueError("Uneven diagonal line: %s -> %s = %s" % (p1, p2, (r_move, c_move)))

    r_move = sign(r_move)
    c_move = sign(c_move)

    paint = p2
    while paint != p1:
      self.point(paint)
      paint = (paint[0] + r_move, paint[1] + c_move)

    self.point(p1)

  def __iter__(self):
    for key, value in self._grid.items():
      if value > 0:
        yield (key, value)

  def __str__(self):
    out = []
    for row in range(self._max_row + 1):
      line = []
      for col in range(self._max_col + 1):
        p = (row, col)
        line.append(str(self._grid.get(p, ".")))
      out.append("".join(line))

    return "\n".join(out)


LOAD = "content"
def REWRITE(lines):
  content = []
  for l in lines:
    start, end = l.split(" -> ")
    content.append((point(start), point(end)))

  return content


def PART1(inputs):
  print(inputs)
  g = Grid()
  for start, end in inputs:
    try:
      g.line(start, end)
    except ValueError:
      pass

  print(g)
  return sum([1 for _p, count in g if count > 1])


def PART2(inputs):
  g = Grid()
  for start, end in inputs:
    g.line(start, end, with_diag=True)

  print(g)
  return sum([1 for _p, count in g if count > 1])
