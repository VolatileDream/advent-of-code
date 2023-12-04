#!/usr/bin/env python-mr

from collections import defaultdict
from typing import NamedTuple
from _.data.formatting.blocks import Block

import re

LOAD = "content"
def REWRITE(lines):
  cards = []
  digits = re.compile("\d+")
  for l in lines:
    # Pass the ":" and " " after it
    l = l[l.find(":") + 2:]
    winners, mine = l.split("|")

    w = []
    for d in digits.finditer(winners):
      w.append(int(d.group()))

    m = []
    for d in digits.finditer(mine):
      m.append(int(d.group()))
    
    cards.append((w,m,))
  return cards


def PART1(inputs):
  def points(n):
    if n == 0:
      return 0
    return 2 ** (count - 1)

  s = 0
  for idx, (winners, mine) in enumerate(inputs):
    winners = set(winners)
    count = 0
    for n in mine:
      if n in winners:
        count += 1
    #print("Card", idx + 1, "matches:", count, "points:", points(count))
    s += points(count)
  return s


def PART2(inputs):
  def points(n):
    if n == 0:
      return 0
    return 2 ** (count - 1)

  mult = defaultdict(lambda: 1)
  s = 0
  cards = 0
  for idx, (winners, mine) in enumerate(inputs):
    winners = set(winners)
    count = 0
    for n in mine:
      if n in winners:
        count += 1
    #print("Card", idx, "(", mult[idx], ")", "matches:", count, "points:", points(count))
    for i in range(count):
      j = idx + i + 1
      #print(" extra", j, ":", mult[idx], "=", mult[j] + mult[idx])
      mult[j] += mult[idx]
    cards += mult[idx]
    s += points(count) * mult[idx]
 
  return (s, cards) 
