#!/usr/bin/python3

import argparse
import collections
import enum
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


class HexMove(enum.Enum):
  EAST = enum.auto()
  SOUTH_EAST = enum.auto()
  SOUTH_WEST = enum.auto()
  WEST = enum.auto()
  NORTH_WEST = enum.auto()
  NORTH_EAST = enum.auto()

  @staticmethod
  def gen_from_iterable(iterator):
    if iterator.__iter__:
      # assume it's an iterable, not an iterator
      iterator = iter(iterator)
    while True:
      # from iterable will raise StopIteration for us.
      try:
        yield HexMove.from_iterable(iterator)
      except StopIteration:
        return

  @staticmethod
  def from_iterable(iterator):
    n = next(iterator)

    # east and west can be matched greedily
    if n == "e":
      return HexMove.EAST
    elif n == "w":
      return HexMove.WEST

    # need a second bit
    n = n + next(iterator)
    if n == "ne":
      return HexMove.NORTH_EAST
    elif n == "nw":
      return HexMove.NORTH_WEST
    elif n == "se":
      return HexMove.SOUTH_EAST
    elif n == "sw":
      return HexMove.SOUTH_WEST
    else:
      raise Exception("Bad HexMove string {}".format(n))


class HexGridPosition(typing.NamedTuple):
  x: int
  y: int
  z: int

  # Can also be represented as (which is less of a pain):
  #  (Also called Axial Representation)
  #
  #                  -2  -1   0   1   2   y=2
  #    nw ne       -2  -1   0   1   2     y=1
  #   w  -  e  =>    -1   0   1   2   3   y=0
  #    sw se       -1   0   1   2   3     y=-1
  #                   0   1   2   3   3   y=-2
  # Which becomes:
  #                 -2  -1   0   1   2    y=2
  #   nw  ne   -    -2  -1   0   1   2    y=1
  #    w   -   e => -2  -1   0   1   2    y=0
  #    -  sw  se    -2  -1   0   1   2    y=-1
  #                 -2  -1   0   1   2    y=-2

  @staticmethod
  def zero():
    return HexGridPosition(0,0,0)

  @staticmethod
  def test():
    # test that some moves are equivalent.
    ms = HexMove.gen_from_iterable("esew")
    h = HexGridPosition.zero()
    assert h.moves(ms) == h.move(HexMove.SOUTH_EAST)
    # loop around the entire start position.
    ms = HexMove.gen_from_iterable("eeswswwwnwnwnenesese")
    h = HexGridPosition.zero()
    assert h.moves(ms) == h

  __MOVES__ = None

  @staticmethod
  def deltas():
    if HexGridPosition.__MOVES__ is None:
      HexGridPosition.__MOVES__ = {
        # Cube Coordinates
        #HexMove.EAST: HexGridPosition(+1, -1, 0),
        #HexMove.WEST: HexGridPosition(-1, +1, 0),
        #HexMove.NORTH_EAST: HexGridPosition(+1, 0,-1),
        #HexMove.SOUTH_WEST: HexGridPosition(-1, 0,+1),
        #HexMove.NORTH_WEST: HexGridPosition( 0,+1,-1),
        #HexMove.SOUTH_EAST: HexGridPosition( 0,-1,+1),

        # Axial Coordinates
        HexMove.EAST: HexGridPosition(+1, 0, 0),
        HexMove.WEST: HexGridPosition(-1, 0, 0),
        HexMove.NORTH_EAST: HexGridPosition( 0,+1, 0),
        HexMove.SOUTH_WEST: HexGridPosition( 0,-1, 0),
        HexMove.NORTH_WEST: HexGridPosition(-1,+1, 0),
        HexMove.SOUTH_EAST: HexGridPosition(+1,-1, 0),
      }
    return HexGridPosition.__MOVES__

  def __add__(self, other):
    return HexGridPosition(self.x + other.x, self.y + other.y, self.z + other.z)

  def move(self, m):
    return self + HexGridPosition.deltas()[m]

  def moves(self, ms):
    n = self
    for m in ms:
      n = n.move(m)
    return n


class Grid:
  def __init__(self, pos=None):
    # Position of all the black tiles
    self.positions = set()
    if pos is not None:
      self.positions.update(pos)

  def copy(self):
    return Grid(self.positions)

  def life(self, rounds=1):
    n = self
    for _ in range(rounds):
      n = n.__life_round()
    return n

  def __life_round(self):
    alive = collections.defaultdict(int)
    for p in self.positions:
      # See the two update loops below for the explanation of this.
      # alive[p] += 0
      for d in HexGridPosition.deltas().values():
        alive[p + d] += 1

    # full update
    next_state = Grid()
    for point, count in alive.items():
      prev = point in self.positions
      if (prev and count == 1) or count == 2:
        # next state is empty, so this always sets the tile.
        next_state.flip(point)

    # run the incremental update & asserts.
    if False:
      # turns out that the incremental update is subtly broken:
      # incremental updates won't iterate through points that had no active neighbours.
      # and if these points were black tiles, then they should be flipped. uh oh.
      # there's a 'alive[p] += 0' line above that fixes this error.

      # semi-incremental update
      updated = self.copy()
      for point, count in alive.items():
        prev = point in self.positions
        flip = (prev and (count == 0 or count > 2)) or (not prev and count == 2)
        if flip:
          updated.flip(point)

      # The two blocks above are 
      joined = set()
      joined.update(updated.positions)
      joined.update(next_state.positions)
      for point in joined:
        assert (point in updated.positions) == (point in next_state.positions), "Point differs: {}".format(point)

    return next_state

  def flip(self, coord):
    if coord in self.positions:
      self.positions.remove(coord)
    else:
      self.positions.add(coord)


def part1(things):
  g = Grid()
  for moves in things:
    h = HexGridPosition.zero()
    g.flip(h.moves(moves))

  return len(g.positions)

def part2(things):
  # Setup (part 1)
  g = Grid()
  for moves in things:
    h = HexGridPosition.zero()
    g.flip(h.moves(moves))

  asserts = []
  #asserts = [15, 12, 25, 14]

  print("Starting:", len(g.positions))
  #print(g.positions)
  for i in range(100):
    g = g.life()
    #print(g.positions)
      
    #print("After day", i + 1, ":", len(g.positions))

  return len(g.positions)


def main(filename):
  things = [list(HexMove.gen_from_iterable(line)) for line in load_file(filename)]
  #print(things)

  HexGridPosition.test()

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
