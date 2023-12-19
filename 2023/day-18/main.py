#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from itertools import pairwise
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.data.structures.point import Point
from _.games.advent_of_code.utils import read_numbers

import math

## From day 10:
DRAW = {
  "│": [(-1, 0), (+1, 0)],
  "─": [(0, -1), (0, +1)],
  "╰": [(-1, 0), (0, +1)],
  "╯": [(-1, 0), (0, -1)],
  "╮": [(+1, 0), (0, -1)],
  "╭": [(+1, 0), (0, +1)],
}
def con_char(pos, adjs):
  row, col = pos
  for char in DRAW:
    found = True
    for (r, c) in DRAW[char]:
      if (row + r, col + c) not in adjs:
        found = False
        break
    if found:
      #print("con_char", char)
      return char

  assert False, f"no found char for {pos} with {adjs}"

def printgraph(graph, minp, maxp, inside=set()):
  for row in range(minp.x, maxp.x + 1):
    line = ""
    for col in range(minp.y, maxp.y + 1):
      p = (row, col)
      if p in graph:
        #line += "\033[31m" + con_char(p, graph[p]) + "\033[39;49m"
        line += con_char(p, graph)
      elif p in inside:
        line += "."
      else:
        line += " "
    print(line)

def find_area_inside(graph, minp, maxp):
  switches = {
    "╭": "╯", "╰": "╮",
  }
  count = 0
  positionsinloop = set()
  for row in range(minp.x, maxp.x + 1):
    inloop = False
    start = None
    for col in range(minp.y, maxp.y + 1):
      p = (row, col)
      if p not in graph:
        if inloop:
          count += 1
          positionsinloop.add(p)
        continue

      char = con_char(p, graph)
      if char == "─":
        continue
      elif char == "│":
        inloop = not inloop
        continue

      if start is None:
        start = char
      else:
        if switches[start] == char:
          inloop = not inloop
        start = None

  return (count, positionsinloop)
## No longer day 10

DIRECTIONS = {
  # Row, column - (0,0) in the top-left.
  "UP": Point(-1, 0),
  "U": Point(-1, 0),
  "3": Point(-1, 0),
  "DOWN": Point(+1, 0),
  "D": Point(+1, 0),
  "1": Point(+1, 0),
  "LEFT": Point(0, -1),
  "L": Point(0, -1),
  "2": Point(0, -1),
  "RIGHT": Point(0, +1),
  "R": Point(0, +1),
  "0": Point(0, +1),
}

@dataclass
class DrillInstr:
  direction: str
  count: int
  color: str

  @staticmethod
  def parse(line):
    d, c, color = line.split(" ")
    return DrillInstr(d, int(c), color)


def minpoint(p1, p2):
  x1 = min(p1.x, p2.x)
  y1 = min(p1.y, p2.y)
  return Point(x1, y1)

def maxpoint(p1, p2):
  x2 = max(p1.x, p2.x)
  y2 = max(p1.y, p2.y)
  return Point(x2, y2)

LOAD = "content"
def REWRITE(lines):
  return [DrillInstr.parse(l) for l in lines]

def TEST(inputs):
  pass

def PART1(inputs):
  pos = Point(0, 0)

  dugout = set()
  dugout.add(pos)

  minp, maxp = pos, pos
  for instr in inputs:
    direction = DIRECTIONS[instr.direction]
    for i in range(instr.count):
      pos = pos + direction
      dugout.add(pos)
    print(pos)
    minp = minpoint(minp, pos)
    maxp = maxpoint(maxp, pos)

  #print(inputs)
  #printgraph(dugout, minp, maxp)
  count, insides = find_area_inside(dugout, minp, maxp)
  printgraph(dugout, minp, maxp, insides)
  # Attempt 1: 40476, too low.
  # Include the "walls" in the amount of dug space... 
  # Attempt 2: 44436 - correct.
  return count + len(dugout)

# Taken from: https://www.mathopenref.com/coordpolygonarea.html
def polygone_area(points):
  assert len(points) > 1
  assert points[0] == points[-1]
  total = 0
  for p1, p2 in pairwise(points):
    total += p1.x * p2.y - p1.y * p2.x

  return int(math.fabs(total) // 2)

def dig_perimeter(points):
  assert len(points) > 1
  assert points[0] == points[-1]
  total = 0
  for p1, p2 in pairwise(points):
    assert p1.x == p2.x or p1.y == p2.y
    delta = p1 - p2
    total += math.fabs(delta.x + delta.y) # one of these is empty.

  # This _is not_ the perimeter of the polygone.
  return int(total / 2) + 1

def PART2(inputs):
  pos = Point(0, 0)

  digline = [pos]

  minp, maxp = pos, pos
  for instr in inputs:
    d = DIRECTIONS[instr.color[-2]] 
    c = int(instr.color[2:-2], base=16) 
    print("move", d, "for", c)
    pos = pos + (d * c)
    digline.append(pos)
    minp = minpoint(minp, pos)
    maxp = maxpoint(maxp, pos)

  area = polygone_area(digline)
  perimeter = dig_perimeter(digline)
  #print("delta to example:", 952408144115 - area - perimeter)
  return area + perimeter
