#!/usr/bin/env python-mr

from collections import defaultdict
from _.data.formatting.blocks import Block

def graph(lines):
  adjacent = defaultdict(set)
  for line in lines:
    n1, n2 = line.split("-")
    adjacent[n1].add(n2)
    adjacent[n2].add(n1)
  return adjacent


def big_cave(cave):
  # defined as a cave with 2 or more neighbours.
  return cave.isupper()
 

LOAD = "content"
def REWRITE(lines):
  return graph(lines)


def all_paths(graph):
  def pathsr(acc, novisit):
    cur = acc[-1]
    if cur == "end":
      yield ",".join(acc)
      return

    for n in graph[cur]:
      if n in novisit:
        continue
      acc_n = [*acc, n]
      nv = novisit
      if not big_cave(n):
        nv = set(novisit)
        nv.add(n)
      yield from pathsr(acc_n, nv)

  return list(pathsr(["start"], set(["start"])))


def PART1(inputs):
  print(inputs)
  for p in all_paths(inputs):
    #print(p)
    pass
  return len(all_paths(inputs))


def double_visit_paths(graph):
  def pathsr(acc, novisit, candoublevisit=True):
    cur = acc[-1]
    if cur == "end":
      yield ",".join(acc)
      return

    for n in graph[cur]:
      double = candoublevisit
      if n in novisit:
        if double and n not in ("start", "end"):
          double = False
        else:
          continue

      acc_n = [*acc, n]
      nv = novisit
      if not big_cave(n):
        nv = set(novisit)
        nv.add(n)
      yield from pathsr(acc_n, nv, double)

  return list(pathsr(["start"], set(["start"])))


def PART2(inputs):
  paths = double_visit_paths(inputs)
  #paths.sort()
  for p in paths:
    #print(p)
    pass
  return len(paths)
