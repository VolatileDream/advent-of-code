#!/usr/bin/env python-mr

from collections import defaultdict
from typing import NamedTuple
from _.data.formatting.blocks import Block

class Pos(NamedTuple):
  x: int
  y: int


class EnhancementArray:
  @staticmethod
  def parse(string):
    values = [int(c == "#") for c in string]
    values.reverse()
    bigint = 0
    for v in values:
      bigint <<= 1
      bigint += v

    ea = EnhancementArray(bigint)
    # Check that all off and all on cause the image to flash.
    # THIS IS NOT TRUE FOR THE TEST CASE PROVIDED.
    #assert ea[0] == 1
    #assert ea[0x1FF] == 0

    return ea

  def __str__(self):
    chars = {
      True: "#",
      False: ".",
    }
    return "".join([chars[bool(self._bigint & (1 << i))] for i in range(512)])

  def __init__(self, bigint):
    self._bigint = bigint

  def __getitem__(self, key):
    return (self._bigint & (1 << key)) > 0


class ImageGrid(NamedTuple):
  on: set[Pos]
  rangex: range
  rangey: range
  outside: bool

  @staticmethod
  def parse(lines):
    pos = set()
    for row, line in enumerate(lines):
      #print(line)
      for col, v in enumerate(line):
        if v == "#":
          pos.add(Pos(col, row))

    ig = ImageGrid(pos, range(0, row + 1), range(0, col + 1), False)
    #print(ig)
    return ig

  def __str__(self):
    chars = {
      True: "#",
      False: ".",
    }
    rx, ry = self.increment_range(2)
    out = []
    for y in ry:
      row = []
      for x in rx:
        p = Pos(x, y)
        if self.inside_border(p):
          row.append(chars[p in self.on])
        else:
          #row.append(" ")
          row.append(chars[self.outside])
      out.append("".join(row))
    return "\n".join(out)

  def increment_range(self, by=1):
    return (range(self.rangex.start - by, self.rangex.stop + by),
            range(self.rangey.start - by, self.rangey.stop + by))

  def neighbours(self, pos):
    x, y = pos
    yield Pos(x - 1, y - 1)
    yield Pos(x, y - 1)
    yield Pos(x + 1, y - 1)

    yield Pos(x - 1, y)
    yield Pos(x, y)
    yield Pos(x + 1, y)

    yield Pos(x - 1, y + 1)
    yield Pos(x, y + 1)
    yield Pos(x + 1, y + 1)

  def idx(self, pos):
    i = 0
    for n in self.neighbours(pos):
      i <<= 1
      if self.inside_border(n):
        i |= int(n in self.on)
      else:
        i |= int(self.outside)
    return i

  def inside_border(self, pos):
    x, y = pos
    return x in self.rangex and y in self.rangey


def update(ig: ImageGrid, ea: EnhancementArray):
  enhanced = set()

  rx, ry = ig.increment_range()
  for y in ry:
    for x in rx:
      pixel = Pos(x, y)
      eindex = ig.idx(pixel)
      if ea[eindex]:
        enhanced.add(pixel)

  if ig.outside:
    o = ea[0x1FF]
  else:
    o = ea[0x0]
  return ImageGrid(enhanced, rx, ry, o)
    

LOAD = "groups"
def REWRITE(lines):
  ea, ig = lines
  return (EnhancementArray.parse(ea[0]), ImageGrid.parse(ig))


def PART1(inputs):
  ea, ig = inputs
  #print(ea)
  print(ig)
  #print("index", bin(ig.idx(Pos(2, 2))))
  print()

  newig = update(ig, ea)
  print(newig)
  print()
  newig = update(newig, ea)
  print(newig)
  print()

  return len(newig.on)

def PART2(inputs):
  ea, ig = inputs
  for i in range(50):
    ig = update(ig, ea)

  return len(ig.on)
