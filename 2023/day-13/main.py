#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

@dataclass
class Rocks:
  size: tuple
  vals: list
  # transposed values.
  tvals: list

  @staticmethod
  def parse(group):
    size = (len(group), len(group[0]),)
    vals = [0] * len(group)
    tvals = [0] * len(group[0])
    for row, l in enumerate(group):
      for col, v in enumerate(l):
        if v == "#":
          vals[row] = vals[row] | (1 << col)
          tvals[col] = tvals[col] | (1 << row)
    #print(size)
    return Rocks(size, vals, tvals)

  @staticmethod
  def pvals(size, vals):
    rows, cols = size
    lines = []
    for r in range(rows):
      line = ""
      for c in range(cols):
        if (vals[r] & (1 << c)) != 0:
          line += "#"
        else:
          line += "."
      lines.append(line)
    return "\n".join(lines)

  def __str__(self):
    return Rocks.pvals(self.size, self.vals)
    #return Rocks.pvals(self.size[::-1], self.tvals)

# for part 2
@dataclass
class RockPermuter:
  @staticmethod
  def permutations(rock):
    rows, cols = rock.size
    for idx in range(rows * cols):
      yield RockPermuter.__permute(rock, idx)

  @staticmethod
  def __permute(rock, n):
    rows, cols = rock.size
    if n > rows * cols:
      raise Exception(f"{n} > {rows * cols}")

    new = Rocks(rock.size, list(rock.vals), list(rock.tvals))
    r, c = divmod(n, cols)

    new.vals[r] = new.vals[r] ^ (1 << c)
    new.tvals[c] = new.tvals[c] ^ (1 << r)

    return new

LOAD = "groups"
def REWRITE(groups):
  out = []
  for g in groups:
    r = Rocks.parse(g)
    #print("\n".join(g))
    #print("r:")
    #print(r)
    #print()
    out.append(r)
  return out

def TEST(inputs):
  pass


def find_reflections(rocks: Rocks, horz):
  maxrows, maxcols = (0, 0)
  vals = None
  if horz:
    maxrows, maxcols = rocks.size
    vals = rocks.vals
  else:
    maxrows, maxcols = rocks.size[::-1]
    vals = rocks.tvals

  candidates = []
  for idx in range(1, maxrows):
    if vals[idx - 1] == vals[idx]:
      candidates.append(idx)
  #print(candidates)

  reflections = []
  for offset in candidates:
    found = True
    idx = 0
    while offset + idx < maxrows and offset - idx - 1 >= 0:
      if vals[offset - idx - 1] != vals[offset + idx]:
        found = False
        break
      idx += 1

    if found:
      reflections.append(offset)

  return reflections

def score1(rocks):
  h = find_reflections(rocks, True)
  v = find_reflections(rocks, False)
  s = 0
  if h:
    s += h[0] * 100
  if v:
    s += v[0] * 1
  return s

def score2(rocks: Rocks):
  h1 = set(find_reflections(rocks, True))
  v1 = set(find_reflections(rocks, False))
  perm = RockPermuter()

  for r in perm.permutations(rocks):
    h2 = set(find_reflections(r, True))
    v2 = set(find_reflections(r, False))

    h2.difference_update(h1)
    v2.difference_update(v1)
    if not h2 and not v2:
      continue

    # new reflection!
    # the question only has us find a __single__ new reflection.
    s = 0
    if h2:
      s += h2.pop() * 100
    if v2:
      s += v2.pop() * 1
    return s
    
  return 0
  

def PART1(inputs):
  #print(inputs)
  s = 0
  for r in inputs:
    #print(r)
    #h = find_reflections(r, True)
    #print(h)
    #print(Rocks.pvals(r.size[::-1], r.tvals))
    #v = find_reflections(r, False)
    #print(v)
    s += score1(r)

  return s

def PART2(inputs):
  s = 0
  for r in inputs:
    u = score2(r)
    #print(r, u)
    s += u
  return s
