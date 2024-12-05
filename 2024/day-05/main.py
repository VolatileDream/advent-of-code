#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from functools import cmp_to_key
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

LOAD = "groups"
def REWRITE(groups):
  # An entry must be <before> some numbers and <after> others.
  # number -> (set<before>, set<after>)
  rules = defaultdict(lambda: (set(), set(),))

  for r in groups[0]:
    before, after = r.split("|")
    rules[before][0].add(after)
    rules[after][1].add(before)

  #print(rules)
  return (rules, groups[1])

def TEST(inputs):
  pass

def correctly_ordered(rules, nums):
  #print(nums)
  # check uniqueness
  assert(len(nums) == len(set(nums)))

  before = set()
  after = set(nums)
  for num in nums:
    after.remove(num)
    before.add(num)

    r = rules[num]
    if len(r[0].intersection(before)) or len(r[1].intersection(after)):
      #print("invalid", num, r, before, after)
      return False

  return True

def PART1(inputs):
  rules, lines = inputs
  value = 0
  for l in lines:
    nums = l.split(",")
    if correctly_ordered(rules, nums):
      v = int(nums[len(nums) // 2])
      #print("valid", nums, v)
      value += v

  # 3608
  return value

def rules_order(rules):
  def cmp(key1, key2):
    r = rules[key1]
    if key2 in r[0]:
      # key1 < key2
      return -1
    elif key2 in r[1]:
      # key1 > key2
      return 1
    raise Exception(f"couldn't handle keys {key1}, {key2}")

  return cmp

def PART2(inputs):
  rules, lines = inputs
  value = 0

  order = rules_order(rules)
  for l in lines:
    nums = l.split(",")
    if not correctly_ordered(rules, nums):
      nums.sort(key=cmp_to_key(order))
      v = int(nums[len(nums) // 2])
      #print("valid", nums, v)
      value += v

  # 4922
  return value
