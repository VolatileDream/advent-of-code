#!/usr/bin/env python-mr

from collections import defaultdict
from typing import NamedTuple
from _.data.formatting.blocks import Block

LOAD = "content"
def REWRITE(lines):
  return lines


def PART1(inputs):
  return 0
  items = []
  for line in inputs:
    digit1, digit2 = None, None
    for c in line:
      if c.isdigit() and digit1 is None:
        digit1 = c
        digit2 = c
      elif c.isdigit():
        digit2 = c

    items.append(int(digit1) * 10 + int(digit2))
  return sum(items)

# IT would be better to use https://en.wikipedia.org/wiki/Aho%E2%80%93Corasick_algorithm
def substitution(line):
  #for i in inputs:
  #  print(i)
  # The question suggests, but _does not require_ we handle "sixteen" or "twenty".
  digits = {
    "one": "1",
    "two": "2",
    "three": "3",
    "four": "4",
    "five": "5",
    "six": "6",
    "seven": "7",
    "eight": "8",
    "nine": "9",
  }

  idx = 0
  while idx < len(line):
    for d, n in digits.items():
      #print(line[idx:], d)
      if line.startswith(d, idx):
        line = line.replace(d, n, 1)
    idx += 1
  return line
    

def PART2(inputs):
  items = []
  for line in inputs:
    #print(line, substitution(line))
    line = substitution(line)

    digit1, digit2 = None, None
    for c in line:
      if c.isdigit() and digit1 is None:
        digit1 = c
        digit2 = c
      elif c.isdigit():
        digit2 = c
    items.append(int(digit1) * 10 + int(digit2))

  return sum(items)
