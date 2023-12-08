#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block

import math

@dataclass(unsafe_hash=True, frozen=True)
class Position:
  moves: int
  state: str


def graph_move(path, graph, pos: Position):
  l, r = graph[pos.state]
  n = path[pos.moves % len(path)]
  if n == "L":
    return Position(pos.moves + 1, l)
  else:
    return Position(pos.moves + 1, r)


LOAD = "groups"
def REWRITE(lines):
  graph = dict()
  movement, edges = lines
  movement = movement[0]
  for e in edges:
    e = e.replace(" ", "").replace("(", "").replace(")", "")
    start, rest = e.split("=")
    l, r = rest.split(",")

    graph[start] = (l, r)
  return (movement, graph)


def PART1(inputs):
  path, graph = inputs
  pos = Position(0, "AAA")
  while pos.state != "ZZZ":
    #print(pos)
    pos = graph_move(path, graph, pos)

  return pos.moves

def cycle_length(path, graph, cycle):
  p = cycle
  moves = 1
  p = graph_move(path, graph, p)
  while (p.moves % len(path), p.state) != (cycle.moves % len(path), cycle.state):
    p = graph_move(path, graph, p)
    moves += 1

  return moves

def find_Z_cycle(path, graph, start):
  p = Position(0, start)
  visitedZ = set()
  visited = set() # (path offset, node)
  moves = 0
  while (p.moves % len(path), p.state) not in visited:
    visited.add((p.moves % len(path), p.state))
    p = graph_move(path, graph, p)
    moves += 1
    if p.state.endswith("Z"):
      visitedZ.add(p)

  cycleStart = p
  cycleDist = moves
  # Found a cycle!
  print("cycle", start, ">", p, p.moves % len(path), moves)
  print("  Z", visitedZ)

  l = cycle_length(path, graph, p)
  print("  length", l)

  assert cycle_length(path, graph, visitedZ.pop()) == l
  return l

def PART2(inputs):
  path, graph = inputs
  states = list(filter(lambda x: x.endswith("A"), graph.keys()))
  print("ending in A", len(states))
  print(states)
  cycles = []
  for s in states:
    cycles.append(find_Z_cycle(path, graph, s))

  # Need least common multiple of this.
  return math.lcm(*cycles)
