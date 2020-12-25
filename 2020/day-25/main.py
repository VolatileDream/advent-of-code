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

def smaller_loopsize(target1, target2, base):
  want = {target1, target2}
  acc = 0
  value = 1
  while value not in want:
    acc += 1
    value = (value * base) % CRYPTO_PRIME

  if value == target1:
    return (acc, None)

  return (None, acc)


def find_loopsize(target, subject):
  acc = 0
  value = 1
  while value != target:
    acc += 1
    value = (value * subject) % CRYPTO_PRIME

  return acc


def transform(base, exponent):
  # this uses square-and-multiply for fast exponentiation, because the
  # "crypto" is just exponentiation.
  #
  # from wikipedia (https://en.wikipedia.org/wiki/Exponentiation_by_squaring):
  #   (this doesn't handle negative exponents)
  assert exponent >= 0, "Bad exponent"

  value = base
  carry = 1
  while exponent > 1:
    if exponent % 2 == 1:
      carry = (carry * value) % CRYPTO_PRIME

    value = (value * value) % CRYPTO_PRIME
  
    exponent = exponent >> 1

  return (value * carry) % CRYPTO_PRIME


def part1(things):
  card_public, door_public = things

  # We can avoid computing both exponents because the encryption value can be
  # derived from one public key, and the other exponent. This is significantly
  # faster than attempting to compute both.
  card_loop, door_loop = smaller_loopsize(card_public, door_public, 7)
  #card_loop = find_loopsize(card_public, 7)
  #door_loop = find_loopsize(door_public, 7)

  print("loop sizes", card_loop, door_loop)
  #assert transform(7, card_loop) == card_public, "{} != {}".format(transform(7, card_loop), card_public)
  #assert transform(7, door_loop) == door_public, "{} != {}".format(transform(7, door_loop), door_public)

  enc = None

  if door_loop:
    enc = transform(card_public, door_loop)

  if card_loop:
    enc = transform(door_public, card_loop)

  return enc


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
