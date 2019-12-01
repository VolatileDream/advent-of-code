#!/usr/bin/env python3

import argparse
import sys

# Solution of part 2 of day 1
def recursive_fuel(mass):
  total_cost = 0
  last_mass = mass
  while True:
    c = fuel_cost(last_mass)
    if c <= 0:
      return total_cost
    total_cost += c
    last_mass = c

# Solution to part 1 of day 1
def fuel_cost(mass):
  return mass // 3 - 2

def p1(input_file, by_line):
  cost = 0
  for line in input_file:
    c = fuel_cost(int(line))
    cost += c
    if by_line:
      print(c)
  if not by_line:
    print(cost)


def p2(input_file, by_line=False):
  cost = 0
  for line in input_file:
    c = recursive_fuel(int(line))
    cost += c
    if by_line:
      print(c)
  if not by_line:
    print(cost)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', type=argparse.FileType('r'), nargs='?', default=sys.stdin)
  parser.add_argument('--by-line', action='store_const', const=True, default=False)
  parser.add_argument('--part', default=None, type=int)

  args = parser.parse_args(sys.argv[1:])
  if args.part == 1:
    p1(args.input, args.by_line)
  elif args.part == 2:
    p2(args.input, args.by_line)
  else:
    raise Exception("unknown part: %s" % args.part)
    

