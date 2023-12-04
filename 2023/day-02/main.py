#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from functools import reduce
from typing import NamedTuple
from _.data.formatting.blocks import Block

@dataclass
class RGB:
  R: int
  G: int
  B: int

  @staticmethod
  def parse(s):
    #print(s)
    R = RGB(0,0,0)
    parts = s.split(", ")
    for p in parts:
      n, c = p.split(" ")
      #print(p, "=", n, "+", c)
      if c == "red":
        R.R = int(n)
      elif c == "green":
        R.G = int(n)
      elif c == "blue":
        R.B = int(n)

    return R
      

LOAD = "content"
def REWRITE(lines):
  games = {}
  for l in lines:
    if not l:
      continue

    l = l.replace("Game ", "")
    n, rest = l.split(": ")

    reads = [RGB.parse(r) for r in rest.split("; ")]

    games[int(n)] = reads
  return games


def PART1(inputs):
  def reqs(r: RGB):
    return r.R <= 12 and r.G <= 13 and r.B <= 14

  s = 0
  for game, reads in inputs.items():
    possible = True
    for r in reads:
      if not reqs(r):
        possible = False
        break

    if possible:
      s += game
    #print(game, possible)
  #print(inputs)
  return s


def PART2(inputs):
  def RGB_max(x, y):
    return RGB(max(x.R, y.R), max(x.G, y.G), max(x.B, y.B))

  def power(r):
    return r.R * r.G * r.B

  s = 0
  for game, reads in inputs.items():
    r = reduce(RGB_max, reads[1:], reads[0])
    #print(game, r, power(r))
    s += power(r)

  return s
