#!/usr/bin/env python-mr

from collections import defaultdict
from itertools import permutations
from _.data.formatting.blocks import Block

def intersection(sets):
  result = sets[0]
  for s in sets[1:]:
    result = result.intersection(s)
  return result


class BrokenDisplaySegment:
  DIGITS = {
      1: "cf",
      7: "acf",
      4: "bcdf",
      2: "acdeg",
      3: "acdfg",
      5: "abdfg",
      0: "abcefg",
      6: "abdefg",
      9: "abcdfg",
      8: "abcdefg",
    }

  CHARACTERS = {value: key for key, value in DIGITS.items()}

  @staticmethod
  def segments(integer):
    # Correct segments.
    return BrokenDisplaySegment.DIGITS[integer]

  @staticmethod
  def parse(string):
    patterns = string.strip().split(" ")
    return BrokenDisplaySegment(patterns)

  def __init__(self, patterns):
    self._patterns = patterns
    self._map = None

  def solve(self) -> str:
    if self._map:
      return self._map

    by_len = defaultdict(list)
    for p in self._patterns:
      by_len[len(p)].append(set(p))

    #print("solve", by_len)

    one, = by_len[2]
    seven, = by_len[3]
    four, = by_len[4]
    #print(one, seven, four)
    a = seven.difference(one).pop()
    cf = seven.intersection(one)
    # have top, bottom, middle all together.
    twothreefive = [by for by in by_len[5]]
    adg = intersection(twothreefive)
    d = four.intersection(adg).pop()
    b = four.difference(one).difference(d).pop()
    g = adg.difference(a + d).pop()

    zero, = [by for by in by_len[6] if d not in by]
    sixnine = [by for by in by_len[6] if d in by]

    ce = sixnine[0].symmetric_difference(sixnine[1])
    c = cf.intersection(ce).pop()
    e = ce.difference(c).pop()
    f = cf.difference(c).pop()

    mapped = a + b + c + d + e + f + g
    self._map = { m: char for m, char in zip(mapped, "abcdefg")}
    return self._map

  def find_digit(self, display_digit):
    #print("find", display_digit)
    mapping = self.solve()
    remapped = [mapping[d] for d in display_digit]
    remapped.sort()
    return BrokenDisplaySegment.CHARACTERS["".join(remapped)]


LOAD = "content"
def REWRITE(lines):
  l = []
  for line in lines:
    patterns, digits = line.split("|")
    display = BrokenDisplaySegment.parse(patterns)
    digits = digits.strip().split(" ")
    l.append((display, digits))
  return l


def PART1(inputs):
  counts = defaultdict(int)
  for display, digits in inputs:
    real = [display.find_digit(d) for d in digits]
    for r in real:
      counts[r] += 1

  return counts[1] + counts[4] + counts[7] + counts[8]


def as_int(a, b, c, d):
  return a * 1000 + b * 100 + c * 10 + d


def PART2(inputs):
  sum = 0
  for display, digits in inputs:
    value = as_int(*[display.find_digit(d) for d in digits])
    sum += value

  return sum
