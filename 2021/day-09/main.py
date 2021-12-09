#!/usr/bin/env python-mr

from collections import defaultdict
from _.data.formatting.blocks import Block

LOAD = "content"
def REWRITE(lines):
  heights = {}
  for row, line in enumerate(lines):
    for col, value in enumerate(line):
      p = (row, col)
      heights[p] = int(value)

  return heights


def neighbours(point):
  row, col = point
  yield (row - 1, col)
  yield (row + 1, col)
  yield (row, col - 1)
  yield (row, col + 1)


def lower_than_neighbours(heights):
  # Return points that are lower than all their neighbours.
  candidates = set(heights.keys())
  lower = set()
  while candidates:
    check = candidates.pop()
    height = heights[check]

    ok = True
    for n in neighbours(check):
      nh = heights.get(n, 10)
      if height < nh:
        # Optimize, don't look at our neighbour.
        candidates.discard(n)
      else:
        ok = False
        break

    if ok:
      lower.add(check)

  return lower


def risk(heights, p):
  return heights.get(p, 10) + 1


def PART1(inputs):
  lower = lower_than_neighbours(inputs)
  print(inputs)
  print(lower)
  return sum([risk(inputs, l) for l in lower])


def basins(heights):
  # Basins are delimited by height=9 items.
  # Do breadth first search to find basins.
  b = defaultdict(list)
  remaining = set(heights.keys())
  dividers = set() # edge points or height = 9
  seen = set()
  
  while remaining:
    check = remaining.pop()
    seen.add(check)

    height = heights[check]
    if height == 9:
      dividers.add(check)
      continue

    # Start a new basin.
    basin = set([check])
    ns = set([n for n in neighbours(check) if n in heights])
    while ns:
      n = ns.pop()
      # point has been considered as part of a basin.
      seen.add(n)
      remaining.discard(n)

      #print("basins", "check", n)
      nh = heights[n]
      if nh == 9:
        # Height of 9 is a basin edge.
        dividers.add(n)
      elif nh < 9:
        basin.add(n)
        for a in neighbours(n):
          if a not in seen and a in heights:
            ns.add(a)

    b[len(basin)].append(basin)

  return b

def PART2(inputs):
  bs = basins(inputs)
  #print(bs)
  sizes = list(bs.keys())
  sizes.sort(reverse=True)

  top3ish = []
  for s in sizes[0:3]:
    top3ish.extend(bs[s])

  #print(top3ish)
  assert len(top3ish) >= 3
  one, two, three, *rest = top3ish
  return len(one) * len(two) * len(three)
  
