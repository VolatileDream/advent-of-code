#!/usr/bin/python3

import argparse
import collections
import re
import sys
import typing


def load_file(filename):
  contents = []
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip() # remove trailing newline
      contents.append(line)
  return contents


def any_item(iterable, default=None):
  for i in iterable:
    return i
  return default


class Position(typing.NamedTuple):
  x: int
  y: int
  z: int

  def __neg__(self):
    return Position(-self.x, -self.y, -self.z)

  def __sub__(self, other):
    return -other + self

  def __add__(self, other):
    return Position(self.x + other.x, self.y + other.y, self.z + other.z)

  @staticmethod
  def unit():
    return Position(1, 1, 1)

  @staticmethod
  def do_coords(p1, p2, func):
    if p1 is None:
      return p2
    elif p2 is None:
      return p1
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    return Position(func(x1, x2), func(y1, y2), func(z1, z2))

  def min(self, other):
    return Position.do_coords(self, other, min)

  def max(self, other):
    return Position.do_coords(self, other, max)

  @staticmethod
  def iterate_range(p1, p2):
    l_x, l_y, l_z = Position.min(p1, p2)
    h_x, h_y, h_z = Position.max(p1, p2)
    for z in range(l_z, h_z + 1):
      for y in range(l_y, h_y + 1):
        for x in range(l_x, h_x + 1):
          yield Position(x, y, z)


# dict with keys limited to True & False
class ConwayND:
  def __init__(self, CoordClass):
    self.grid = set()
    self.clz = CoordClass
    self.max = None
    self.min = None

  @staticmethod
  def from_lines(lines, CoordClass, **defaults):
    state = ConwayND(CoordClass)
    for y, l in enumerate(lines):
      for x, c in enumerate(l):
        if c == '#':
          state[CoordClass(x=x, y=y, **defaults)] = True
    return state

  def __update_minmax__(self, key=None):
    if key:
      # incremental
      self.min = key.min(self.min)
      self.max = key.max(self.max)
    else:
      # full update
      self.min = self.max = any_item(self.grid)
      for p in grid:
        self.__update_minmax__(p)

  def __getitem__(self, key):
    return key in self.grid

  def __setitem__(self, key, value):
    if value:
      self.grid.add(key)
      self.__update_minmax__(key)
    elif key in self.grid:
      self.grid.remove(key)

  def step(self, adj_func, active_func):
    updated = ConwayND(self.clz)
    for p in self.clz.iterate_range(self.min - self.clz.unit(), self.max + self.clz.unit()):
      adj = set(adj_func(p))
      count = len(adj.intersection(self.grid))
      updated[p] = active_func(self[p], count)

    return updated

  def bounds(self):
    return (self.min, self.max)

  def __repr__(self):
    lower, higher = self.bounds()
    if lower is None or higher is None:
      return ""
    l_x, l_y, l_z = lower
    h_x, h_y, h_z = higher
    layers = ""
    for z in range(l_z, h_z + 1):
      layers += "z={}\n".format(str(z))
      for y in range(l_y, h_y + 1):
        for x in range(l_x, h_x + 1):
          c = '.'
          if Position(x, y, z) in self.grid:
            c = '#'
          layers += c
        layers += '\n'
      layers += '\n'
    return layers


def adjacent(p):
  u = p.unit()
  for adj in p.iterate_range(p - u, p + u):
    if adj == p:
      continue
    yield adj


def active(state, count):
  # equivalent to:
  # state and count in [2, 3] => True
  # not state and count == 3 => True
  # else => False
  return count == 3 or (state and count == 2)


def part1(things):
  things = ConwayND.from_lines(things, CoordClass=Position, z=0)
  for i in range(6):
    print("iteration", i)
    #print(repr(things))
    things = things.step(adjacent, active)

  return len(things.grid) 


class P4(typing.NamedTuple):
  x: int
  y: int
  z: int
  w: int

  def __neg__(self):
    return P4(-self.x, -self.y, -self.z, -self.w)

  def __sub__(self, other):
    return -other + self

  def __add__(self, other):
    return P4(self.x + other.x, self.y + other.y, self.z + other.z, self.w + other.w)

  @staticmethod
  def unit():
    return P4(1, 1, 1, 1)

  @staticmethod
  def do_coords(p1, p2, func):
    if p1 is None:
      return p2
    elif p2 is None:
      return p1
    x1, y1, z1, w1 = p1
    x2, y2, z2, w2 = p2
    return P4(func(x1, x2), func(y1, y2), func(z1, z2), func(w1, w2)) 

  def min(self, other):
    return P4.do_coords(self, other, min)

  def max(self, other):
    return P4.do_coords(self, other, max)

  @staticmethod
  def iterate_range(p1, p2):
    l_x, l_y, l_z, l_w = P4.min(p1, p2)
    h_x, h_y, h_z, h_w = P4.max(p1, p2)
    for z in range(l_z, h_z + 1):
      for y in range(l_y, h_y + 1):
        for x in range(l_x, h_x + 1):
          for w in range(l_w, h_w + 1):
            yield P4(x, y, z, w)


def part2(things):
  things = ConwayND.from_lines(things, CoordClass=P4, z=0, w=0)
  for i in range(6):
    print("iteration", i)
    #print(repr(things))
    things = things.step(adjacent, active)

  return len(things.grid) 


def main(filename):
  things = load_file(filename)

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
