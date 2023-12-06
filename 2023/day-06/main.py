#!/usr/bin/env python-mr

from collections import defaultdict
from typing import NamedTuple
from itertools import zip_longest
from functools import reduce
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

import math

LOAD = "content"
def REWRITE(lines):
  return lines


def dist(wait, time):
  return wait * (time - wait)


def solve_max_distance_range(time, record_distance):
  # This is simple math, it makes a polynomial function for distance.
  # distance(wait) = speed * (time - wait)
  #                = -wait ** 2 + wait * time  # since speed = wait
  # distance'(wait) = -2 wait + time

  # Solve for distance'(wait) = 0.
  # distance'(wait) = -2 wait + time
  #          2 wait = time
  #            wait = time / 2   

  # Optimal:
  # print(time // 2, dist(time//2, time), distance)

  mid = time // 2
  lo, hi = mid, mid

  # Oops. The above math wasn't perfect. If instead we use a different
  # formula for distance, we can avoid the loops.
  # better-distance(wait) = speed * (time - wait) - record_distance
  #                       = -wait**2 + wait * time - record_distance
  # Solve for the zeros here, and that's where we tie the record.
  #
  # x = (-b +- sqrt(b**2 - 4ac) ) / 2a
  #   = (-time +- sqrt(time*time - 4 * -1 * -record_distance)) / -2
  #   = (-time +- sqrt(time*time - 4 * record_distance)) / -2
  #   = time/2 +- sqrt(time*time - 4 * record_distance)/2

  s = math.sqrt(time * time - 4 * record_distance) / 2
  t = time / 2

  # If you use lo=ceil(t-s), hi=floor(t+s) you need to probe out for the answer.
  lo = math.floor(t - s)
  hi = math.ceil(t + s)
  #print("quad", t, s)

  # Now that we have very good estimates for where we beat the record,
  # probe out to make sure we're exact. A better evaluation of the math
  # might remove the need for this.
  #
  #while dist(lo, time) > record_distance:
  #  lo -= 1
  #while dist(hi, time) > record_distance:
  #  hi += 1
  #print("hilo", lo, hi)
  
  #print("opts", hi - lo - 1)
  return hi - lo - 1

def PART1(inputs):
  times, distances = inputs
  print(times)
  print(distances)
  times = read_numbers(times)
  distances = read_numbers(distances)

  opts = []
  for (time, distance) in zip_longest(times, distances):
    # print(time, distance)
    opts.append(solve_max_distance_range(time, distance))

  return reduce(lambda x, y: x * y, opts, 1)


def PART2(inputs):
  times, distances = [i.replace(" ", "") for i in inputs]
  print(times)
  print(distances)
  times = read_numbers(times)
  distances = read_numbers(distances)

  def dist(wait, time):
    return wait * (time - wait)

  opts = []
  for (time, distance) in zip_longest(times, distances):
    # print(time, distance)
    opts.append(solve_max_distance_range(time, distance))

  return reduce(lambda x, y: x * y, opts, 1)
