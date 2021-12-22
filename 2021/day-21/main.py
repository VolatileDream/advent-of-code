#!/usr/bin/env python-mr

from collections import defaultdict
from itertools import product
from typing import NamedTuple
from _.data.formatting.blocks import Block


class Die:
  def __init__(self):
    self._roll = 0
    self._c = 0

  def roll(self) -> int:
    self._c += 1
    r = self._roll
    self._roll = (self._roll + 1) % 100
    return r + 1

  def __repr__(self):
    return f"Die(rolls={self._c}, next={self._roll})"

def move(position, die):
  return (position + die.roll() + die.roll() + die.roll()) % 10


def play(p1, p2):
  d = Die()
  s1 = 0
  s2 = 0
  while s1 < 1000 and s2 < 1000:
    p1 = move(p1, d)
    s1 += p1 + 1 # position is zero indexed
    if s1 >= 1000:
      break
    p2 = move(p2, d)
    s2 += p2 + 1 # position is zero indexed

  return (s1, s2, d)

def REWRITE(lines):
  # Zero index start positions:
  return (int(lines[0].replace("Player 1 starting position: ", "")) - 1,
          int(lines[1].replace("Player 2 starting position: ", "")) - 1)

def PART1(inputs):
  print(inputs)
  result = play(*inputs)
  print(result)
  s1, s2, die = result
  return min(s1, s2) * die._c


# With quantum dice we want to solve for when a player gets to the score >= 21.

class CountingDict(defaultdict):
  def __add__(self, other):
    if type(self) != type(other):
      return NotImplemented

    keys = set(self.keys()).union(other.keys())
    out = CountingDict(int)
    for k in keys:
      out[k] += self.get(k, 0)
      out[k] += other.get(k, 0)

    return out


class State(NamedTuple):
  p1_position: int
  p2_position: int
  p1_score: int = 0
  p2_score: int = 0
  multiplyer: int = 1


class Wins(NamedTuple):
  p1: int = 0
  p2: int = 0


# Uncached solution, kind of slow.
def play_quantum(p1, p2):
  # Quantum dice roll 1, 2, or 3.
  qdie = (1, 2, 3)
  # The sum of 3 quantum rolls sums from 3 to 9, with repeats.
  rolls = [sum(r) for r in product(qdie, repeat=3)]

  # Map roll -> occurances (cuts down on universes).
  roll_count = defaultdict(int)
  for r in rolls:
    roll_count[r] += 1

  print("roll counts", roll_count)

  wins = Wins()

  progress = 0
  # Parallel universes to play
  remaining = [State(p1, p2)]
  while remaining:
    game = remaining.pop()

    progress += 1
    if not progress % 10000:
      print("In", wins.p1 + wins.p2, "games the outcome is split:", wins)

    while game.p1_score < 21 and game.p2_score < 21:
      #print(game)
      p1, p2, s1, s2, m = game

      outcomes = []
      for p1_roll, p1_m in roll_count.items():
        #print("p1", p1_roll, "happens", p1_m, "times")
        p1n = (p1 + p1_roll) % 10
        s1n = s1 + p1n + 1
        if s1n >= 21:
          wins = Wins(wins.p1 + m * p1_m, wins.p2)
          continue

        for p2_roll, p2_m in roll_count.items():
          #print("p2", p2_roll, "happens", p1_m * p2_m, "times")
          p2n = (p2 + p2_roll) % 10
          s2n = s2 + p2n + 1
          if s2n >= 21:
            wins = Wins(wins.p1, wins.p2 + m * p1_m * p2_m)
            continue

          # Neither p1 nor p2 won, add the state for the next round.
          ns = State(p1n, p2n, s1n, s2n, m * p1_m * p2_m)
          #print(ns)
          outcomes.append(ns)
        # end p2
      # end p1
      if not outcomes:
        break
      # Choose the next game state to compute.
      game = outcomes.pop()
      # Add all the pending game states.
      remaining.extend(outcomes)

  return wins


def faster_quantum(start1, start2):
  # didn't get here at the beginning. needed some help from reading reddit/r/adventofcode
  #
  # Saw lots of caching which made me think of things differently. Only when i started
  # thinking in (score, position) ordering of data did it click that the answer could be
  # computed by building up the solution.

  qdie = (1, 2, 3)
  # The sum of 3 quantum rolls sums from 3 to 9, with repeats.
  rolls = [sum(r) for r in product(qdie, repeat=3)]

  # Map roll -> occurances (cuts down on universes).
  roll_count = defaultdict(int)
  for r in rolls:
    roll_count[r] += 1

  # Rely on building up state as we go.
  # Use a dict[scores, dict[positions, count]] to keep track of the number of
  # parallel universes in this state.
  counts = defaultdict(lambda: defaultdict(int))
  # Score -> Position -> Count
  counts[(0,0)][(start1, start2)] = 1
  wins = Wins()

  # To collapse as many different states together, we attempt to process the
  # games with the lowest scores first, as they are the furthest from ending.
  # eg: (0, 0) -> (3, 3) -> (3, 4) -> (4, 3)
  #     Each of those states will generate at least one (7, 7) state.
  #
  # NOTE: Doing this wrong (using max instead) basically computes games one at
  #       a time, which is very very slow.
  while counts:
    # Find the game with lowest score.
    longest = min(counts, key=lambda a: a[0] + a[1])

    positions = counts[longest]
    del counts[longest] # don't compute them again.

    s1, s2 = longest

    print("computing", longest, sum(positions.values()), "over", len(positions))
    for (p1, p2), count in positions.items():
      # Roll for player 1
      for r1, c1 in roll_count.items():
        pn1 = (p1 + r1) % 10
        sn1 = s1 + pn1 + 1
        if sn1 >= 21:
          wins = Wins(wins.p1 + count * c1, wins.p2)
          continue

        # Only in games that don't end, roll for player 2
        for r2, c2 in roll_count.items():
          pn2 = (p2 + r2) % 10
          sn2 = s2 + pn2 + 1
          if sn2 >= 21:
            wins = Wins(wins.p1, wins.p2 + count * c1 * c2)
            continue

          # No winners, update the game states.
          counts[(sn1, sn2)][(pn1, pn2)] += count * c1 * c2

  return wins


def PART2(inputs):
  #wins = play_quantum(*inputs)
  wins = faster_quantum(*inputs)
  print(wins)
  #return max(wins.p1, wins.p2)
