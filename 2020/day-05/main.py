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


class BinaryBoarding:

  MATCHER = re.compile("[BF]{7}[RL]{3}")

  def __init__(self, s):
    assert BinaryBoarding.MATCHER.fullmatch(s)
    self.s = s

  def __repr__(self):
    return "BinaryBoarding('{0}')".format(self.s)

  @staticmethod
  def __bin__(seq, check):
    # convert a sequence to a binary number.
    out = 0
    for c in seq:
      out *= 2
      if check(c):
        out += 1
    return out

  def position(self):
    row = BinaryBoarding.__bin__(self.s[:7], lambda c: c == 'B')
    col = BinaryBoarding.__bin__(self.s[7:], lambda c: c == 'R')
    return (row, col)

  def seat_id(self):
    pos = BinaryBoarding.__bin__(self.s, lambda c: c == 'B' or c == 'R')
    return pos


def part1(passes):
  ids = [p.seat_id() for p in passes]
  return (min(ids), max(ids))


def part2(passes):
  # this gives us the range of seats to expect.
  # our seat isn't the first, nor the last.
  start, end = part1(passes)
  missing = set(range(start, end + 1))
  for p in passes:
    missing.remove(p.seat_id())

  # We expect that this is the case.
  if len(missing) == 1:
    return missing.pop()

  # just in case defensive programming.
  for c in missing:
    if (c - 1) in missing and (c + 1) in missing:
      return c

  return -1


def main(filename):
  passes = [BinaryBoarding(p) for p in load_file(filename)]

  print("part 1, seat id range:", part1(passes))
  print("part 2, my seat:", part2(passes))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
