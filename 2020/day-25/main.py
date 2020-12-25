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

CRYPTO_PRIME = 20201227

def find_loopsize(target, subject):
  acc = 0
  value = 1
  while value != target:
    acc += 1
    value *= subject
    value = value % CRYPTO_PRIME

  return acc


def transform(subject, loop):
  value = 1
  # while you _can_ use exponents here, why make the numbers big?
  # because python supports bignumbers, it'll do it...but then it
  # gets sloooooooooooow.
  for _ in range(loop):
    value *= subject
    value = value % CRYPTO_PRIME
  return value


def crypto():
  m = {}
  card_public = transform(m, 7, 8)
  door_public = transform(m, 7, 11)
  return (card_public, door_public)


def part1(things):
  card_public, door_public = things
  card_loop = find_loopsize(card_public, 7)
  door_loop = find_loopsize(door_public, 7)

  assert transform(7, card_loop) == card_public
  assert transform(7, door_loop) == door_public

  enc1 = transform(card_public, door_loop)
  enc2 = transform(door_public, card_loop)
  assert enc1 == enc2

  return enc1

def part2(things):
  pass


def main(filename):
  things = [int(i) for i in load_file(filename)]

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
