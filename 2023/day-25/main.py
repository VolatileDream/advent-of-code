#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

import random

LOAD = "content"
def REWRITE(lines):
  graph = defaultdict(set)
  for l in lines:
    node, edges = l.split(": ")
    edges = edges.split(" ")
    for e in edges:
      graph[e].add(node)
    graph[node].update(edges)
  return graph

def TEST(inputs):
  pass

def connected_components(graph, removed=set()):
  nodes = set(graph.keys())
  components = []
  while nodes:
    processing = set([nodes.pop()])
    component = set()
    while processing:
      p = processing.pop()
      nodes.discard(p)
      component.add(p)

      for a in graph[p]:
        if (p, a) in removed or (a, p) in removed:
          continue
        if a in nodes:
          processing.add(a)

    components.append(component)

  return components

# Finding and removing cliques was the first thing I could think of.
# In a highly connected graph, it could have compressed it a whole bunch.
#
# defn: Clique - a group of nodes in a graph, that are all connected to each other.
def cliques(graph):
  process = set(graph.keys())
  clique = []
  while process:
    n = process.pop()
    protoclique = set([n])
    for e in graph[n]:
      if n in graph[e] and e in process:
        protoclique.add(e)
        process.remove(e)
    clique.append(protoclique)

  for idx, c1 in enumerate(clique):
    for c2 in clique[idx + 1:]:
      assert c1.isdisjoint(c2)

  return clique

# This compresses cliques in a graph, by picking a random representative,
# and then remapping all the edges to the random representative.
#
# This is actually bad for things like kargers, because it increases the
# probability that the min-cut edges get randomly chosen, since it removes
# a lot of the non-min-cut edges that are part of cliques.
def compress_cliques(graph):
  newGraph = defaultdict(set)
  nodeMap = {}
  repIndex = {}
  cliqs = cliques(graph)
  for cliq in cliqs:
    rep = next(iter(cliq))
    nodeMap[rep] = cliq
    for c in cliq:
      repIndex[c] = rep

  for node in graph:
    r1 = repIndex[node]
    for e in graph[node]:
      r2 = repIndex[e]
      if r1 == r2:
        continue
      newGraph[r1].add(r2)
      newGraph[r2].add(r1)

  return newGraph, nodeMap

# Simple / naive edge cutting checks.
# Generates all the edges, and then goes through them one at a time. TT_TT
# Very slow O(E^3)
def edge_cutting(graph):
  edges = set()
  for node in graph:
    for e in graph[node]:
      if (e, node,) not in edges:
        edges.add((node, e,))
  #print("edges", len(edges))
  edges = list(edges)

  # This is the key! The graphs given as part of the problem are
  # highly connected, and so running a centrality computation first
  # makes it much easier to find where to cut in the graph.
  central = centrality(graph)
  def edge_weight(e):
    n1, n2 = e
    return central[n1] + central[n2]
  edges.sort(key=edge_weight, reverse=True)

  for i, e1 in enumerate(edges):
    print(f"{i}", len(edges) - i)
    for j, e2 in enumerate(edges[i+1:]):
      for k, e3 in enumerate(edges[i+j+2:]):
        remove = set([e1, e2, e3])
        components = connected_components(graph, remove)
        if len(components) == 2:
          return ((e1, e2, e3), components)

  return False

