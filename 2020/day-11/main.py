#!/usr/bin/python3

import argparse
import collections
import re
import sys
import typing


def load_file(filename):
  contents = []
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip() # remove trailing newline
      contents.append(line)
  return contents


class Position(typing.NamedTuple):
  width: int
  height: int

  def __add__(self, other):
    assert type(other) == Position
    return Position(self.width + other.width, self.height + other.height)


class Seating:
  def __init__(self, width, height, seats):
    self.width = width
    self.height = height
    self.seats = seats
    self.changed = True # makes iterations easier

  @staticmethod
  def __dict():
    # by default return 'void' so that we can catch edges
    # this helps looping code that works on 'while position == .'
    return collections.defaultdict(lambda: ' ')

  @staticmethod
  def from_lines(lines):
    # Convert to internal dict format
    height = len(lines)
    width = len(lines[0])

    # default to floor
    seats = Seating.__dict()

    for h in range(height):
      line = lines[h]
      assert len(line) == width

      for w in range(width):
        seats[Position(w, h)] = line[w]

    return Seating(width, height, seats)

  def __repr__(self):
    out = []
    for h in range(self.height):
      line = ''
      for w in range(self.width):
        line += self.seats[(w, h)]
      out.append(line)
    return '\n'.join(out)

  # Sort of like Conway's game of life.
  def step(self, adj_func, leave_seat_threshold):
    n = Seating.__dict()
    self.changed = False
    for h in range(self.height):
      for w in range(self.width):
        pos = Position(w, h)
        value = self.seats[pos]

        if value == '.':
          n[pos] = value
          continue

        occupied = 0
        for adj in adj_func(self.seats, pos):
          if self.seats[adj] == '#':
            occupied += 1

        if value == 'L' and occupied == 0:
          value = '#'
          self.changed = True
        elif value == '#' and occupied >= leave_seat_threshold:
          value = 'L'
          self.changed = True

        n[pos] = value

    if self.changed:
      return Seating(self.width, self.height, n)
    else:
      return self


def until_stable(seating, *step_args, printer=None):
  steps = 0
  while seating.changed:
    printer(seating)
    seating = seating.step(*step_args)
    steps += 1
    printer()

  #print("steps", steps)
  return seating


def count_states(seating): 
  d = collections.defaultdict(int)
  for v in seating.seats.values():
    d[v] += 1
  return d
  

def directions():
  # left, right, up, down
  yield Position(-1, +0)
  yield Position(+1, +0)
  yield Position(+0, -1)
  yield Position(+0, +1)

  # diagonals
  yield Position(-1, -1)
  yield Position(-1, +1)
  yield Position(+1, -1)
  yield Position(+1, +1)


def p1_adjacent(_seats, pos):
  for p in directions():
    yield pos + p


def part1(things, printer):
  seating = until_stable(things, p1_adjacent, 4, printer=printer)
  counts = count_states(seating)
  return counts['#']


def p2_adjacent(seats, start):
  def until_seat(pos, translate):
    while seats[pos] == '.' or pos == start:
      pos = pos + translate
    return pos

  for p in directions():
    pos = start + p
    while seats[pos] == '.':
      pos = pos + p

    yield pos


def part2(things, printer):
  seating = until_stable(things, p2_adjacent, 5, printer=printer)
  counts = count_states(seating)
  return counts['#']


def main(filename, printer):
  things = Seating.from_lines(load_file(filename))

  print("part 1:", part1(things, printer))
  print("part 2:", part2(things, printer))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')
  parser.add_argument('--print', '-p', action='store_true', default=False)

  printer = lambda *x: None
  args = parser.parse_args(sys.argv[1:])

  if args.print:
    printer = print
  main(args.input, printer)
