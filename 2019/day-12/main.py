#!/usr/bin/env python3

import argparse
import copy
import itertools
import math
import sys

def c(i1, i2):
  """Compare two integers, returning -1, 0, 1 based on their relation."""
  if i1 < i2:
    return -1
  elif i1 > i2:
    return 1
  else:
    return 0


class Vector(object):
  def __init__(self, x=0, y=0, z=0):
    self.x = x
    self.y = y
    self.z = z

  def __add__(self, other):
    return Vector(
        self.x + other.x,
        self.y + other.y,
        self.z + other.z)

  def __sub__(self, other):
    return self + (-other)

  def __neg__(self):
    return Vector(
        -self.x,
        -self.y,
        -self.z)

  def __repr__(self):
    return "<x=%s, y=%s, z=%s>" % (self.x, self.y, self.z)

  def ord(self):
    """convert to sum of absolute value of components"""
    return abs(self.x) + abs(self.y) + abs(self.z)

  def cmp(self, other):
    """Compares each of the components of the vector with c"""
    return Vector(
        c(self.x, other.x),
        c(self.y, other.y),
        c(self.z, other.z))


class Moon(object):
  def __init__(self, position):
    self.pos = position
    self.vel = Vector()

  def __repr__(self):
    return "Moon(%s, %s)" % (repr(self.pos), repr(self.vel))


class Planet(object):
  def __init__(self, moons):
    self.moons = moons

  def update_velocity(self):
    for m1, m2 in itertools.combinations(self.moons, 2):
      m1to2 = m1.pos.cmp(m2.pos)
      m1.vel -= m1to2
      m2.vel += m1to2

  def update_position(self):
    for m1 in self.moons:
      m1.pos += m1.vel

  def energy(self):
    return sum([m.pos.ord() * m.vel.ord() for m in self.moons])

  def step(self, n=1):
    for i in range(n):
      self.update_velocity()
      self.update_position()

  def __repr__(self):
    return "\n".join([repr(m) for m in self.moons])

class P(object):
  def __init__(self, p, v):
    self.p = p
    self.v = v

  def __eq__(self, o):
    return self.p == o.p and self.v == o.v

  def __hash__(self):
    return self.p * self.v

  def __copy__(self):
    return P(self.p, self.v)

  def __repr__(self):
    return "P(%s, %s)" % (self.p, self.v)

def cycle_step(cs):
  rs = [copy.copy(c) for c in cs]
  for a, b in itertools.combinations(rs, 2):
    atob = c(a.p, b.p)
    a.v -= atob
    b.v += atob
  for r in rs:
    r.p += r.v
  return rs

def cycle_params(cs):
  """Return (offset, cycle length)"""
  historical = {tuple(cs): 0}
  idx = 0
  while True:
    idx += 1
    #print(n)
    if idx % 100 == 0:
      #print(".", end="", flush=True)
      pass
    n = cycle_step(cs)
    if tuple(n) in historical:
      first = historical[tuple(n)]
      return (first, idx - first)
    historical[tuple(n)] = idx
    cs = n

def lcm(s):
  lcm = s[0]
  for value in s[1:]:
    lcm = lcm * value // math.gcd(lcm, value)
  return lcm

def cycle_length(planet):
  # calculate the length that each component takes.
  xs = [P(m.pos.x, m.vel.x) for m in planet.moons]
  ys = [P(m.pos.y, m.vel.y) for m in planet.moons]
  zs = [P(m.pos.z, m.vel.z) for m in planet.moons]

  s = dict()
  s[tuple([P(1,2), P(2,3)])] = 1
  assert tuple([P(1,2), P(2,3)]) in s

  offset_x, length_x = cycle_params(xs)
  offset_y, length_y = cycle_params(ys)
  offset_z, length_z = cycle_params(zs)

  print("offsets:", offset_x, offset_y, offset_z)
  print("cycle lengths:", length_x, length_y, length_z)
  print("step cycle:", lcm([length_x, length_y, length_z]))
  print("first repeat:", min(offset_x, offset_y, offset_z) + lcm([length_x, length_y, length_z]))

if __name__ == "__main__":
  parser = argparse.ArgumentParser()

  p = Planet([
    Moon(Vector(-1, 0, 2)),
    Moon(Vector(2, -10, -7)),
    Moon(Vector(4, -8, 8)),
    Moon(Vector(3, 5, -1)),
  ])
  cycle_length(p)
  #for i in range(10):
  #  print(p)
  #  p.update_velocity()
  #  p.update_position()
  p.step(10)
  #print("last update:")
  #print(p)
  #print("Energy:", p.energy())
  assert p.energy() == 179

  p2 = Planet([
    Moon(Vector(-8, -10, 0)),
    Moon(Vector(5, 5, 10)),
    Moon(Vector(2, -7, 3)),
    Moon(Vector(9, -8, -3)),
  ])
  cycle_length(p2)
  p2.step(100)
  #print(p2)
  assert p2.energy() == 1940

  jupiter = Planet([
    Moon(Vector(-7, -1, 6)),
    Moon(Vector(6, -9, -9)),
    Moon(Vector(-12, 2, -7)),
    Moon(Vector(4, -17, -12)),
  ])
  cycle_length(jupiter)
  jupiter.step(1000)
  print(jupiter.energy())

  # find the number of steps to reach a previous state.
