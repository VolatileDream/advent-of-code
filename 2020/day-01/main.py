#!/usr/bin/python3

import argparse
import collections
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
    contents.append(acc)

  return contents


def find_sum1(items, target_sum):
  seen = set()
  for value in items:
    seen.add(value)
    if (target_sum - value) in seen:
      return (value, target_sum - value)

  return None


def find_sum2(items, target_sum):
  # This is called 3SUM in computer science.

  # Keep track of everything we see.
  seen = set()
  for value in items:
    seen.add(value)

  # Not a lot of values, sorting after the fact is fine.
  values = list(sorted(seen))

  # O(n^2) is the best we can do.
  for first in range(len(values)):
    for second in range(first, len(values)):
      v1 = values[first]
      v2 = values[second]
      v3 = target_sum - v1 - v2
      # Check if we've seen target - *start - *end.
      if v3 in seen:
          return (v1, v2, v3)

  return None


def product(iterable):
  p = 1
  for i in iterable:
    p *= i
  return p

def part1(things):
  return product(find_sum1(things, 2020))


def part2(things):
  return product(find_sum2(things, 2020))


def main(filename):
  things = [int(i) for i in load_file(filename)]

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
