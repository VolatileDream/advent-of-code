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

  def name(self):
    # short name
    if self == Rotation.NO_ROTATION:
      return "  0*"
    elif self == Rotation.ROT_90:
      return " 90*"
    elif self == Rotation.ROT_180:
      return "180*"
    else:
      return "270*"

  def transform_point(self, p):
    if self == Rotation.NO_ROTATION:
      return p

    x, y = p
    if self == Rotation.ROT_180:
      x, y = (-x, -y)
    elif self == Rotation.ROT_90:
      x, y = (-y, x)
    else:
      x, y = (y, -x)

    return Position(x, y)

  @staticmethod
  def test():
    p = Position(2, 1)
    assert Rotation.NO_ROTATION.transform_point(p) == p
    assert Rotation.ROT_90.transform_point(p) == Position(-1, 2)
    assert Rotation.ROT_180.transform_point(p) == Position(-2, -1)
    assert Rotation.ROT_270.transform_point(p) == Position(1, -2)


class Orientation(enum.IntFlag):
  NO_FLIP = 0
  HORIZONTAL_FLIP = 1

  def name(self):
    if self == Orientation.NO_FLIP:
      return " "
    else:
      return "f"

  def transform_point(self, p):
    if self == Orientation.NO_FLIP:
      return p

    x, y = p
    if bool(Orientation.HORIZONTAL_FLIP & self):
      y = -y

    return Position(x, y)

  @staticmethod
  def test():
    p = Position(1, 2)
    assert Orientation.NO_FLIP.transform_point(p) == p
    assert Orientation.HORIZONTAL_FLIP.transform_point(p) == Position(1, -2)


class Spot(enum.IntEnum):
  TOP = 0
  RIGHT = 1
  BOTTOM = 2
  LEFT = 3


class Position(typing.NamedTuple):
  x: int
  y: int

  def adjacent(self):
    yield Position(self.x, self.y + 1)
    yield Position(self.x, self.y - 1)
    yield Position(self.x + 1, self.y)
    yield Position(self.x - 1, self.y)

  def transform(self, o=Orientation.NO_FLIP, r=Rotation.NO_ROTATION):
    return r.transform_point(o.transform_point(self))


class Tile:
  @staticmethod
  def from_lines(lines):
    name = int(lines[0].split(" ")[1].strip(":"))
    spots = set()
    values = {}
    for y, line in enumerate(lines[1:]):
      for x, c in enumerate(line):
        if c != '.':
          spots.add(Position(x, y))
        values[Position(x, y)] = c

    return Tile(name, spots, len(lines[1]), values)

  @staticmethod
  def test():
    lines = [
      "Tile 3:",
      ".A.",
      "B.C",
      ".DE",
    ]
    expect_lines = [
      "Tile 3:",
      ".B.",
      "D.A",
      "EC.",
    ]
    t = Tile.from_lines(lines)
    #print("loaded", t)
    t = t.transform(Orientation.NO_FLIP, Rotation.ROT_90)
    #print("turned", t)
    expect = Tile.from_lines(expect_lines)
    #print("expect", expect)
    assert t.grid == expect.grid

  def __init__(self, name, grid, size, values=None):
    self.name = name
    self.grid = grid
    self.size = size

    self.values = values

    # cache for rotation / transformation of edges
    self.edges = self.__edge_cache()
    self.uedges = frozenset(self.__unique_edges())

  def __repr__(self):
    out = ["Tile {}:".format(self.name)]
    start = 0 #-self.size + 1
    for y in range(start, self.size):
      line = []
      for x in range(start, self.size):
        #if Position(x,y) in self.grid:
        #  line.append("#")
        if Position(x, y) in self.values:
          line.append(self.values[Position(x,y)])
        else:
          line.append(".")
        pass
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
   
    # reduce cache items that are equivalent.

    c2 = {}
    for key, value in cache.items():
      t = tuple(value)
      if t in c2:
        continue
      c2[t] = key
 
    return { key: value for value, key in c2.items() }

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
    for o, r in self.edges.keys():
      matches = functools.reduce(lambda a,b: a and b,
                                 map(lambda t: t[0](t[1]),
                                     zip(matchers, self.get_edges(o, r))),
                                 True)
      if matches:
        possible_matches.append((o, r))
    return possible_matches

  def get_edges(self, orientation, rotation):
    return self.edges[(orientation, rotation)]

  def transform(self, o=Orientation.NO_FLIP, r=Rotation.NO_ROTATION):
    #print("transform", o, r)
    new = set()
    new_values = {}
    tl_x, tl_y = any_item(self.grid).transform(o, r)
    for old_point in self.grid:
      new_point = old_point.transform(o, r)
      #print("transform", old_point, self.values[old_point], "=>", new_point)
      tl_x = min(tl_x, new_point.x)
      tl_y = min(tl_y, new_point.y)
      new.add(new_point)
      new_values[new_point] = self.values[old_point]
    # Translate
    #print("translation", -tl_x, -tl_y)
    new = set([Position(p.x - tl_x, p.y - tl_y) for p in new])
    new_values = { Position(p.x - tl_x, p.y - tl_y): v for p, v in new_values.items() }
    #print("new grid", new)
    #print("new values", new_values)
    return Tile(self.name, new, self.size, new_values)

  def chop(self, orientation, rotation, cut=1):
    #print("chop", self.name, orientation, rotation)
    #print("before:", self)

    t = self.transform(orientation, rotation)

    #return Tile(t.name, t.grid, t.size + 1, t.values)

    #print("after", t)

    end = self.size - 1 - cut

    chopped = set()
    chopped_values = {}
    for point in t.grid:
      x, y = point
      if x < cut or end < x or y < cut or end < y:
        continue

      chopped.add(Position(x - cut, y - cut))
      chopped_values[Position(x - cut, y - cut)] = t.values[point]
      #chopped.add(Position(x, y))

    after = Tile(t.name, chopped, t.size - cut * 2, chopped_values)
    #print("chopped", after)
    return after


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
        assert len(index[e]) <= 2, "found edge shared with more than two tiles {}".format(e)

    return index

  def unique_edges(self):
    edges = set()
    for t in self.tiles:
      edges.update(t.unique_edges())
    return edges

  def tile_count(self):
    return len(self.tiles)

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
        index, o, r = placement[Position(x, y)]
        parts = [
          str(self.tiles[index].name),
          o.name(),
          r.name()
        ] 
        line.append(" ".join(parts))
      out.append(", ".join(line))
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

  def find_placement(self):
    # dict of Position(x, y) => (Tile index, Orientation, Rotation)
    placement = {}
    # set of (Position(x, y), index, Orientation, Rotation)
    tried = set()
    # set of indicies used already
    used = set()
    return self.__m(tried, used, placement, Position(0, 0))

  def convert_to_image(self, placement):
    # index => Tile
    chopped_tiles = {index : self.tiles[index].chop(o, r) for (index, o, r) in placement.values()}
    tile_side_len = any_item(chopped_tiles.values()).size

    position_index = {}
    for position in placement:
      position_index[position] = placement[position][0]

    joined_grid = set()
    joined_values = {}
    for y in range(self.size):
      for x in range(self.size):
        p = Position(x, y)

        tile = chopped_tiles[position_index[p]]
        
        for coord in tile.grid:
          x_offset, y_offset = coord
          joined_pos = Position(x * tile_side_len + x_offset, y * tile_side_len + y_offset)
          joined_grid.add(joined_pos)
          joined_values[joined_pos] = tile.values[coord]

        pass

    return Tile('all', joined_grid, self.size * tile_side_len, joined_values)
    pass


