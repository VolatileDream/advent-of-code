#!/usr/bin/env python-mr

from collections import defaultdict
from typing import NamedTuple
from _.data.formatting.blocks import Block


def within(start, stop, value):
  return start <= value and value < stop


def overlap(r1, r2):
  if len(r2) > len(r1):
    r1, r2 = r2, r1
  return (within(r1.start, r1.stop, r2.start) or
          within(r1.start, r1.stop, r2.stop - 1) or
          within(r2.start, r2.stop, r1.start) or
          within(r2.start, r2.stop, r1.stop - 1))


def merge(r1, r2):
  return range(min(r1.start, r2.start), max(r1.start, r2.start))


class Update(NamedTuple):
  state: bool
  xs: range
  ys: range
  zs: range

  @staticmethod
  def pr(r):
    start, end = r.split("..")
    # Parsed ranges are INCLUSIVE.
    return range(int(start), int(end) + 1)

  @staticmethod
  def parse(line):
    state, ranges = line.replace("x=", "").replace("y=", "").replace("z=", "").split(" ")
    x, y, z = ranges.split(",")
    return Update(state == "on", Update.pr(x), Update.pr(y), Update.pr(z))

  def overlap(self, o):
    return overlap(self.xs, o.xs) and overlap(self.ys, o.ys) and overlap(self.zs, o.zs)

  def volume(self):
    return len(self.xs) * len(self.ys) * len(self.zs)


LOAD = "content"
def REWRITE(lines):
  return [Update.parse(l) for l in lines]


def PART1(inputs):
  #print(inputs)
  small_region = Update(True, range(-50, 51), range(-50, 51), range(-50, 51))
  for i in inputs:
    #print(i.overlap(small_region), i)
    pass
  small = list(filter(lambda u: u.overlap(small_region), inputs))
  #print(small)

  # Horrible brute force. Had not yet thought of a better way to do it.
  grid = set()
  for s in small:
    for x in s.xs:
      for y in s.ys:
        for z in s.zs:
          p = (x,y,z)
          if s.state:
            grid.add(p)
          else:
            grid.discard(p)

  return len(grid)


def find_intersect(prism1, prism2):
  if not prism1.overlap(prism2):
    return None

  def nr(r1, r2):
    return range(max(r1.start, r2.start), min(r1.stop, r2.stop))

  direction = prism1.state ^ prism2.state
  return Update(direction,
                nr(prism1.xs, prism2.xs),
                nr(prism1.ys, prism2.ys),
                nr(prism1.zs, prism2.zs))


def compute_volume_change(prism, others):
  #print("cvc", prism)
  # For the prism & the others we need to compute the intersection regions.
  intersections = []
  for o in others:
    i = find_intersect(prism, o)
    if i:
      intersections.append(i)

  # Given all the intersections, we need to compute the volume change.
  # And also check if those regions intersect themselves...

  # Gotta handle intersections of intersections...
  return find_volume_set(intersections, True)


def find_volume_set(prisms, compute_all=False):
  #print("find_volume_set")
  operations = {index: i for index, i in enumerate(prisms)}

  # key is intersected by some part of values.
  affected_by = defaultdict(set)
  for i in range(len(prisms)):
    op = operations[i]
    for j in range(i):
      other = operations[j]
      if op.overlap(other):
        affected_by[j].add(i)

  # From the affects map we can see there's a lot of overlap, but we don't actually
  # care about overlapping, just the count of the number of things turned on.

  # TODO:
  # It took a while to figure out that we want to go backwards. It makes handling
  # removals much simpler, as we only care about adding new points, and when going
  # backwards a removal or addition look the same in terms of new added points.

  volume = 0
  for index, operation in enumerate(prisms):
    intersects = [operations[a] for a in affected_by[index]]

    if operation.state or compute_all:
      volume += operation.volume()
      # Because we're going backwards, then the volumes that have already been added
      # all become equivalent "don't count that" space.
      volume -= compute_volume_change(operation, intersects)

  #print("found_volume_set", volume)
  return volume


def PART2(inputs):
  #small_region = Update(True, range(-50, 51), range(-50, 51), range(-50, 51))
  #for i in inputs:
    #print(i.overlap(small_region), i)
    #pass
  #small = list(filter(lambda u: u.overlap(small_region), inputs))
  return find_volume_set(inputs)
