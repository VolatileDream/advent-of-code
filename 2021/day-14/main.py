#!/usr/bin/env python-mr

from collections import defaultdict
from _.data.formatting.blocks import Block

def pair_map(lines):
  m = {}
  for line in lines:
    pair, insert = line.split(" -> ")
    if pair in m:
      raise Exception("Duplicate pairs?")
    m[pair] = insert

  return m


LOAD = "groups"
def REWRITE(lines):
  return (lines[0][0], pair_map(lines[1]))


def insert(string, insertions):
  out = ""
  for first, second in zip(string, string[1:]):
    i = insertions[first + second]
    out = out + first + i

  out += string[-1]
  return out


def count(string):
  c = defaultdict(int)
  for s in string:
    c[s] += 1

  return c


def PART1(inputs):
  string, mapping = inputs
  print(inputs)

  s = string
  for _i in range(10):
    s = insert(s, mapping)

  c = count(s)
  return c[max(c, key=lambda x: c[x])] - c[min(c, key=lambda x: c[x])]


class CountingDict(defaultdict):
  def __add__(self, other):
    if type(self) != type(other):
      return NotImplemented

    keys = set(self.keys()).union(other.keys())
    out = CountingDict(int)
    for k in keys:
      out[k] += self.get(k, 0)
      out[k] += other.get(k, 0)

    return out


def inserts(string, mapping, count=1):
  # The string ~doubles in size every insertion pass, an iterated solution is
  # much too slow. Instead this recursive memoization is much much faster.

  memo = {}
  def compute_pair(p1, p2, count):
    key = (p1, p2, count)
    #print("compute_pair", *key)

    if key in memo:
      return memo[key]

    c = CountingDict(int)
    if count == 0:
      c[p1] += 1
      c[p2] += 1
    else:
      i = mapping[p1 + p2]
      c = compute_pair(p1, i, count - 1) + compute_pair(i, p2, count - 1)
      # i is counted in both.
      c[i] -= 1

    memo[key] = c
    return c

  c = CountingDict(int)
  for first, second in zip(string, string[1:]):
    #print("zip", first, second, c)
    c = c + compute_pair(first, second, count)
    c[second] -= 1

  c[string[-1]] += 1 # removed because it was the last pair
  return c


def PART2(inputs):
  string, mapping = inputs
  count = 40
  c = inserts(string, mapping, count=count)
  #print("after", count, "we see", c)
  return c[max(c, key=lambda x: c[x])] - c[min(c, key=lambda x: c[x])]