def product(args):
  p = 1
  for a in args:
    p *= a
  return p


def part1(things):
  grid, placement = things
  print(grid.print_placement(placement))
  print()

  return product([grid.tiles[placement[p][0]].name for p in grid.corners()])


SEAMONSTER = None
def seamonster():
  global SEAMONSTER
  if SEAMONSTER is not None:
    return SEAMONSTER

  seamonster = set()
  lines = [
    "                  # ",
    "#    ##    ##    ###",
    " #  #  #  #  #  #   ",
  ]
  for y, line in enumerate(lines):
    for x, c in enumerate(line):
      if c == "#":
        seamonster.add(Position(x, y))

  SEAMONSTER = (seamonster, len(lines[0]), len(lines))
  return SEAMONSTER


def has_seamonster(tile):
  monster, mwidth, mheight = seamonster()

  for y in range(tile.size - mheight):
    for x in range(tile.size - mwidth):
      # x & y to create offset. when doing check.
      match = True
      for p in monster:
        offset_point = Position(p.x + x, p.y + y)
        if offset_point not in tile.grid:
          match = False
          break
      if match:
        return True


def remove_seamonsters(tile):
  monster, mwidth, mheight = seamonster()

  # create a copy because we're gonna edit.
  copy_grid = set(tile.grid)
  copy_value = dict(tile.values)

  # positions that were in a monster, and have been removed from the grid.
  # we have to check against these, 
  monster_grid = set()

  monster_count = 0

  for y in range(tile.size - mheight):
    for x in range(tile.size - mwidth):
      # x & y to create offset. when doing check.
      match = True
      for p in monster:
        offset_point = Position(p.x + x, p.y + y)
        if offset_point not in copy_grid and offset_point not in monster_grid:
          match = False
          break
      if match:
        monster_count += 1
        for p in monster:
          offset_point = Position(p.x + x, p.y + y)
          copy_grid.remove(offset_point)
          monster_grid.add(offset_point)
          copy_value[offset_point] = 'O'

  print("found", monster_count, "monsters")
  return Tile(tile.name, copy_grid, tile.size, copy_value)


def part2(things):
  grid, placement = things

  tile = grid.convert_to_image(placement)
  print(tile)

  for o in Orientation:
    for r in Rotation:
      t = tile.transform(o, r)
      if has_seamonster(t):
        print("found monster!")
        t = remove_seamonsters(t)
        print(t)
        return len(t.grid)

  pass


def main(filename):
  things = TileGrid.from_groups(load_groups(filename))
  #print(things.tiles[0])
  #print("tile count", things.size * things.size)
  for o in Orientation:
    for r in Rotation:
      #print("Orientation & Rotation", o, r)
      #print(things.tiles[0].transform(o, r))
      pass
  #print()
  print("unique edges", len(things.unique_edges()))

  things = (things, things.find_placement())
  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  Rotation.test()
  Orientation.test()
  Tile.test()

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
