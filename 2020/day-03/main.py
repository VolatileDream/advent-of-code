#!/usr/bin/python3

import argparse
import math
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
    elif move == "check":
      line = landscape[y]
      pos = x % len(line)
      yield line[pos]

    if y >= len(landscape):
      return


def move(right, down):
  while True:
    for _ in range(right):
      yield "right"
    for _ in range(down):
      yield "down"
    yield "check"


def count_trees(landscape, move):
  trees = 0
  for t in traversal(landscape, move):
    if t == "#":
      trees += 1
  return trees


def main(filename):
  landscape = load_file(filename)
  print("part 1:", count_trees(landscape, move(3, 1)))

  p2_moves = [(1, 1), (3, 1), (5, 1), (7, 1), (1, 2)]
  p2_counts = [count_trees(landscape, move(r,d)) for r, d in p2_moves]
  print("part 2:", math.prod(p2_counts))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
