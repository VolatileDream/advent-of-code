#!/usr/bin/python3

import argparse
import collections
import itertools
import functools
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


def load_groups(filename):
  # because some files follow this format instead.
  contents = []
  acc = [] 
  for line in load_file(filename):
    if line:
      acc.append(line)
    else:
      contents.append(acc)
      acc = []

  if acc:
    contents.append(line)

  return contents


def lcm(a, b):
  return a * b // math.gcd(a, b)


def next_multiple(base, m):
  # returns a value >= base such that it is a multiple of m
  remainder = base % m
  if remainder == 0:
    return base
  else:
    return base + m - remainder


def part1(things):
  time = int(things[0])
  busses = [int(b) for b in things[1].replace("x,", "").split(",")]

  cycle = functools.reduce(lcm, busses, 1)

  differences = { b: next_multiple(time, b) for b in busses }

  bus = busses[0]
  smallest = differences[bus]
  for i in range(1,len(busses)):
    b = busses[i]
    if differences[b] < smallest:
      bus = b
      smallest = differences[b]

  return bus * (smallest - time)


def next_offset_multiple(a, lcm, offset, b):
  # return x such that:
  # x = a * z, and
  # x + offset = b * y.
 
  val = a
 
  # this sort of looks like lcm, but not.
  while True:
    if (val + offset) % b == 0:
      return val
    val += lcm


def part2(things):
  time = int(things[0])

  items = things[1].split(",")
  print(items)
  restrictions = []
  for i in range(len(items)):
    r = items[i]
    if r == "x":
      continue
    restrictions.append((i, int(r)))

  # this is the width we'd have to search. it's gonna be biiiiiig.
  # too big to search naively.
  cycle = functools.reduce(lcm, [int(i) for i in things[1].replace("x,", "").split(",")], 1)
  print("cycle", cycle)

  # this is a math puzzle. woo.
  # trying to solve:
  # t + 0 = a * restrict[0]
  # t + 1 = b * restrict[1]
  # ...
  # t + n = l * restrict[n]

  print(restrictions)

  offset, val = restrictions[0]
  rolling_lcm = val
  for i in range(1, len(restrictions)):
    o, v = restrictions[i]
    val = next_offset_multiple(val, rolling_lcm, o, v)
    rolling_lcm = lcm(rolling_lcm, v)
    #print("(", val,"+", o, ") %", v, "== 0 =>", (val + o) % v == 0, "lcm:", rolling_lcm)

  #print("validate")
  # validate.
  for (off, bus) in restrictions:
    #print("(", val,"+", off, ") %", bus, "== 0 =>", (val + off) % bus == 0)
    pass

  #print("expect:", time, "==", val)
  return val


def main(filename):
  things = load_file(filename)

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
