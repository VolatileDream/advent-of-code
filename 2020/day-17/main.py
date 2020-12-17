#!/usr/bin/python3

import argparse
import collections
import functools
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


class Coordinate:
  def __init__(self, dimensions):
    self.values = dimensions
    self.__hash = None

  def __repr__(self):
    return "Coordinate({})".format(", ".join([str(i) for i in self.values]))

  @staticmethod
  def zero(length):
    return Coordinate((0,) * length)

  def get_zero(self):
    return Coordinate.zero(len(self))

  @staticmethod
  def unit(length):
    return Coordinate((1,) * length)

  def get_unit(self):
    return Coordinate.unit(len(self))

  def __len__(self):
    return len(self.values)

  def __update__(self, func, other):
    assert len(self) == len(other)
    return Coordinate(tuple(map(func, zip(self.values, other.values))))

  def __hash__(self):
    return hash(self.values)

  def __neg__(self):
    return Coordinate(tuple(map(lambda a: -a, self.values)))

  def __sub__(self, other):
    return self.__update__(lambda a: a[0] - a[1], other)

  def __add__(self, other):
    return self.__update__(lambda a: a[0] + a[1], other)

  def __eq__(self, other):
    return self.values == other.values

  def min(self, other):
    if other is None:
      return self
    return self.__update__(min, other)

  def max(self, other):
    if other is None:
      return self
    return self.__update__(max, other)

  @staticmethod
  def __r(lower, higher):
    if len(lower) == 0:
      yield tuple()
      return
    l, *lrest = lower
    h, *hrest = higher

    for v in range(l, h+1):
      for r in Coordinate.__r(lrest, hrest):
        yield (v,) + r

  @staticmethod
  def range(p1, p2):
    lower = p1.min(p2)
    higher = p1.max(p2)
    assert lower == p1
    assert higher == p2

    for c in Coordinate.__r(lower.values, higher.values):
      yield Coordinate(c)

  @staticmethod
  def range_distance(p1, p2):
    # output len(range(p1, p2))
    lower = p1.min(p2)
    higher = p1.max(p2)
    count = 1
    for one, two in zip(lower.values, higher.values):
      count *= two - one

    return count

# dict with keys limited to True & False
class ConwayND:
  def __init__(self, CoordClass):
    self.grid = set()
    self.clz = CoordClass
    self.max = None
    self.min = None

  @staticmethod
  def from_lines2(lines, ext):
    state = ConwayND(Coordinate)
    for y, l in enumerate(lines):
      for x, c in enumerate(l):
        if c == '#':
          state[Coordinate(tuple([x, y] + ext))] = True
    return state

  def __update_minmax__(self, key):
    # incremental
    self.min = key.min(self.min)
    self.max = key.max(self.max)

  def __getitem__(self, key):
    return key in self.grid

  def __setitem__(self, key, value):
    if value:
      self.grid.add(key)
      self.__update_minmax__(key)
    elif key in self.grid:
      self.grid.remove(key)

  def step(self, adj_func):
    updated = ConwayND(self.clz)

    # Count the number of alive items beside every point
    alive = collections.defaultdict(int)
    for p in self.grid:
      alive[p] += 1
      for a in adj_func(p):
        alive[a] += 1

    for point, count in alive.items():
      # For all the alive points, set their alive status
      updated[point] = count == 3 or (self[point] and count == 2)

    return updated

  def bounds(self):
    return (self.min, self.max)


def product(p):
  o = 1
  for c in p.values:
    o *= c
  return o


def adjacent(p):
  u = p.get_unit()
  for adj in p.range(p - u, p + u):
    if adj == p:
      continue
    yield adj


def part1(things):
  things = ConwayND.from_lines2(things, [0])
  for i in range(6):
    print("iteration", i)
    #print(repr(things))
    things = things.step(adjacent)

  return len(things.grid) 


def part2(things):
  things = ConwayND.from_lines2(things, [0, 0])
  for i in range(6):
    print("iteration", i)
    #print(repr(things))
    things = things.step(adjacent)

  return len(things.grid) 


def main(filename):
  things = load_file(filename)

  print("adjacent", Coordinate.unit(3), len(list(adjacent(Coordinate.unit(3)))))
  print("adjacent", Coordinate.unit(4), len(list(adjacent(Coordinate.unit(4)))))

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
