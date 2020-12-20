#!/usr/bin/python3

import argparse
import collections
import enum
import itertools
import functools
import math
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


def load_groups(filename):
  # because some files follow this format instead.
  contents = []
  acc = [] 
  for line in load_file(filename):
    if line:
      acc.append(line)
    else:
      contents.append(acc)
      acc = []

  if acc:
    contents.append(acc)

  return contents


def any_item(iterable, default=None):
  for i in iterable:
    return i
  return default


class Rotation(enum.Enum):
  NO_ROTATION = 0
  ROT_90  = 1
  ROT_180 = 2
  ROT_270 = 3

  def transform_point(self, p):
    if self == Rotation.NO_ROTATION:
      return p

    x, y = p
    if self == Rotation.ROT_180:
      x, y = (-x, -y)
    elif self == Rotation.ROT_90:
      x, y = (y, -x)
    else:
      x, y = (-y, x)

    return Position(x, y)

  @staticmethod
  def test():
    p = Position(1, 2)
    assert Rotation.NO_ROTATION.transform_point(p) == p
    assert Rotation.ROT_90.transform_point(p) == Position(2, -1)
    assert Rotation.ROT_180.transform_point(p) == Position(-1, -2)
    assert Rotation.ROT_270.transform_point(p) == Position(-2, 1)


class Orientation(enum.IntFlag):
  NO_FLIP = 0
  HORIZONTAL_FLIP = 1
  VERTICAL_FLIP = 2
  BOTH_FLIP = 3

  def transform_point(self, p):
    if self == Orientation.NO_FLIP:
      return p

    x, y = p
    if bool(Orientation.HORIZONTAL_FLIP & self):
      y = -y
    if bool(Orientation.VERTICAL_FLIP & self):
      x = -x

    return Position(x, y)

  @staticmethod
  def test():
    p = Position(1, 2)
    assert Orientation.NO_FLIP.transform_point(p) == p
    assert Orientation.HORIZONTAL_FLIP.transform_point(p) == Position(1, -2)
    assert Orientation.VERTICAL_FLIP.transform_point(p) == Position(-1, 2)
    assert Orientation.BOTH_FLIP.transform_point(p) == Position(-1, -2)


class Spot(enum.IntEnum):
  TOP = 0
  RIGHT = 1
  BOTTOM = 2
  LEFT = 3


class Position(typing.NamedTuple):
  x: int
  y: int

  def transform(self, o=Orientation.NO_FLIP, r=Rotation.NO_ROTATION):
    return o.transform_point(r.transform_point(self))


