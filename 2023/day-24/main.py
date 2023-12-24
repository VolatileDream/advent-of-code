#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers, factors

import math
import z3

class Range(NamedTuple):
  start: int
  end: int

  def __contains__(self, num):
    return self.start <= num and num < self.end

class Pos3(NamedTuple):
  x: int
  y: int
  z: int

  def __str__(self):
    return f"({self.x},{self.y},{self.z})"

  def __add__(self, other):
    return Pos3(self.x + other.x, self.y + other.y, self.z + other.z)

  @staticmethod
  def parse(line):
    return Pos3(*read_numbers(line))

class Hail(NamedTuple):
  pos: Pos3
  vel: Pos3

  def __str__(self):
    return f"Hail({self.pos} @ {self.vel})"

  @staticmethod
  def parse(line):
    pos, vel = line.split(" @ ")
    return Hail(Pos3.parse(pos), Pos3.parse(vel))

def line_intersect_2d(h1, h2, range):
  # y = m * x + b
  m1 = h1.vel.y / h1.vel.x
  b1 = h1.pos.y - m1 * h1.pos.x

  m2 = h2.vel.y / h2.vel.x
  b2 = h2.pos.y - m2 * h2.pos.x

  #print(h1, h2, ">", b1, b2)

  # Now we have all the values for the composite equation of motion.
  if m1 == m2:
    # The lines intersect forever if they have the same offset, otherwise parallel.
    #print(" parallel?", b1, b2)
    return b2 == b1

  x = (b2 - b1) / (m1 - m2)
  y = x * m2 + b2
  #print(" ", x, y)
  if not x in range or not y in range:
    return False

  # Check if the intersection is forwards or backwards in time.
  # Recall:
  #  pos = vel * t + start
  # then:
  # t = (pos - start) / vel
  # This applies to a single coordinate.
  t1 = (x - h1.pos.x) / h1.vel.x
  t2 = (x - h2.pos.x) / h2.vel.x
  #print(" ", t1, t2)
  return t1 > 0 and t2 > 0

LOAD = "content"
def REWRITE(lines):
  return [Hail.parse(l) for l in lines]

def TEST(inputs):
  pass

def PART1(inputs):
  r = Range(200000000000000, 400000000000000)
  if False:
    r = Range(7, 28)

  print(inputs)
  print(len(inputs))

  count = 0
  for idx, h1 in enumerate(inputs):
    for h2 in inputs[idx + 1:]:
      if line_intersect_2d(h1, h2, r):
        #print(h1, h2)
        count += 1
  return count

def PART2(inputs):
  # oh no. :(
  # I have no idea how to do this. clearly there's a better solution than
  # trying the system of equations solution?

  # Fuck it. we're learning Z3 and leaning on reddit.
  s = z3.Solver()
  # A really clever thing from reddit: we can apply a change to all the hail
  # to have them all pass through the same point. This is the negation of the
  # movement of the rock over time, and the position is going to be the
  # starting position of the rock.

  # Position where everything intersects / rock start.
  x0 = z3.Int("x0")
  y0 = z3.Int("y0")
  z0 = z3.Int("z0")

  # "Rock" velocity modification / inverse rock movement.
  vx = z3.Int("vx")
  vy = z3.Int("vy")
  vz = z3.Int("vz")

  for idx, h in enumerate(inputs):
    # each rock eventually intersects our point on all axes,
    # when given modified velocity.
    t = z3.Int(f"t{idx}")
    s.add(x0 == (h.vel.x + vx) * t + h.pos.x)
    s.add(y0 == (h.vel.y + vy) * t + h.pos.y)
    s.add(z0 == (h.vel.z + vz) * t + h.pos.z)

  print(s.check())
  m = s.model()
  coords = (m[x0], m[y0], m[z0])
  print(coords)
  vel = (m[vx], m[vy], m[vz])
  print(vel)

  return sum(coords)

