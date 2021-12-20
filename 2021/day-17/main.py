#!/usr/bin/env python-mr

from collections import defaultdict
from math import ceil, floor, sqrt
from typing import NamedTuple
from _.data.formatting.blocks import Block

class Pos(NamedTuple):
  x: int
  y: int

  def __add__(self, other):
    if type(other) != type(self):
      return NotImplemented

    return Pos(self.x + other.x, self.y + other.y)


class Probe(NamedTuple):
  position: Pos
  velocity: Pos


def sign(x):
  if x > 0:
    return 1
  elif x < 0:
    return -1
  else:
    return 0


def physics_step(p: Probe):
  npos = p.position + p.velocity

  # Update velocity for drag
  x = p.velocity.x
  if x:
    x = (abs(x) - 1) * sign(x)
  y = p.velocity.y - 1

  return Probe(npos, Pos(x, y))


def peak(p1: Pos, p2: Pos):
  if p1.y > p2.y:
    return p1
  return p2


class TargetArea(NamedTuple):
  start: Pos
  end: Pos

  @staticmethod
  def parse(line):
    # Always x, y
    line = line.replace("target area: x=", "").replace(" y=", "")
    xspread, yspread = line.split(",")
    x1, x2 = [int(i) for i in xspread.split("..")]
    y1, y2 = [int(i) for i in yspread.split("..")]

    assert x1 > 0 and x2 > 0, "Can't assume positive x for target"
    assert y1 < 0 and y2 < 0, "Can't assume negative y for target"

    # Top left and bottom right
    return TargetArea(
        Pos(min(x1, x2), max(y1, y2)),
        Pos(max(x1, x2), min(y1, y2)))

  def __contains__(self, pos):
    if type(pos) != Pos:
      return NotImplemented

    return (self.start.x <= pos.x and pos.x <= self.end.x
        and self.start.y >= pos.y and pos.y >= self.end.y)

  def overshoot(self, pos):
    return pos.x > self.end.x or pos.y < self.end.y


def solve_x_root(distance):
  def xdist(start_velocity):
    return (start_velocity + 1) * start_velocity // 2

  velocity = 0
  while xdist(velocity) < distance:
    velocity += 1
  return velocity


# The integral to calculate height
def height(start_y_velocity, steps):
  s = steps - 1/2
  return int(start_y_velocity*steps - (s*s) // 2)


def peak(start_y_velocity):
  # See steps_at_max
  steps = start_y_velocity
  return height(start_y_velocity, steps)


def solve_y_root(distance, exit_distance):
  # for any given starting velocity (v) we see the velocity graph:
  # * v, v - 1, v - 2, v - 3, ...
  # This is a line with slope -1, with coordinates (0, v), giving the line:
  #  y = -1 * x + v
  # If we integrate, we get the height travelled.
  # height = - step^2/2 + v * step

  # We can derive some nice functions from the line & parabola.
  # Number of steps until we hit maximum height, or when the derivative = 0.
  def steps_at_max(velocity):
    # Because the fn is y = -1 * x + v
    # 0 = -x + v
    # x = v
    return velocity

  # When the height-parabola gets to the second zero.
  def ground_again_steps(velocity):
    # Since the function starts at height = 0, and the other zero will be on
    # the opposite side of the maximum, and also equi-distant, it becomes very
    # easy to calculate.
    return 2 * velocity

  def step_hit_distance(start_velocity):
    velocity = start_velocity
    height = 0
    steps = 0
    while height > distance:
      height += velocity
      velocity -= 1
      steps += 1

    #print("step_hit_distance", start_velocity, "to distance", distance, "in", steps, "steps")
    #print("step_hit_distance", "height", height)
    return (steps, height)

  # Starting with a negative y velocity makes no sense, it puts our max(y) at
  # zero. We use `too_fast_for_zone` to find the highest possible y velocity
  # that can conceivably be used, and then search from that value to zero.
  lower_bound = 0

  # When the probe gets back to level with the launcher, it has a velocity of
  # -start_velocity. if -start_velocity causes it to overshoot the target area
  # then it, and all faster probes can not possibly land in the target area.
  # use this as an upper velocity bound.
  upper_bound = abs(exit_distance) + 1

  # Run the physics simulation to check if the starting velocity would land in
  # the target area that we have.
  def in_target_area(start_velocity):
    (dist_steps, height) = step_hit_distance(start_velocity)
    # target area y is negative.
    return distance >= height and height >= exit_distance

  print("y velocity search width", upper_bound - lower_bound)

  # Greedy search backwards... the first thing we find will go highest.
  while not in_target_area(upper_bound):
    upper_bound -= 1

  return upper_bound


def find_range(ta: TargetArea):
  # The goal is to reduce the space of "all x and y" down to a smaller range
  # of possible x and y velocities to test.

  # Distance travelled based on start X velocity is equal to the sum of 0..vel
  x_vel = (solve_x_root(ta.start.x), solve_x_root(ta.end.x))

  # Y is more complex, because it will continue to decrease past zero.
  y_vel = solve_y_root(ta.start.y, ta.end.y)
  return x_vel, y_vel


def eventually_lands_within(p: Probe, ta: TargetArea):
  #print(p.position)
  while not ta.overshoot(p.position):
    p = physics_step(p)
    if p.position in ta:
      #print("in!", p.position)
      return True
    #print(p.position)

  return False



LOAD = "content"
def REWRITE(lines):
  return TargetArea.parse(lines[0])


def PART1(inputs):
  print(inputs)
  rangex, maxy = find_range(inputs)
  print("x in", rangex, "y:", maxy)

  #for i in range(maxy + 4):
  #  print("height", height(maxy, i))
  return peak(maxy)

def PART2(inputs):
  # find all the starting velocities that work.
  unique = 0
  # Test everything from 1 step in, to many steps in.
  for y in range(-abs(inputs.end.y),  abs(inputs.end.y) + 1):
    #print("testing y", y)
    for x in range(0, abs(inputs.end.x) + 1):
      #print("x:", x)
      p = Probe(Pos(0,0), Pos(x, y))
      if eventually_lands_within(p, inputs):
        unique += 1

  return unique
