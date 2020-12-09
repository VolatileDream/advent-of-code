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
        return (n, index)

      q.add(n)
    
      index += 1
  except StopIteration:
    # next raises this exception, we're done.
    pass

  return None


def part1(things, preamble):
  return "missing: {} at index: {}".format(*do(things, preamble))


def find_subset_sum(items, target):
  # This isn't the "real" subset sum, this is contiguous subset sum.
  start = 0
  end = start + 1

  # `start < end` as an invariant.
  while start < len(items):
    s = sum(items[start:end])
    if s == target:
      return items[start:end]
    elif s < target and end + 1 < len(items):
      end += 1
    else:
      # either s > target, or end + 1 is the end
      start += 1
      end = start + 1

  return None


def part2(things, preamble):
  item, index = do(things, preamble)

  subset = find_subset_sum(things[:index], item)
  subset.sort()
  return subset[0] + subset[-1]


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