def kargers(graph, target=100):
  # Implementation of kargers algorithm. Doesn't really seem
  # to work well... Did i do it wrong?
  # https://en.wikipedia.org/wiki/Karger%27s_algorithm
  multigraph = defaultdict(lambda: defaultdict(int))

  # Convert to multigraph.
  for node in graph:
    for e in graph[node]:
      multigraph[node][e] = 1
      multigraph[e][node] = 1

  def edgeCount():
    count = 0
    for node in multigraph:
      for e in multigraph[node]:
        count += multigraph[node][e]
    return count

  def randEdge():
    count = edgeCount()
    if count == 0:
      return (None, None)
    r = random.randint(0, count - 1)

    for node in multigraph:
      for e in multigraph[node]:
        if r <= multigraph[node][e]:
          return (node, e)
        r -= multigraph[node][e]

    assert False, f"rand should have been generated in range..."

  # Oh no, this is really low... :S
  print("kargers probability:", target**2 / edgeCount()**2 )

  while len(multigraph) > target:
    (n1, n2) = randEdge()

    # Do a thing to get consistent naming.
    if n2 < n1:
      n1, n2 = n2, n1
    assert n1 is not None
    assert n2 is not None
    assert n1 != n2

    # Is this edge handling right?
    #multigraph[n1][n2] -= 1
    #multigraph[n2][n1] -= 1
    #if multigraph[n1][n2] > 0:
    #  continue

    del multigraph[n1][n2]
    del multigraph[n2][n1]

    # This lets us retrieve the joined nodes later. :)
    composite = f"{n1}-{n2}"

    n1edges = set(multigraph[n1].keys())
    for e1 in n1edges:
      multigraph[composite][e1] += multigraph[n1][e1]
      multigraph[e1][composite] += multigraph[n1][e1]
      del multigraph[e1][n1]
    del multigraph[n1]

    n2edges = set(multigraph[n2].keys())
    for e2 in n2edges:
      multigraph[composite][e2] += multigraph[n2][e2]
      multigraph[e2][composite] += multigraph[n2][e2]
      del multigraph[e2][n2]
    del multigraph[n2]

  return multigraph

def bfs_path(graph, start, end):
  seen = set()
  # Track the minimum distance from the start,
  # and which node we need to visit to take the min path.
  mindist = defaultdict(lambda: float("inf"))
  mindist[start] = 0
  distfrom = {start: start}
  process = [start]
  processing = set(process)
  while process:
    p = process.pop(0)
    processing.remove(p)
    seen.add(p)

    assert p in mindist
    assert p in distfrom
    if p == end:
      break

    for e in graph[p]:
      if mindist[e] > mindist[p] + 1:
        mindist[e] = mindist[p] + 1
        distfrom[e] = p
      if e in seen or e in processing:
        continue
      process.append(e)
      processing.add(e)

    process.sort(key=lambda n: mindist[n])

  # Connect graph, guaranteed to have a path.
  assert mindist[end] < float("inf")

  path = []
  node = end
  while node != start:
    path.append(node)
    node = distfrom[node]

  path.append(start)
  path.reverse()
  return path

def centrality(graph, count=1000):
  # Node -> int
  weights = defaultdict(int)

  # BFS shortest path for two random nodes in the graph.
  # We assume the graph given to us might be nice with it's centrality.

  nodes = list(graph.keys())

  for _ in range(count):
    n1 = random.choice(nodes)
    n2 = random.choice(nodes)
    if n1 == n2:
      continue

    path = bfs_path(graph, n1, n2)

    for n in path[1:-1]:
      weights[n] += 1

  return weights

def PART1(inputs):
  #print(inputs)
  #print(len(connected_components(inputs)))  

  # This is probably easier to visualize to find the edges.
  #print("graph mygraph {")
  #for node in inputs:
  #  print(f"  {node};")
  #  for e in inputs[node]:
  #    print(f"  {node} -- {e};")
  #print("}")
  # Dot did not like the graph. probably too much interconnectedness. :(

  #compressed, index = compress_cliques(inputs)
  #print("compressed size:", len(compressed), "vs", len(inputs))
  #print("compressed edges:", sum([len(edges) for edges in compressed.values()]), 
  #    "vs", sum([len(edges) for edges in inputs.values()]))

  edges, components = edge_cutting(inputs)
  # Attempt 1: 606062 - right.
  return [len(c) for c in components]

  # An attempt to run Kargers until we get a good answer...but didn't work.
  answer = None
  while not answer:
    k = kargers(inputs)
    cutresult = edge_cutting(k)
    if not cutresult:
      continue

    edges, components = cutresult
    c1, c2 = components
    # inflate components.
    for c in components:
      expanded = set()
      for name in c:
        expanded.update(name.split("-"))
      c.clear()
      c.update(expanded)
    #print(components)
    print(edges, ":", [len(c) for c in components])

def PART2(inputs):
  return "no part 2!"
