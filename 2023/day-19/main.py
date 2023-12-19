#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.data.structures.inversion_list import InversionList
from _.games.advent_of_code.utils import read_numbers

import copy

@dataclass
class Test:
  check: None
  checktuple: tuple
  label: str

  @staticmethod
  def parse(line):
    if ":" not in line:
      return Test(None, None, line)
    check, label = line.split(":")
    which = check[0]
    op = check[1]
    value = int(check[2:])
    if op == ">":
      return Test(lambda v: getattr(v, which) > value, (which, op, value), label)
    return Test(lambda v: getattr(v, which) < value, (which, op, value), label)

@dataclass
class TestSet:
  label: str
  tests: list[Test]

  def test(self, value):
    for t in self.tests:
      if t.check is None or t.check(value):
        return t.label

    assert False, f"test without fallthrough label"

  @staticmethod
  def parse(line):
    label, rest = line.split("{")
    tests = [Test.parse(t) for t in rest.rstrip("}").split(",")]
    return TestSet(label, tests)
    

@dataclass
class Value:
  x: int
  m: int
  a: int
  s: int

  @staticmethod
  def parse(line):
    parts = line.rstrip("}").split(",")
    vals = [p[p.find("=") + 1:] for p in parts]
    return Value(*[int(v) for v in vals])
    

LOAD = "groups"
def REWRITE(groups):
  tests = {}
  for line in groups[0]:
    t = TestSet.parse(line)
    tests[t.label] = t

  values = []
  for line in groups[1]:
    v = Value.parse(line)
    values.append(v)

  return (tests, values)

def TEST(inputs):
  pass

def partvalue(v):
  return v.x + v.m + v.a + v.s

def PART1(inputs):
  tests, values = inputs
  print(len(tests), len(values))

  process = defaultdict(list)
  process["in"] = list(values)

  while len(process["A"]) + len(process["R"]) != len(values):
    keys = set(process.keys())
    keys.remove("A")
    keys.remove("R")

    while keys:
      k = keys.pop()
      vs = process[k]
      del process[k]

      test = tests[k]
      for v in vs:
        n = test.test(v)
        process[n].append(v)

  print(process["A"])
  return sum(map(partvalue, process["A"])) 

def rangevalue(v):
  return len(v.x) * len(v.m) * len(v.a) * len(v.s)

@dataclass
class ValueRange:
  x: InversionList
  m: InversionList
  a: InversionList
  s: InversionList

  def remove(self, attr, r):
    selfattr = getattr(self, attr)
    intersect = selfattr.intersects(r)
    if not intersect:
      return None

    otherattrs = ["x", "m", "a", "s"]
    otherattrs.remove(attr)

    nvr = copy.deepcopy(self)
    setattr(nvr, attr, intersect)
    for r in intersect.iterranges():
      selfattr -= r

    return nvr

  def __bool__(self):
    return bool(self.x) and bool(self.m) and bool(self.a) and bool(self.s)

  @staticmethod
  def all():
    return ValueRange(
      InversionList((1, 4001)),
      InversionList((1, 4001)),
      InversionList((1, 4001)),
      InversionList((1, 4001)),
    )

  @staticmethod
  def range(op, value):
    if op == "<":
      return range(1, value)
    return range(value + 1, 4001)

def PART2(inputs):
  tests, values = inputs

  process = defaultdict(list)
  process["in"] = [ValueRange.all()]

  while True:
    keys = set(process.keys())
    keys.discard("A")
    keys.discard("R")

    if not keys:
      break

    while keys:
      k = keys.pop()
      vs = process[k]
      del process[k]

      test = tests[k]
      #print(k)
      #print(test)
      #print(vs)
      for v in vs:
        n = None
        for t in test.tests:
          if t.checktuple is None:
            n = t.label
            break
          which, op, value = t.checktuple
          r = ValueRange.range(op, value)
          removed = v.remove(which, r)
          if removed:
            process[t.label].append(removed)

        if v:
          process[n].append(v)

  print(process["A"])
  return sum(map(rangevalue, process["A"])) 
