#!/usr/bin/env python-mr

from collections import defaultdict
from itertools import permutations
from _.data.formatting.blocks import Block
from _.command_line.flags import Flag

def intersection(sets):
  result = sets[0]
  for s in sets[1:]:
    result = result.intersection(s)
  return result


class BitSegments:
  @staticmethod
  def to_int(segments):
    out = 0
    for s in segments:
      offset = ord(s) - ord("a")
      out += (1 << offset)
    return out

  @staticmethod
  def to_str(segments):
    out = ""
    offset = 0
    while segments:
      if segments & 1:
        o = offset + ord("a")
        out += chr(o)
      offset += 1
      segments = segments >> 1
    return offset


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
  CHARACTERS_B = {BitSegments.to_int(value): key for key, value in DIGITS.items()}

  @staticmethod
  def parse(string):
    patterns = string.strip().split(" ")
    patterns.sort(key=len)
    return BrokenDisplaySegment(patterns)

  def __init__(self, patterns):
    self._patterns = patterns
    self._map = None
    self._bmap = None

  def solve(self) -> str:
    if self._map:
      return self._map

    # Patterns already sorted for length
    pats = [set(p) for p in self._patterns]
    one, seven, four, mtwo, mthree, mfive, *zerosixnine, eight = pats

    #print(one, seven, four)
    a = seven.difference(one).pop()
    cf = seven.intersection(one)
    # have top, bottom, middle all together.
    adg = intersection((mtwo, mthree, mfive))
    d = four.intersection(adg).pop()
    b = four.difference(one).difference(d).pop()
    g = adg.difference(a + d).pop()

    zero, = [by for by in zerosixnine if d not in by]
    sixnine = [by for by in zerosixnine if d in by]

    ce = sixnine[0].symmetric_difference(sixnine[1])
    c = cf.intersection(ce).pop()
    e = ce.difference(c).pop()
    f = cf.difference(c).pop()

    mapped = a + b + c + d + e + f + g
    self._map = { m: char for m, char in zip(mapped, "abcdefg")}
    return self._map

  def solve_bits(self):
    if self._bmap:
      return self._bmap

    # Patterns already sorted by length
    pats = [BitSegments.to_int(p) for p in self._patterns]
    one, seven, four, mtwo, mthree, mfive, *zerosixnine, eight = pats

    a = one ^ seven
    cf = seven & one
    # have top, bottom, middle all together.
    adg = mtwo & mthree & mfive
    d = four & adg
    b = (four ^ one) ^ d
    g = adg ^ (a | d)

    zero, = [by for by in zerosixnine if not d & by]
    msix, mnine = [by for by in zerosixnine if d & by]

    ce = msix ^ mnine
    c = cf & ce
    e = ce ^ c
    f = cf ^ c

    bmap = {
      a: "a",
      b: "b",
      c: "c",
      d: "d",
      e: "e",
      f: "f",
      g: "g",
    }
    self._bmap = {key: BitSegments.to_int(value) for key, value in bmap.items()}
    return self._bmap

  def find_digit(self, display_digit: str):
    mapping = self.solve()
    remapped = [mapping[d] for d in display_digit]
    remapped.sort()
    return BrokenDisplaySegment.CHARACTERS["".join(remapped)]

  def find_digit_(self, display_digit: str):
    mapping = self.solve_bits()
    remap = 0
    for d in display_digit:
      remap |= mapping[BitSegments.to_int(d)]
    return BrokenDisplaySegment.CHARACTERS_B[remap]


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