class Tile:
  @staticmethod
  def from_lines(lines):
    name = int(lines[0].split(" ")[1].strip(":"))
    spots = set()
    values = {}
    for y, line in enumerate(lines[1:]):
      for x, c in enumerate(line):
        if c == '#':
          spots.add(Position(x, y))
        values[Position(x, y)] = c

    return Tile(name, spots, len(lines[1]), values)

  def __init__(self, name, grid, size, values=None):
    self.name = name
    self.grid = grid
    self.size = size

    self.values = values

    # cache for rotation / transformation of edges
    self.edges = self.__edge_cache()
    self.uedges = self.__unique_edges()

  def __repr__(self):
    out = ["Tile {}:".format(self.name)]
    for y in range(self.size):
      line = []
      for x in range(self.size):
        line.append(self.values[Position(x,y)])
      out.append(''.join(line))
    return '\n'.join(out)

  def __unique_edges(self):
    edges = set()
    for transform in self.edges:
      edges.update(self.edges[transform])

    return edges

  def unique_edges(self):
    return self.uedges

  def __edge_cache(self):
    cache = {}

    def rev(value):
      rev = 0
      for _ in range(self.size):
        rev = (rev << 1) | (value & 1)
        value = value >> 1
      return rev

    def gen_rotations(orientation, top, right, bottom, left):
      rtop, rright, rbottom, rleft = (rev(top), rev(right), rev(bottom), rev(left))
      cache[(orientation, Rotation.NO_ROTATION)] = [top, right, bottom, left]
      cache[(orientation, Rotation.ROT_90)] = [rleft, top, rright, bottom]
      cache[(orientation, Rotation.ROT_180)] = [rbottom, rleft, rtop, rright]
      cache[(orientation, Rotation.ROT_270)] = [right, rbottom, left, rtop]

    top, right, bottom, left = self.__base_edges()
    rtop, rright, rbottom, rleft = (rev(top), rev(right), rev(bottom), rev(left))

    gen_rotations(Orientation.NO_FLIP, top, right, bottom, left)
    gen_rotations(Orientation.HORIZONTAL_FLIP, bottom, rright, top, rleft)
    gen_rotations(Orientation.VERTICAL_FLIP, rtop, left, rbottom, right)
    gen_rotations(Orientation.BOTH_FLIP, rbottom, rleft, rtop, rright)
   
    # reduce cache items that are equivalent.
 
    return cache

  def __base_edges(self):
    top = []
    right = []
    bottom = []
    left = []
    size = self.size
    end = size - 1
    # these are generated top to bottom, left to right
    for i in range(size):
      if Position(i, 0) in self.grid:
        top.append("1")
      else:
        top.append("0")

      if Position(end, i) in self.grid:
        right.append("1")
      else:
        right.append("0")

      if Position(i, end) in self.grid:
        bottom.append("1")
      else:
        bottom.append("0")

      if Position(0, i) in self.grid:
        left.append("1")
      else:
        left.append("0")
 
    top = ''.join(top)
    right = ''.join(right)
    bottom = ''.join(bottom)
    left = ''.join(left)
    return [int(top, 2), int(right, 2), int(bottom, 2), int(left, 2)]

  def __base_edges_values(self):
    top = []
    right = []
    bottom = []
    left = []
    size = self.size
    end = size - 1
    # these are generated top to bottom, left to right
    for i in range(size):
      top.append(self.values[Position(i, 0)])
      right.append(self.values[Position(end, i)])
      bottom.append(self.values[Position(i, end)])
      left.append(self.values[Position(0, i)])
 
    top = ''.join(top)
    right = ''.join(right)
    bottom = ''.join(bottom)
    left = ''.join(left)
    return [top, right, bottom, left]

  def matches_edges(self, edges):
    #print("set check", self.uedges, edges)
    return self.uedges.issuperset(edges)

  def match_restriction(self, etop, eright, ebottom, eleft):
    def build_matcher(expect):
      if expect:
        return lambda value: expect == value
      return lambda value: True
        
    matchers = [build_matcher(e) for e in [etop, eright, ebottom, eleft]]

    possible_matches = []
    for o in Orientation:
      for r in Rotation:
        matches = functools.reduce(lambda a,b: a and b,
                                   map(lambda t: t[0](t[1]),
                                       zip(matchers, self.get_edges(o, r))),
                                   True)
        if matches:
          possible_matches.append((o, r))
    return possible_matches

  def get_edges(self, orientation, rotation):
    return self.edges[(orientation, rotation)]


