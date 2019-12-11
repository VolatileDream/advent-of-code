#!/usr/bin/env python3

import argparse
import sys

def visit_nodes(graph, node, path_lengths, length=0):
  if node in path_lengths:
    path_lengths[node] = min(path_lengths[node], length)
    return

  path_lengths[node] = length
  if node not in graph:
    print("terminal node:", node)
    return

  children = graph[node]
  for kid in children:
    print("visiting:", node, kid)
    visit_nodes(graph, kid, path_lengths, length + 1)

  return


def path_root(graph, node, find, visited):
  if node in visited:
    return

  if node == find:
    return [find]

  visited.add(node)
  if node not in graph:
    #print("terminal node:", node)
    return

  children = graph[node]
  for kid in children:
    #print("visiting:", node, kid)
    path = path_root(graph, kid, find, visited)
    if path:
      return [node] + path
  return
  

def common_path(path1, path2):
  common = []
  idx = 0
  while path1[idx] == path2[idx]:
    common.append(path1[idx])
    idx += 1
  return (common, path1[idx:], path2[idx:])


def run(f):
  edges = {}
  for line in f:
    closer, farther = line.strip().split(')')
    if closer not in edges:
      edges[closer] = []
    edges[closer] += [farther]
  print(edges)

  lengths = {}
  visit_nodes(edges, 'COM', lengths)
  print(lengths)
  s = 0
  for k,v in lengths.items():
    s += v
  print("length:", s)

  location_you = path_root(edges, 'COM', 'YOU', set())
  location_san = path_root(edges, 'COM', 'SAN', set())
  print(location_you)
  print(location_san)
  common, you, san = common_path(location_you, location_san)
  print("common root path:", common)
  print("you:", you)
  print("san:", san)
  # Remove to because we don't count you & santa.
  print("orbital transfers:", len(you) + len(san) - 2)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', type=argparse.FileType('r'), nargs='?', default=sys.stdin)

  args = parser.parse_args(sys.argv[1:])

  run(args.input)
