#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

import re

LOAD = "content"
def REWRITE(lines):
  return lines

def TEST(inputs):
  pass

def PART1(inputs):
  #print(len(inputs))

  count = 0
  val = 0
  for line in inputs:
    multmatch = re.compile("mul\(\d{1,3},\d{1,3}\)")
    for mul in multmatch.finditer(line):
      mul = mul.group()
      comma = mul.index(",")
      first, second = int(mul[4:comma]), int(mul[comma+1:-1])
      #print(mul)#, first, second)
      val += first * second
      count += 1

  #print(count)
  # Attempt 1: 26556497 - accidentally only processed line 1
  return val

def PART2(inputs):
  enable = True
  count = 0
  val = 0
  for line in inputs:
    multmatch = re.compile("(mul\(\d{1,3},\d{1,3}\)|do\(\)|don't\(\))")
    for item in multmatch.finditer(line):
      item = item.group()
      if item == "do()":
        enable = True
      elif item == "don't()":
        enable = False
      elif enable:
        mul = item
        comma = mul.index(",")
        first, second = int(mul[4:comma]), int(mul[comma+1:-1])
        val += first * second
        count += 1
  return val
