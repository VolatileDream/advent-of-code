#!/usr/bin/env python3

import argparse
import itertools
import math
import sys

def load_map(f):
  m = {}
  mcol = 0
  for row, line in enumerate(f):
    for col, v in enumerate(line):
      if v == '#':
        m[(col, row)] = True
      mcol = col
  return (m, row, mcol)


def angle(p1, p2):
  y1, x1 = p1
  y2, x2 = p2

  xd = x2 - x1
  yd = y2 - y1

  return math.atan2(yd, xd)


def dist(p1, p2):
  y1, x1 = p1
  y2, x2 = p2

  xd = x2 - x1
  yd = y2 - y1
  
  return math.sqrt(yd ** 2 + xd ** 2)


def p1(space):
  # map of point -> set(angles)
  visible = {}

  for k1 in space.keys():
    visible[k1] = set()
    for k2 in space.keys():
      if k1 == k2:
        continue
      visible[k1].add(angle(k1, k2))

  vs = [ len(v) for v in visible.values() ]
  m = max(vs)
  print("max visible:", m)

  for k, v in visible.items():
    if len(v) == m:
      return k, v


def normalize(angle):
  return (angle - math.pi + 2 * math.pi) % (math.pi * 2)


def destroy_asteroids(targets):
  if len(targets) < 2:
    #print("done destroying", targets)
    return targets

  destroyed = []
  passed = []
  last_angle = math.pi * 2
  idx = len(targets) - 1
  while idx >= 0:
    angle, dist, pos = targets[idx]
    if last_angle != angle:
      last_angle = angle
      destroyed.append(targets.pop(idx))
      #print("destroying", pos, "left:", len(targets))
    else:
      passed.append(targets.pop(idx))
    idx -= 1

  return destroyed + destroy_asteroids(passed)


def p2(space, k1):
  # map of point -> angle
  #visible = {}
  #for k2 in space.keys():
  #  if k1 == k2:
  #    continue
  #  visible[k2] = angle(k1, k2)

  # need list[angle -> distance)
  # iterate through it, if 2+
  # consecutive angles are the same, ignore.
  l = []
  for k2 in space.keys():
    if k1 == k2:
      continue
    l.append((normalize(angle(k1, k2)), dist(k1, k2), k2))

  # angles have been normalized to the lazer.
  # lazer rotates towards negative direction.
    
  # sort 2 ways, because sorting is stable.
  l = sorted(l, key=lambda x: x[1], reverse=True)
  targets = sorted(l, key=lambda x: x[0])
  # fix items with angle zero -> they go on the end.
  zeros = itertools.takewhile(lambda x: x[0] == 0, targets)
  others = itertools.dropwhile(lambda x: x[0] == 0, targets)
  targets = list(others) + list(zeros)
  #[ print(t) for t in targets ]
  destroyed = destroy_asteroids(targets)
  [print(i + 1, t[2]) for i, t in enumerate(destroyed)]
  i200 = destroyed[199]
  print(i200[2][0] * 100 + i200[2][1])


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', type=argparse.FileType('r'), nargs='?', default=sys.stdin)

  args = parser.parse_args(sys.argv[1:])

  (space, rows, cols) = load_map(args.input)

  pos, vis_count = p1(space)
  print("position of max vis", pos)
  p2(space, pos)
