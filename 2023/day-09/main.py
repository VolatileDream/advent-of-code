#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

import itertools

def all_zero(seq):
  for s in seq:
    if s != 0:
      return False
  return True

# try to compute the degree of the polynomial.
# I gave up on this because i parsed numbers wrong, and then
# would have had to do a lot to implement fixed form polynomial
# solver...
def degree(seq):
  b = Block()
  count = -1
  #print("degree")
  while not all_zero(seq):
    count += 1
    b |= " ".join([str(i) for i in seq])
    #print(" ", seq)
    nseq = []
    for idx, n in enumerate(seq[:-1]):
      nseq.append(seq[idx + 1] - n)
    seq = nseq

  b = Block(f"degree {count}") | (" " + b)
  #print(b)
  assert len(seq) != 0
  return count

LOAD = "content"
def REWRITE(lines):
  return [read_numbers(l) for l in lines]

def extrapolate(seq, count=1):
  print(" ", seq)
  # Some nice polynomial handling first. :)
  if all_zero(seq) or len(seq) == 0:
    return itertools.repeat(0, count)
  # This is not a shortcut that can be taken... :(
  #elif len(seq) >= 3 and all_zero(seq[-3:-1]):
  #  return itertools.repeat(0, count)

  deltas = []
  for idx, n in enumerate(seq[:-1]):
    deltas.append(seq[idx + 1] - n)

  ndeltas = extrapolate(deltas, count)
  out = [seq[-1]]
  for d in ndeltas:
    out.append(out[-1] + d)
  print(" ", out[1:])
  return out[1:]

def PART1(inputs):
  #print(inputs)
  s = 0
  for i in inputs:
    d = degree(i)
    #print(">", d)
    print("extrapolate")
    e = extrapolate(i, 1)
    s += e[0]

  # Attempt 1: 2933906465 too high
  # Attempt 2: 2876825525 too high
  # After realizing number parsing didn't handle negatives properly...
  # Which explained the problems i had with weird non converging sequences.
  # Attempt 3: 1969958987 - YES!
  return s

def PART2(inputs):
  # oh. easy peasy.
  s = 0
  for i in inputs:
    i.reverse()
    s += extrapolate(i, 1)[0]
  return s
