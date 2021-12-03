#!/usr/bin/env python-mr

from collections import defaultdict

def dec_bool(val):
  if val == "1":
    return True
  elif val == "0":
    return False
  else:
    raise ValueError("Unexpected value for bool conversion: %s" % (val,))


def REWRITE(values):
  # these are binary numbers but effectively get used as flags.
  # convert to boolean tuples
  return [tuple([dec_bool(b) for b in bits]) for bits in values]


def to_int(tup):
  v = 0
  for t in tup:
    v = v * 2 + int(t)
  return v


def count_set(values):
  pos = defaultdict(int)
  for v in values:
    for index, bit in enumerate(v):
      pos[index] += int(bit)

  return pos


def PART1(values):
  size = len(values)
  counts = count_set(values)
  gamma = [bool(counts[c] > size / 2) for c in counts]
  epsilon = [not b for b in gamma]
  mul = to_int(gamma) * to_int(epsilon)
  return (to_int(gamma), to_int(epsilon), mul)


def filter(values, keep_fn):
  #print("Filtering...")
  size = len(values[0])
  candidates = list(values)
  index = 0
  while len(candidates) > 1:
    bits_set = count_set(candidates)
    #print("Candidates:", [to_int(c) for c in candidates])
    candidates = [c for c in candidates if keep_fn(bits_set, index, c, len(candidates))]
    index = (index + 1) % size
  return candidates[0]


def PART2(values):
  size = len(values[0])
  amount = len(values)
  counts = count_set(values)

  # Compute O2
  o2 = filter(values, lambda counts, index, c, a: c[index] == (counts[index] >= a / 2))
  co2 = filter(values, lambda counts, index, c, a: c[index] == (counts[index] < a / 2))

  o2 = to_int(o2)
  co2 = to_int(co2)
  return (o2, co2, o2 * co2)


