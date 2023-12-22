#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass, field
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

class Pos3(NamedTuple):
  x: int
  y: int
  z: int

  def __str__(self):
    return f"({self.x},{self.y},{self.z})"

  @staticmethod
  def parse(line):
    return Pos3(*[int(i) for i in line.split(",")])

class Brick(NamedTuple):
  start: Pos3
  end: Pos3

  def xyfootprint(self):
    return abs(self.start.x - self.end.x) + abs(self.start.y - self.end.y) + 1

  def drop(self, z):
    zd = self.end.z - self.start.z
    return Brick(Pos3(self.start.x, self.start.y, z), Pos3(self.end.x, self.end.y, z + zd))

  def __len__(self):
    return abs(self.end.x - self.start.x) + abs(self.end.y - self.start.y) + abs(self.end.z - self.start.z) + 1

  def __str__(self):
    return f"{self.start}~{self.end}"

  @staticmethod
  def parse(line):
    s1, s2 = line.split("~")
    p1, p2 = Pos3.parse(s1), Pos3.parse(s2)
    # Important assertions.
    assert Brick.__two_same(p1, p2), f"{p1} and {p2} don't share 2 of the same coords."
    assert p1.x <= p2.x
    assert p1.y <= p2.y
    assert p1.z <= p2.z
    return Brick(p1, p2)

  @staticmethod
  def __two_same(p1, p2):
    c = 0
    if p1.x == p2.x:
      c += 1
    if p1.y == p2.y:
      c += 1
    if p1.z == p2.z:
      c += 1
    return c >= 2

@dataclass
class Mask:
  occupied: dict = field(default_factory=dict)

  def add(self, brick):
    for x in range(brick.start.x, brick.end.x + 1):
      for y in range(brick.start.y, brick.end.y + 1):
        self.occupied[(x, y)] = brick

  def intersect(self, brick: Brick) -> bool:
    assert type(brick) == Brick
    for x in range(brick.start.x, brick.end.x + 1):
      for y in range(brick.start.y, brick.end.y + 1):
        p = (x, y)
        if p in self.occupied:
          return True
    return False

  def getintersects(self, brick: Brick) -> bool:
    assert type(brick) == Brick
    hit = set()
    for x in range(brick.start.x, brick.end.x + 1):
      for y in range(brick.start.y, brick.end.y + 1):
        p = (x, y)
        if p in self.occupied:
          hit.add(self.occupied[p])
    return hit

def intersect(b1, b2):
  def i(b1, b2, attr):
    return ((getattr(b1.start, attr) <= getattr(b2.start, attr) and getattr(b2.start, attr) <= getattr(b1.end, attr))
        or (getattr(b2.start, attr) <= getattr(b1.start, attr) and getattr(b1.start, attr) <= getattr(b2.end, attr)))

  return i(b1, b2, "x") and i(b1, b2, "y") and i(b1, b2, "z")

LOAD = "content"
def REWRITE(lines):
  bricks = [Brick.parse(l) for l in lines]
  bricks.sort(key=lambda b: b.start.z)
  #for i, b1 in enumerate(bricks):
  #  for j, b2 in enumerate(bricks[i + 1:]):
  #    assert not intersect(b1, b2), f"starting positions intersect: {b1} > {b2}"
  #print(len(bricks))
  return bricks

def drop_bricks(bricks):
  minX = min(map(lambda b: b.end.x, bricks))
  minY = min(map(lambda b: b.end.y, bricks))
  maxX = max(map(lambda b: b.end.x, bricks))
  maxY = max(map(lambda b: b.end.y, bricks))
  #print(minX, maxX)
  #print(minY, maxY)

  # We want to create a mask for each Z index to quickly check intersect.
  FLOOR_GUARD = object()
  floor = Mask({(x, y): FLOOR_GUARD for x in range(minX, maxX + 1) for y in range(minY, maxY + 1)})

  masks = defaultdict(Mask)
  masks[0] = floor
  highestZ = 0

  # list of bricks with updated positions.
  done = []

  # index of parent bricks
  parents = {}
  children = defaultdict(set)

  while bricks:
    dropped = bricks.pop(0)

    # Bricks auto drop to one above the highest Z we've ever dropped.
    currZ = highestZ + 1
    while not masks[currZ].intersect(dropped):
      currZ -= 1

    # There is an intersect here.
    hit = masks[currZ].getintersects(dropped)
    fell = dropped.drop(currZ + 1)
    done.append(fell)
    highestZ = max(highestZ, fell.end.z)

    for z in range(fell.start.z, fell.end.z + 1):
      masks[z].add(fell)

    parents[fell] = hit
    for parent in hit:
      children[parent].add(fell)

  print("all bricks dropped")
  return (done, parents, children)

def TEST(inputs):
  pass

def PART1(inputs):
  #print("".join([str(b) for b in inputs]))
  bricks = list(inputs)

  done, parents, children = drop_bricks(bricks)

  s = 0
  for brick in done:
    safe = True
    for c in children[brick]:
      if len(parents[c]) == 1:
        safe = False
        break
    if safe:
      s += 1
  return s


def chain_drop(brick, parents, children):
  # small hack to handle the brick case.
  falling = set([brick])
  seen = set()

  processing = set()
  processing.add(brick)

  # BFS feels like overkill, but we have to handle an entire
  # z layer before moving on to the next one.

  process = [brick]
  while process:
    candidate = process.pop(0)
    processing.remove(candidate)
    seen.add(candidate)

    cParents = parents[candidate]
    if candidate not in falling and not falling.issuperset(cParents):
      continue

    falling.add(candidate)

    cChildren = children[candidate]
    sort = False
    for c in cChildren:
      if c in seen:
        continue
      if c not in processing:
        processing.add(c)
        process.append(c)
        sort = True
    if sort:
      process.sort(key=lambda b: b.end.z)

  # Undo the hack from above.
  falling.remove(brick)
  return falling

def PART2(inputs):
  bricks = list(inputs)
  done, parents, children = drop_bricks(bricks)

  drops = [chain_drop(brick, parents, children) for brick in done]
  # Attempt 1: 1249 - too low
  # misread question, sum of drops, not biggest drop.
  # Attempt 2: 67468 - correct
  return sum(map(len, drops))
