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


def part1(things, distance=2020):
  last_said = collections.defaultdict(list)

  for i in range(len(things)):
    last = things[i]
    last_said[last].append(i)
    #print(last) 

  for i in range(len(things), distance):
    previously = last_said[last]
    if len(previously) <= 1:
      last = 0
    else:
      last = previously[-1] - previously[-2]
   
    #print(last) 
    last_said[last].append(i)

    while len(last_said[last]) > 2:
      last_said[last].pop(0)

  return last


def part2(things):
  return part1(things, 30000000)


def main(filename):
  things = [int(i) for i in load_file(filename)[0].split(",")]

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
