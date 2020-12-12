#!/usr/bin/python3

import argparse
import collections
import math
import re
import sys
import typing


def load_file(filename):
  contents = []
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip() # remove trailing newline
      contents.append(line)
  return contents


def move_pair(direction, amount=1):
  if direction == 'N':
    return (amount, 0)
  elif direction == 'E':
    return (0, amount)
  elif direction == 'S':
    return (-amount, 0)
  elif direction == 'W':
    return (0, -amount)
  assert False, "bad direction: {}".format(direction)


def move(x, y, direction, distance):
  dx, dy = move_pair(direction, distance)
  return (x + dx, y + dy)

def direction(facing_degrees):
  if facing_degrees == 0:
    return 'N'
  elif facing_degrees == 90:
    return 'E'
  elif facing_degrees == 180:
    return 'S'
  elif facing_degrees == 270:
    return 'W'
  assert False, "bad degrees: {}".format(facing_degrees)


def part1(things):
  # north is 0
  facing = 90 # east
  # north, east is +
  ns = 0
  ew = 0

  directions = ['N', 'E', 'S', 'W']

  for item in things:
    instr = item[0]
    amount = int(item[1:])

    if instr == 'L':
      facing = (facing - amount) % 360
    elif instr == 'R':
      facing = (facing + amount) % 360
    elif instr in directions:
      ns, ew = move(ns, ew, instr, amount)
    else:
      assert instr == 'F'
      ns, ew = move(ns, ew, direction(facing), amount)

  return abs(ns) + abs(ew)


def sign(val):
  return math.copysign(1, val)

def point_rotate(degrees, rel_ns, rel_ew):
  # rotation happens around the ship
  if degrees == 180:
    rel_ns, rel_ew = (-rel_ns, -rel_ew)
  elif degrees == 90:
    rel_ns, rel_ew = (-rel_ew, rel_ns)
  elif degrees == 270:
    rel_ns, rel_ew = (rel_ew, -rel_ns)

  return (rel_ns, rel_ew)

def part2(things):
  # north, east is +
  ns = 0
  ew = 0

  w_ns, w_ew = 1, 10

  rotations = ['L', 'R']
  directions = ['N', 'E', 'S', 'W']

  print("ship:", ns, ew, "waypoint:", w_ns, w_ew)
  for item in things:
    print("instr", item)
    instr = item[0]
    amount = int(item[1:])

    if instr == 'L':
      amount = 360 - amount

    if instr in rotations:
      w_ns, w_ew = point_rotate((amount % 360), w_ns, w_ew)
    elif instr in directions:
      w_ns, w_ew = move(w_ns, w_ew, instr, amount)
    else:
      assert instr == 'F'
      ns = ns + w_ns * amount
      ew = ew + w_ew * amount
    print("ship:", ns, ew, "waypoint:", w_ns, w_ew)

  return abs(ns) + abs(ew)
  pass


def main(filename):
  things = load_file(filename)

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
