#!/usr/bin/env python-mr

import re
import typing
from collections import defaultdict
from _.data.formatting.blocks import Block

class Point(typing.NamedTuple):
  x: int
  y: int

  @staticmethod
  def parse(line):
    x, y = line.split(",")
    return Point(int(x), int(y))

  def __repr__(self):
    return f"Point({self.x}, {self.y})"

  def reflect(self, x=None, y=None):
    # Reflects points on the specified x and/or y lines.
    #
    # Reflects points such that the generated point falls under (x,y)
    if not (x or y):
      raise Exception("Must provide x or y for reflect")

    out_x = self.x
    out_y = self.y

    if x:
      out_x = x - abs(out_x - x)
    if y:
      out_y = y - abs(out_y - y)

    return Point(out_x, out_y)


class Fold(typing.NamedTuple):
  RE = re.compile("fold along ([xy])=(\d+)")

  x: typing.Optional[int] = None
  y: typing.Optional[int] = None

  @staticmethod
  def parse(line):
    m = Fold.RE.match(line)
    if m.group(1) == "x":
      return Fold(x=int(m.group(2)))
    return Fold(y=int(m.group(2)))

  def __repr__(self):
    if self.x:
      return f"Fold(x={self.x})"
    return f"Fold(y={self.y})"

  def reflect(self, point):
    return point.reflect(self.x, self.y)


def biggest_coords(points):
  mx = 0
  my = 0
  for p in points:
    mx = max(p.x, mx)
    my = max(p.y, my)

  return Point(mx, my)


def print_points(points):
  x, y = biggest_coords(points)
  out = []
  for col in range(x + 1):
    line = []
    for row in range(y + 1):
      if Point(col, row) in points:
        line.append("#")
      else:
        line.append(".")
    out.append("".join(line))
    print("".join(line))

  return "\n".join(out)


LOAD = "groups"
def REWRITE(lines):
  dots = set([Point.parse(l) for l in lines[0]])
  folds = [Fold.parse(l) for l in lines[1]]
  return (dots, folds)


def PART1(inputs):
  points, folds = inputs
  print(inputs)

  update = set([folds[0].reflect(p) for p in points])
  return len(update)


def PART2(inputs):
  points, folds = inputs
  print()

  ps = points
  for f in folds:
    ps = set([f.reflect(p) for p in ps])

  print_points(ps)
