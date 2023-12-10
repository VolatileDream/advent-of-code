#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

import math
import sys

ADJ = {
  "|": [(-1, 0), (+1, 0)],
  "-": [(0, -1), (0, +1)],
  "L": [(-1, 0), (0, +1)],
  "J": [(-1, 0), (0, -1)],
  "7": [(+1, 0), (0, -1)],
  "F": [(+1, 0), (0, +1)],
  "S": [(-1, 0), (+1, 0), (0, -1), (0, +1)],
  #".": [],
}
DRAW = {
  "│": [(-1, 0), (+1, 0)],
  "─": [(0, -1), (0, +1)],
  "╰": [(-1, 0), (0, +1)],
  "╯": [(-1, 0), (0, -1)],
  "╮": [(+1, 0), (0, -1)],
  "╭": [(+1, 0), (0, +1)],
}

def walk(graph, prev, node, end, seen=None):
  if node == end:
    return [node]

  if seen is None:
    seen = set()

  for adj in graph[node]:
    if adj in seen or adj == prev:
      continue
    seen.add(adj)

    path = walk(graph, node, adj, end, seen)
    if path is not None:
      path.append(node)
      return path

  return None


LOAD = "content"
def REWRITE(lines):
  start = None
  graph = defaultdict(set)
  for row, line in enumerate(lines):
    for col, l in enumerate(line):
      if l == "S":
        start = (row, col)
      elif l == ".":
        continue
      for r, c in ADJ[l]:
        graph[(row, col)].add((row + r, col + c))

  rm = prune_edges(graph)
  sys.setrecursionlimit(len(graph) + 1000)
  print("rm", rm)

  return (start, (len(lines), len(lines[0])), graph)


def find_cycle(graph, start):
  for a in graph[start]:
    path = walk(graph, start, a, start, None)
    return path

def prune_edges(graph):
  # prune the graph for bits that don't point to each other.
  rm = 0
  npositions = list(graph.keys())
  positions = None
  while npositions != positions:
    positions = npositions
    for pos in positions:
      cpy = list(graph[pos])
      for a in cpy:
        if a not in graph or pos not in graph[a]:
          graph[pos].remove(a)
          rm += 1
      if len(graph[pos]) == 0:
        del(graph[pos])

    npositions = list(graph.keys())
  return rm

def PART1(inputs):
  start, sizes, graph = inputs

  #print(graph)
  path = find_cycle(graph, start)
  #print(path)
  #print(len(graph))

  # Attempt 1: 8700 - half of the remaining graph size after pruning.
  # Attempt 2: 7102 half the cycle size. :) - YES!
  return len(path) / 2

def con_char(pos, adjs):
  row, col = pos
  for char in DRAW:
    found = True
    for (r, c) in DRAW[char]:
      if (row + r, col + c) not in adjs:
        found = False
        break
    if found:
      #print("con_char", char)
      return char

  assert False, f"no found char for {pos} with {adjs}"

def printgraph(graph, sizes, inside=set()):
  maxrows, maxcols = sizes
  for row in range(maxrows):
    line = ""
    for col in range(maxcols):
      p = (row, col)
      if p in graph:
        #line += "\033[31m" + con_char(p, graph[p]) + "\033[39;49m"
        line += con_char(p, graph[p])
      elif p in inside:
        line += "."
      else:
        line += " "
    print(line)

# Relies on the observation that "in" or "out" of the cycle is just checking how
# many pipe segments we've crossed over (plus some other logic).
#
# Cross pipes:
#  * ╰---╮
#  * |
#  * ╭---╯
# NOT cross:
#  * ╰---╯
#  * -
#  * ╭---╮
#
def find_area_inside(graph, sizes):
  switches = {
    "╭": "╯", "╰": "╮",
  }
  count = 0
  positionsinloop = set()
  maxrows, maxcols = sizes
  for row in range(maxrows):
    inloop = False
    start = None
    for col in range(maxcols):
      p = (row, col)
      if p not in graph:
        if inloop:
          count += 1
          positionsinloop.add(p)
        continue

      char = con_char(p, graph[p])
      if char == "─":
        continue
      elif char == "│":
        inloop = not inloop
        continue

      if start is None:
        start = char
      else:
        if switches[start] == char:
          inloop = not inloop
        start = None

  return (count, positionsinloop)

def PART2(inputs):
  start, sizes, graph = inputs
  path = find_cycle(graph, start)

  ngraph = {}
  for idx, p in enumerate(path):
    prev = (idx - 1) % len(path)
    next = (idx + 1) % len(path)
    ngraph[p] = set([path[prev], path[next]])

  #printgraph(ngraph, sizes)
  count, inside = find_area_inside(ngraph, sizes)
  printgraph(ngraph, sizes, inside)

  return count
