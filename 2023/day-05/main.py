#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from itertools import islice, pairwise
from typing import NamedTuple
from _.data.formatting.blocks import Block

@dataclass
class Range:
  dst: int
  src: int
  len: int

  @staticmethod
  def parse(line):
    d, s, l = [int(i) for i in line.split(" ")]
    return Range(d, s, l)

  def __contains__(self, i):
    return self.src <= i and i < self.src + self.len

  def map(self, i):
    if i not in self:
      raise Exception(f"can't map value not contained in Range: {i}")
    o = (i - self.src) + self.dst
    #print("map", i, self.delta(), "=", o)
    return o

  def delta(self):
    # assumes that the number falls in the source range.
    return self.dst - self.src

  def intersect(self, other):
    start = self.src
    end = self.src + self.len
    ostart = other.src
    oend = other.src + other.len
    return ((ostart <= start and start < oend) or
            (ostart < end and end < oend))


@dataclass
class ThingMap:
  src_type: str
  dst_type: str

  mappings: list # list[]

  @staticmethod
  def parse(group):
    src, dst = group[0].removesuffix(" map:").split("-to-")
    rs = [Range.parse(l) for l in group[1:]]
    rs.sort(key=lambda x: x.src)
    return ThingMap(src, dst, rs)

  def __contains__(self, i):
    for r in self.mappings:
      if i in r:
        return True
    return False

  def map(self, i):
    for idx, m in enumerate(self.mappings):
      if i in m:
        return m.map(i)
    return i

  def breakpoints(self):
    breaks = set()
    for r in self.mappings:
      breaks.add(r.src)
      breaks.add(r.src + r.len)
      breaks.add(r.dst)
      breaks.add(r.dst + r.len)
    breaks = list(breaks)
    breaks.sort()
    return breaks

  def mapr(self, range):
    # Map a range forward. It should never get split!
    #print("mapr", "range", range)
    #print("mapr", "maps", self.mappings)
    for m in self.mappings:
      #print("mapr", m, m.delta())
      if range.src + range.len < m.src:
        #print("smaller")
        return range

      if range.src >= m.src and range.src + range.len <= m.src + m.len:
        d = m.delta()
        #print(d)
        return Range(range.src + d, range.src + d, range.len)

    last = self.mappings[-1]
    assert last.src + last.len <= range.src, f"{last.src + last.len} <= {range.src}"
    return range


def overlapping_map_ranges(maps):
  for m in maps:
    for i, r1 in enumerate(m.mappings):
      for j, r2 in enumerate(m.mappings[i+1:]):
        if r1.intersect(r2):
          return True
  return False


def check_contiguous(maps):
  for m in maps:
    l = list(m.mappings)
    l.sort(key=lambda x: x.dst)
    for i, r in enumerate(l[:-1]):
      if r.dst + r.len != l[i + 1].dst:
        return False
    l.sort(key=lambda x: x.src)
    for i, r in enumerate(l[:-1]):
      if r.src + r.len != l[i + 1].src:
        return False

  return True
    

LOAD = "groups"
def REWRITE(groups):
  _, seeds = groups[0][0].split(": ")
  seeds = [int(s) for s in seeds.split(" ")]
  maps = []
  for g in groups[1:]:
    maps.append(ThingMap.parse(g))

  if overlapping_map_ranges(maps):
    raise Exception("overlapping ranges!")

  print("contiguous:", check_contiguous(maps))
  rules = 0
  for m in maps:
    print(">", m.src_type, m.dst_type)
    rules += len(m.mappings)
  print("layers:", len(maps), "rules:", rules)

  # find all the breakpoints (start of the range) for each mapping layer.
  breaks = set()
  breaks.update(seeds)
  for m in maps:
    breaks.update(m.breakpoints())

  # Convert to list to ensure stable ordering.
  breaks = list(breaks)
  breaks.sort()
  print("breaks:", breaks, "length:", len(breaks))
  print("min delta", min(map(lambda t: t[1] - t[0], pairwise(breaks))))

  # Hard coded answer to part1
  #seeds = [141010855, 1]
  return (seeds, maps)


def find_map(name, maps):
  for m in maps:
    if m.src_type == name:
      return m
  raise Exception(f"no map with name {name}")

def convert_to(items, start, end, maps):
  if start == end:
    return items

  current = start
  while current != end:
    #print(current)
    nextmap = find_map(current, maps)
    nextitems = [nextmap.map(i) for i in items]
    current = nextmap.dst_type
    items = nextitems

  return items


def PART1(inputs):
  seeds, maps = inputs
  #print(seeds)
  #print(maps)
  ends = []
  for s in seeds:
    end = convert_to([s], "seed", "location", maps)
    ends.extend(end)
    print(s, "=>", end[0])
  return min(ends)


def seed_range(iterable):
  it = iter(iterable)
  while True:
    try:
      start = next(it)
    except StopIteration:
      return
    length = next(it)
    yield Range(start, start, length)


def split_range(range, breaks):
  for start in breaks:
    if range.len == 0:
      return
    if range.src > start:
      continue

    if range.src + range.len < start:
      yield range
      return

    if start != range.src:
      yield Range(range.src, range.src, start - range.src)
    range = Range(start, start, range.src + range.len - start)

  if range.len != 0:
    yield range


def PART2(inputs):
  seeds, maps = inputs
  seeds = list(seed_range(seeds))
  #print("seeds:", " ".join([f"{s.src} {s.len}" for s in seeds]))
  print("seeds:", seeds, "amount:", sum([s.len for s in seeds]))
  seeds = ThingMap("seed", "seed", seeds)
  #print(maps)

  # For part two there's waaaaaaaay too many seeds to go forward one at a time.
  # So instead we built up ThingMap.mapr and split_range to map an entire range
  # through a mapping layer. This is much much faster.

  seed_ranges = list(seeds.mappings)
  for layer in maps:
    # Some of the code was resorting this list... :|
    # And it broke my code for a long time...
    #layer.mappings.sort(key=lambda r: r.src)
    print("layer:", layer.src_type, layer.dst_type)
    breaks = layer.breakpoints()
    # Sorting the ranges only necessary for display.
    #seed_ranges.sort(key=lambda r: r.src)
    #print("breaks", breaks)
    #print("ranges", [(s.src, s.src + s.len - 1) for s in seed_ranges])
    new_ranges = []
    for r in seed_ranges:
      #print("processing", r)
      split = split_range(r, breaks)
      #print(split)
      for s in split:
        mapped = layer.mapr(s)
        #print(" ", s, "=>", mapped)
        new_ranges.append(mapped)
        pass

    seed_ranges = new_ranges

  seed_ranges.sort(key=lambda r: r.src)
  #print("done", [(s.src, s.src + s.len - 1) for s in seed_ranges])

  return seed_ranges[0].src
