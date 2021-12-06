#!/usr/bin/env python-mr

from collections import defaultdict
from _.data.formatting.blocks import Block

class LanternFishSwarm:
  @staticmethod
  def from_list(days):
    state = defaultdict(int)
    for d in days:
      state[d] += 1
    return LanternFishSwarm(state)

  def __init__(self, state):
    # Map counting days remaining -> # of fish
    self._days = state

  def __str__(self):
    remaining = []
    for days, count in self._days.items():
      remaining.append(",".join([str(days)] * count))
    return ",".join(remaining)

  def count_fish(self):
    return sum(self._days.values())

  def increment_days(self) -> "LanternFishSwarm":
    next_state = defaultdict(int)
    for i in self._days:
      if i == 0:
        next_state[6] += self._days[i]
        next_state[8] += self._days[i]
      else:
        next_state[i - 1] += self._days[i]

    return LanternFishSwarm(next_state)


LOAD = "content"
def REWRITE(lines):
  state, = lines
  return LanternFishSwarm.from_list([int(i) for i in state.split(",")])


def PART1(inputs):
  #print(inputs)
  swarm = inputs
  for _day in range(80):
    swarm = swarm.increment_days()
    #print(swarm)

  #print("Fish", swarm.count_fish())
  return swarm.count_fish()
  

def PART2(inputs):
  #print(inputs)
  swarm = inputs
  for _day in range(256):
    swarm = swarm.increment_days()
    #print(swarm)

  #print("Fish", swarm.count_fish())
  return swarm.count_fish()
