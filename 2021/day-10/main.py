#!/usr/bin/env python-mr

from collections import defaultdict
from _.data.formatting.blocks import Block

LOAD = "content"
def REWRITE(lines):
  return lines


PARENS = ["()", "[]", "{}", "<>"]
PAIR_ENDS = {second: first for first, second in PARENS}
STARTS = set([first for first, second in PARENS])
CORRUPT_SCORES = {
  ")": 3,
  "]": 57,
  "}": 1197,
  ">": 25137,
}
OPEN_SCORES = {
  "(": 1,
  "[": 2,
  "{": 3,
  "<": 4,
}

def still_open(line):
  stack = []
  for l in line:
    if l in STARTS:
      stack.append(l)
    else:
      need = PAIR_ENDS[l]
      if not stack or stack[-1] != need:
        raise Exception(l)
      else:
        stack.pop()
  return stack


def corrupt(line):
  try:
    still_open(line)
    return None
  except Exception as e:
    return e.args[0]


def PART1(inputs):
  score = 0
  for i in inputs:
    c = corrupt(i)
    if c:
      score += CORRUPT_SCORES[c]
  return score


def PART2(inputs):
  incomplete = []
  for i in inputs:
    try:
      open = still_open(i)
      open.reverse()
      score = 0
      for s in open:
        score = score * 5 + OPEN_SCORES[s]
      incomplete.append(score)
    except:
      # ignore corrupt lines
      pass

  incomplete.sort()
  print(incomplete)
  return incomplete[len(incomplete) // 2]
