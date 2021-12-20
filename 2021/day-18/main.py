#!/usr/bin/env python-mr

from collections import defaultdict
from math import ceil, floor
from typing import NamedTuple
from _.data.formatting.blocks import Block

class SN(NamedTuple):
  left: "SN"
  right: "SN"

  @staticmethod
  def parse(line):
    if isinstance(line, str):
      line = eval(line)
    elif isinstance(line, int):
      return line
    children = [SN.parse(l) for l in line]
    return SN(*children)

  def __str__(self):
    return f"({str(self.left)}, {str(self.right)})"

  def __add__(self, other):
    prev = SN(self, other)
    #print("adding", self, other, "=", prev)
    while True:
      exploded = prev.explode() # evals all explosions.
      split, act = exploded.split()
      #print("after split", act, split)
      prev = split

      if not act:
        # no splits!
        break


    return prev

  def add_right(self, val):
    if isinstance(self, int):
      return self + val
    else:
      return SN(self.left, SN.add_right(self.right, val))

  def add_left(self, val):
    if isinstance(self, int):
      return self + val
    return SN(SN.add_left(self.left, val), self.right)

  def explode(self, nesting=None):
    #print("exploding", nesting, self)
    if isinstance(self, int):
      return 0, 0, self, False

    if nesting is None:
      exploded = True
      while exploded:
        _l, _r, self, exploded = self.explode(0)
        #print("after explosion", self)
      return self

    elif nesting >= 4: # explode
      assert isinstance(self.left, int)
      assert isinstance(self.right, int)
      return self.left, self.right, 0, True

    else:
      l, r, replace, act = SN.explode(self.left, nesting + 1)
      if act:
        return l, 0, SN(replace, SN.add_left(self.right, r)), True

      l, r, replace, act = SN.explode(self.right, nesting + 1)
      if act:
        return 0, r, SN(SN.add_right(self.left, l), replace), True

      return 0, 0, self, False

    raise Exception("impl error")

  def split(self):
    if isinstance(self, int):
      if self >= 10:
        half = self / 2
        return SN(int(floor(half)), int(ceil(half))), True
      else:
        return self, False
    else:
      l, act = SN.split(self.left)
      if act:
        return SN(l, self.right), True

      r, act = SN.split(self.right)
      if act:
        return SN(self.left, r), True

    return self, False
      
  def magnitude(self):
    if isinstance(self, int):
      return self
    else:
      l = SN.magnitude(self.left)
      r = SN.magnitude(self.right)
      return l * 3 + r * 2


LOAD = "content"
def REWRITE(lines):
  return [SN.parse(l) for l in lines]


def PART1(inputs):
  for i in inputs:
    #print(i)
    pass

  s = inputs[0]
  #print(s)
  for i in inputs[1:]:
    s = s + i
    #print(s)

  return s.magnitude()


def PART2(inputs):
  largest_sum = 0
  for x in inputs:
    for y in inputs:
      if x == y:
        continue

      largest_sum = max(largest_sum, (x + y).magnitude())

  return largest_sum
