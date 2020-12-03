#!/usr/bin/python3

import argparse
import sys


def load_file(filename):
  contents = []
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip() # remove trailing newline
      contents.append(line)
  return contents


def traversal(landscape, movement_gen):
  x,y = (0,0)
  while True:
    move = next(movement_gen)

    if move == "down":
      y += 1
    elif move == "right":
      x += 1
    elif move == "left":
      x -= 1
    elif move == "check":
      line = landscape[y]
      pos = x % len(line)
      yield line[pos]

    if y >= len(landscape):
      return



def part1_move():
  while True:
    yield "right"
    yield "right"
    yield "right"
    yield "down"
    yield "check"


def count_trees(traversal):
  trees = 0
  for t in traversal:
    if t == "#":
      trees += 1
  return trees


def main(filename):
  landscape = load_file(filename)
  print("part 1:", count_trees(traversal(landscape, part1_move())))
  print("part 2:", count_trees(traversal(landscape, part1_move())))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
