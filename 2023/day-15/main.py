#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

LOAD = "content"
def REWRITE(lines):
  return lines[0].split(",")

def TEST(inputs):
  pass

def hashfn(s):
  h = 0
  for c in s:
    h += ord(c)
    h *= 17
    h %= 256
  return h

def PART1(inputs):
  #print(inputs)

  s = 0
  for i in inputs:
    h = hashfn(i)
    #print(i, h)
    s += h

  return s

def PART2(inputs):
  boxes = [list() for _ in range(256)]

  labelval = {}

  for i in inputs:
    if "=" in i:
      label, val = i.split("=")
      if label in labelval:
        labelval[label] = val
      else:
        
        boxes[hashfn(label)].append(label)
        labelval[label] = val

    else:
      label = i.rstrip("-")
      if label not in labelval:
        continue

      del labelval[label]
      boxes[hashfn(label)].remove(label)

  power = 0
  for boxn, b in enumerate(boxes):
    for idx, lense in enumerate(b):
      power += (boxn + 1) * (idx + 1) * int(labelval[lense])

  return power
