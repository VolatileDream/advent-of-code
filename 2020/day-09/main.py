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


class Q:
  def __init__(self, size):
    self.mset = collections.defaultdict(int)
    self.storage = []
    self.size = size

  def add(self, item):
    self.storage.append(item)
    self.mset[item] += 1
    #print("add", item)

    if len(self.storage) > self.size:
      remove = self.storage.pop(0)
      #print("remove", remove)
      self.mset[remove] -= 1

  def contains_sum(self, value):
    # Use the dictionary lookup trick from day 1
    for s in self.storage:
      compliment = value - s
      if compliment == s:
        # doesn't count
        continue
      #print("trying", s, "need", compliment)
      if self.mset[compliment] > 0:
        return True

    return False


def do(things, preamble):
  # track the order to remove items.
  q = Q(preamble)

  for i in range(preamble):
    n = things[i]
    q.add(n)

  index = preamble

  try:
    while index < len(things):
      n = things[index]

      # check.
      if not q.contains_sum(n):
        return "missing: {} at index: {}".format(n, index)

      q.add(n)
    
      index += 1
  except StopIteration:
    # next raises this exception, we're done.
    pass

  return None


def part1(things, preamble):
  return do(things, preamble)


def part2(things, preamble):
  pass


def main(filename, preamble):
  things = [int(i) for i in load_file(filename)]

  print("part 1:", part1(things, preamble))
  print("part 2:", part2(things, preamble))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')
  parser.add_argument('--preamble', nargs='?', type=int, default=25)

  args = parser.parse_args(sys.argv[1:])
  main(args.input, args.preamble)
