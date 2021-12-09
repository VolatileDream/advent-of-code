#!/usr/bin/env python-mr

from collections import defaultdict
from _.data.formatting.blocks import Block

LOAD = "content"
def REWRITE(lines):
  crabs = defaultdict(int)
  for i in lines[0].split(","):
    crabs[int(i)] += 1

  return crabs


def cost(crabs, end):
  # what is the abs delta from all inputs to pos?
  return sum([abs(end - pos) * count for pos, count in crabs.items()])


def width(crabs):
  return (min(crabs), max(crabs))


def best(costs):
  b = None
  c = None
  for value, cost in costs.items():
    if b is None or cost < c:
      b = value
      c = cost
  return (b, c)


def calculate_costs(inputs, cost_fn):
  lo, hi = width(inputs)
  costs = {}
  for i in range(lo, hi + 1):
    costs[i] = cost_fn(inputs, i)

  return costs

def PART1(inputs):
  costs = calculate_costs(inputs, cost)
  #print(costs)
  return best(costs)


def exp_cost(crabs, end):
  def step_cost(steps):
    return (steps + 1) * steps // 2
  return sum([step_cost(abs(end - pos)) * count for pos, count in crabs.items()])


def PART2(inputs):
  costs = calculate_costs(inputs, exp_cost)
  #print(costs)
  return best(costs)
