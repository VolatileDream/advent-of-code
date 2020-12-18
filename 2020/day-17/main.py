#!/usr/bin/python3

import argparse
import collections
import functools
import itertools
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

  __dimension_deltas_cache__ = {}

  def __init__(self, dimensions):
    self.values = dimensions
    self.__hash = None

  def __repr__(self):
    return "Coordinate({})".format(", ".join([str(i) for i in self.values]))

  @staticmethod
  def deltas(dimensions):
    cache = Coordinate.__dimension_deltas_cache__
    cached = cache.get(dimensions, None)
    if cached is None:
      all_items = list(itertools.product((-1, 0, 1), repeat=dimensions))
      all_items.remove((0,) * dimensions)
      cache[dimensions]  = frozenset([Coordinate(c) for c in all_items])
    return cache[dimensions]

  @staticmethod
  def zero(dimensions):
    return Coordinate((0,) * dimensions)

  def get_zero(self):
    return Coordinate.zero(len(self))

  @staticmethod
  def unit(dimensions):
    return Coordinate((1,) * dimensions)

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
    return state.freeze()

  def __update_minmax__(self, key):
    # incremental
    self.min = key.min(self.min)
    self.max = key.max(self.max)

  def __getitem__(self, key):
    return key in self.grid

  def __setitem__(self, key, value):
    assert type(value) == bool
    if value:
      self.grid.add(key)
      self.__update_minmax__(key)
    # ignore updates that don't set Value to True.

  def freeze(self):
    self.grid = frozenset(self.grid)
    return self

  def step(self):
    updated = ConwayND(self.clz)

    # Extra optimization:
    # Because we start with a 2D input, all other dimensions end up being symmetric.
    # That is, if point (x, y, z, ...) is alive, then (x, y, -z, - ...) is too.
    # you could in theory process half the point space using this (taking care to handle)
    # (x, y, 0...) specially (all of it's alive counts would need to be doubled).
    #
    # This is not done below.

    # Count the number of alive items beside every point
    alive = collections.defaultdict(int)
    for p in self.grid:
      alive[p] += 1
      for d in Coordinate.deltas(len(p)):
        alive[p + d] += 1

    for point, count in alive.items():
      # For all the alive points, set their alive status
      updated[point] = count == 3 or (self[point] and count == 2)

    return updated.freeze()

  def bounds(self):
    return (self.min, self.max)


def product(p):
  o = 1
  for c in p.values:
    o *= c
  return o


def flip_lastn(point):
  # flip the sign of all but the first two indicies

  # extract the tuple
  t = point.values
  last = t[2:]
  flipped = tuple()
  for l in last:
    flipped += (-l,)
  return Coordinate(t[:2] + flipped)


def run(things, dimensions, cycles=6):
  things = ConwayND.from_lines2(things, [0] * (dimensions - 2))
  for i in range(cycles):
    print("iteration", i)
    things = things.step()

  # compare the "up" and "down" layers
  for point in things.grid:
    opposite = flip_lastn(point)
    assert opposite in things.grid

  return len(things.grid)


def part1(things):
  return run(things, 3)


def part2(things):
  return run(things, 4)


def main(filename):
  things = load_file(filename)

  print("adjacent", Coordinate.unit(3), len(Coordinate.deltas(3)))
  print("adjacent", Coordinate.unit(4), len(Coordinate.deltas(4)))

  print("part 1:", part1(things))
  print("part 2:", part2(things))
  #print("6d, 4c:", run(things, dimensions=6, cycles=4))


if __name__ == "__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
