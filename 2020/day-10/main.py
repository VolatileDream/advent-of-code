#!/usr/bin/python3

import argparse
import collections
import functools
import itertools
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


def machine_rating(jolts):
  return jolts[-1] + 3


def deltas(jolts):
  # return the delta of jolts.
  j1 = list(jolts)
  j1.insert(0, 0)
  j2 = list(jolts)
  j2.append(machine_rating(jolts))
  return list(map(lambda z: z[1] - z[0], zip(j1, j2)))


def part1(things):
  ds = deltas(things)
  out = collections.defaultdict(int)
  for d in ds:
    out[d] += 1
  return out[1] * out[3]


def within(x, y, max_delta):
  return abs(x - y) <= max_delta


def valids(jolts):
  # For each item count the number of valid preceeding items
  # Note: it can be at most 3, eg: 1 2 3 4 -> 4 has 3 options.

  jolts_with_ends = list(jolts)
  jolts_with_ends.insert(0, 0)
  jolts_with_ends.append(machine_rating(jolts))

  options = []
  for i in range(1, len(jolts_with_ends)):
    bottom = max(0, i - 3) # catch early items

    valid = 0
    item = jolts_with_ends[i]

    for j in range(bottom, i):
      if within(jolts_with_ends[j], item, 3):
        valid += 1

    options.append(valid)

  return options
        
      
def product(l):
  p = 1
  for i in l:
    p *= i
  return p


def split_on_delta(jolts):
  out = []
  acc = [0]
  prev = 0
  for i in jolts:
    acc.append(i)
    if abs(i - prev) == 3:
      out.append(acc)
      acc = [i]

    prev = i

  if acc:
    out.append(acc)
  return out


def bfs_paths(current, adjacent, end):
  # breadth first search for possible paths from the start of the array to the end.

  if current == end:
    return 1

  paths = 0
  for a in adjacent[current]:
    paths += bfs_paths(a, adjacent, end)

  return paths


def compute_paths(jolts):
  #print(jolts)
  if len(jolts) < 3:
    # impossible to have more than 1 path
    return 1

  first, *middle, end = jolts

  adjacency = collections.defaultdict(set)
  jolts_set = set(jolts)
  for p in jolts:
    #print("range", p, list(range(p + 1, p + 4)))
    for i in range(p + 1, p + 4):
      if i in jolts_set:
        adjacency[p].add(i)

  #print(first, "->", end, ":", adjacency.items())
  return bfs_paths(first, adjacency, end)


def count_paths(jolts):
  # the shortest string of deltas we can do is [3, 3, 3, ...]
  # the longest is [1, 1, 1, ...]

  # there are some spots where we _have_ to have a 3 delta.
  # We want to break up the problem into segments and then rejoin
  # based on these required delta=3 parts.
  subseqs = split_on_delta(jolts)
  counts = [compute_paths(s) for s in subseqs]
  return product(counts)

def part2(things):
  # for part two we want to append the machine to the end.
  things.append(machine_rating(things))
  #print(split_on_delta(things))
  #print(things)
  #print(deltas(things))
  print(product(valids(things)))
  return count_paths(things)


def main(filename):
  things = [int(i) for i in load_file(filename)]
  things.sort()

  print("jolts:", len(things), "=>", things)
  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
