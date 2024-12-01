#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

LOAD = "content"
def REWRITE(lines):
  return [read_numbers(l) for l in lines]

def TEST(inputs):
  pass

def PART1(inputs):
  first, second = list(), list()

  for f, s in inputs:
    first.append(f)
    second.append(s)

  first.sort()
  second.sort()
  print(first, second)

  distance = 0
  for f, s in zip(first, second):
    distance += abs(f - s)

  return distance

def PART2(inputs):
  counts = {}
  for _, s in inputs:
    prev = counts.get(s, 0)
    counts[s] = prev + 1

  similarity = 0
  for f, _ in inputs:
    c = counts.get(f, 0)
    similarity += f * c

  return similarity
    