class TileGrid:
  @staticmethod
  def from_groups(groups):
    return TileGrid([Tile.from_lines(g) for g in groups])

  def __init__(self, tiles):
    self.tiles = tiles
    self.size = math.isqrt(len(tiles))
    self.tiles_by_edge = self.__tile_index()

  def __tile_index(self):
    index = {}
    for i, t in enumerate(self.tiles):
      for e in t.unique_edges():
        if e not in index:
          index[e] = set()
        index[e].add(i)

    return index

  def unique_edges(self):
    edges = set()
    for t in self.tiles:
      edges.update(t.unique_edges())
    return edges

  def corners(self):
    end = self.size - 1
    yield Position(0, 0)
    yield Position(0, end)
    yield Position(end, 0)
    yield Position(end, end)

  def print_placement(self, placement):
    out = []
    for y in range(self.size):
      line = []
      for x in range(self.size):
        index, _, _ = placement[Position(x, y)]
        name = str(self.tiles[index].name)
        line.append(name)
      out.append(" ".join(line))
    return "\n".join(out)

  def next_position(self, p):
    x, y = p
    if x + 1 >= self.size and y + 1>= self.size:
      return None
    if x + 1 >= self.size:
      return Position(0, y + 1)
    return Position(x + 1, y)

  def __get_restriction(self, existing, position):
    # set up such that existing[(x,y)].get_edges()[s] gives us the restriction on this side.
    # iteration order matches Tile.get_edges(...) ordering.
    x, y = position
    adjacents = [
      (x, y - 1, Spot.BOTTOM), # above position
      (x + 1, y, Spot.LEFT), # to the right
      (x, y + 1, Spot.TOP), # below position
      (x - 1, y, Spot.RIGHT), # to the left
    ]
    for x, y, side in adjacents:
      p = Position(x, y)
      beside = existing.get(p, None)

      if not beside:
        yield None
        continue

      index, orientation, rotation = beside

      yield self.tiles[index].get_edges(orientation, rotation)[side]
    return
  
  def __m(self, tried, used, existing_placement, position):
    indent = "|" * (len(existing_placement) + 1)
    if len(existing_placement) == self.size * self.size:
      # placed everything! yay!
      return existing_placement

    if len(existing_placement) == 0:
      print()
      pass

    next_pos = self.next_position(position)
    restriction = list(self.__get_restriction(existing_placement, position))
    restriction_edges = [r for r in restriction if r]

    #print(indent, "trying", position, len(existing_placement))
    #print(indent, "restrictions:", restriction)

    possible = set(range(len(self.tiles))).difference(used)
    for r in restriction_edges:
      # restrictions are double use, ignore none entries.
      possible = possible.intersection(self.tiles_by_edge[r])

    #print(indent, "possible:", possible)

    for i in possible:
      tile = self.tiles[i]
      name = tile.name

      if not tile.matches_edges(restriction_edges):
        #print(indent, "no edge match", name)
        continue

      matching_placements = tile.match_restriction(*restriction)
      if len(matching_placements) == 0:
        #print(indent, "trying", position, "can't match", name, "into", restriction)
        continue

      #print(indent, "match", name, "in", position, "with", len(matching_placements), "options")
      for orientation, rotation in matching_placements:
        #print(indent, "trying", name, "in", orientation, rotation)
        next_place = dict(existing_placement)
        next_place[position] = (i, orientation, rotation)

        next_used = set(used)
        next_used.add(i)

        if next_pos is None:
          return next_place

        #tried.add((position, i, orientation, rotation))
        result = self.__m(tried, next_used, next_place, next_pos)
        if result:
          return result

    #print(indent, "no matches", position)
    return None

  def __start_match(self, tried, used, existing_placement, position):
    all_edges = self.unique_edges()

    edge_count = {e: 0 for e in all_edges} # count number of tiles with this edge.
    for t in self.tiles:
      for e in t.unique_edges():
        edge_count[e] += 1

    shared_edge_count = { i: 0 for i in range(len(self.tiles)) }
    for i, t in enumerate(self.tiles):
      for e in t.unique_edges():
        # edge_count has count 2 or more it means at least 2 tiles share the edge.
        if edge_count[e] > 1:
          shared_edge_count[i] += 1

    min_shared = min(shared_edge_count.values())

    #print(edge_count)
    #print(shared_edge_count)
    #print(min_shared)

    corners = []
    for index, count in shared_edge_count.items():
      if count == min_shared:
        corners.append(index)

    print("min shared edges", min_shared, "corner tiles", corners)
    # our corner tiles are going to be one of the tiles with fewest shared edges.

    for i in corners:
      for orientation in Orientation:
        for rotation in Rotation:
          placement = dict()
          placement[Position(0, 0)] = (i, orientation, rotation)
          used = set()
          used.add(i)
          result = self.__m(set(), used, placement, self.next_position(Position(0, 0)))
          if result:
            return result

    return None

  def find_placement(self):
    # dict of Position(x, y) => (Tile index, Orientation, Rotation)
    placement = {}
    # set of (Position(x, y), index, Orientation, Rotation)
    tried = set()
    # set of indicies used already
    used = set()
    return self.__m(tried, used, placement, Position(0, 0))
    #return self.__start_match(tried, used, placement, Position(0, 0))


def product(args):
  p = 1
  for a in args:
    p *= a
  return p

def part1(things):
  grid = things.find_placement()
  print(grid)
  print()
  print(things.print_placement(grid))
  print()

  return product([things.tiles[grid[p][0]].name for p in things.corners()])

def part2(things):
  pass


def main(filename):
  things = TileGrid.from_groups(load_groups(filename))
  print(things.tiles[0])
  print("tile count", things.size * things.size)
  edges = things.tiles[0].get_edges(Orientation.NO_FLIP, Rotation.NO_ROTATION)
  print(edges)
  edges = things.tiles[0].get_edges(Orientation.NO_FLIP, Rotation.ROT_90)
  print(edges)
  edges = things.tiles[0].get_edges(Orientation.NO_FLIP, Rotation.ROT_180)
  print(edges)
  edges = things.tiles[0].get_edges(Orientation.NO_FLIP, Rotation.ROT_270)
  print(edges)
  print()
  print("unique edges", len(things.unique_edges()))
  print()

  Rotation.test()
  Orientation.test()

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
