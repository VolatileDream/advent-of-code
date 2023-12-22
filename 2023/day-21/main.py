#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.data.structures.point import Point
from _.games.advent_of_code.utils import read_numbers

import functools

def abs(x):
  if x < 0:
    return -x
  return x

LOAD = "content"
def REWRITE(lines):
  size = (len(lines), len(lines[0]))

  grid = {}
  for row, line in enumerate(lines):
    for col, val in enumerate(line):
      if val != ".":
        grid[Point(row, col)] = val
  return (size, grid)

def printgrid(size, grid, reached=set()):
  maxrow, maxcol = size
  b = Block()
  for r in range(maxrow):
    row = Block()
    for c in range(maxcol):
      p = Point(r, c)
      if p not in grid and p not in reached:
        row += "."
      elif p in reached:
        row += "O"
      else:
        row += grid[p]
    b |= row

  return str(b)

DIRECTIONS = {
  # Row, column - (0,0) in the top-left.
  "UP": Point(-1, 0),
  "DOWN": Point(+1, 0),
  "LEFT": Point(0, -1),
  "RIGHT": Point(0, +1)
}

def TEST(inputs):
  pass

def grid_rock(grid, pos):
  return grid.get(pos, ".") == "#"

# There are only a few spots that can be reached in 2 steps:
#   O
#  O.O
# O.S.O
#  O.O
#   O
# any of these can be blocked off if the bottom, top or sides
# are covered with a rock.
#
# 1)   O    2)   .
#     O.O       O#X
#    X#S.O     O.S#.
#     O.O       O.O
#      O         O
# If the top, bottom, sides are covered: then the corresponding
# double move can not be done (1). If two adjacent sides are
# covered, then the diagonal move can not be done (2).
REACH_PATHS = [
  # (Position, possible points to there)
  (Point(-2, 0), (Point(-1, 0),)),
  (Point(+2, 0), (Point(+1, 0),)),
  (Point(0, -2), (Point(0, -1),)),
  (Point(0, +2), (Point(0, +1),)),
  
  (Point(-1, -1), (Point(-1, 0), Point(0, -1),)),
  (Point(+1, +1), (Point(+1, 0), Point(0, +1),)),
  (Point(-1, +1), (Point(0, +1), Point(-1, 0),)),
  (Point(+1, -1), (Point(0, -1), Point(+1, 0),)),
]  

def steponce(grid, reached):
  spots = set()
  for r in reached:
    for d in DIRECTIONS.values():
      n = r + d
      if not grid_rock(grid, n):
        spots.add(n)
  return spots 

def stepforward(grid, reached, steps):
  process = set(reached)
  seen = set(reached)
  while steps > 1:
    new = set()
    steps -= 2
    while process:
      p = process.pop()
      for offset, checks in REACH_PATHS:
        n = p + offset
        if n in seen:
          continue
        if grid_rock(grid, n):
          continue
        for c in checks:
          if not grid_rock(grid, p + c):
            new.add(n)
            break
    seen.update(new)
    process = new

  if steps == 1:
    return steponce(grid, seen)
  else:
    return seen

def reachable(grid, start, steps, ring=False, cache=None):
  if cache is None:
    cache = {}

  cachestate = (id(grid), id(start), steps, ring)
  if cachestate in cache:
    #print(f"hit {cachestate}")
    pass
  else:
    #print(f"miss {cachestate}")
    cache[cachestate] = __reachable(grid, start, steps, ring, cache)

  return cache[cachestate]

def __reachable(grid, start, steps, ring, cache):
  # This builds on the theory that points reachable in 2n steps
  # slowly make an ever expanding ring where you can remove the
  # points reachable from 2(n-1) steps. And we can avoid processing
  # steps that we've already seen since each reachable spot because
  # every spot we can reach in 2y steps can be visited in 2x steps
  # by going back and forth between adjacent spots.
  #
  #                      O
  #                     O.O
  #    .       O       O.X.O
  #   ...     O.O     O.X.X.O
  #  ..O.. > O.X.O > O.X.X.X.O
  #   ...     O.O     O.X.X.O
  #    .       O       O.X.O
  #                     O.O
  #                      O
  #
  assert steps % 2 == 0
  # This is the same regardless of ring=True/False
  if steps == 0:
    return set([start])

  reach = set()
  prev_ring = reachable(grid, start, steps - 2, ring=True, cache=cache) 
  seen = reachable(grid, start, steps - 2, ring=False, cache=cache)
  for p in prev_ring:
    for offset, checks in REACH_PATHS:
      n = p + offset
      if n in seen:
        continue
      if grid_rock(grid, n):
        continue
      for c in checks:
        if not grid_rock(grid, p + c):
          reach.add(n)
          break

  if ring:
    return reach
  else:
    return seen.union(reach)

def PART1(inputs):
  #print(inputs)
  size, grid = inputs
  #print(printgrid(*inputs))
  #print(size)

  start = next(filter(lambda x: x[1] == "S", grid.items()))[0]
  print(start)

  cache = {}
  for steps in range(0, 33, 2):
    r = reachable(grid, start, steps, ring=False, cache=cache)
    #print(steps, ">", len(r))
    #print(printgrid(size, grid, r))
  r = reachable(grid, start, 64, ring=False, cache=cache)
  r65 = steponce(grid, r)
  print(printgrid(size, grid, r65))
  # Attempt 1: 954 - too low
  return len(r)

@dataclass
class RepeatingGrid:
  rows: int
  cols: int
  base: dict[Point, str]

  def get(self, value, default):
    if value not in self:
      return default
    return self[value]

  def __contains__(self, val):
    x, y = (val.x % self.rows, val.y % self.cols)
    return Point(x, y) in self.base

  def __getitem__(self, val):
    x, y = (val.x % self.rows, val.y % self.cols)
    return self.base[Point(x, y)]

def partition_grid_cells(infgrid, reached):
  squares = defaultdict(set)
  for p in reached:
    xC, xT = divmod(p.x, infgrid.rows)
    yC, yT = divmod(p.y, infgrid.cols)
    squares[Point(xC, yC)].add(Point(xT, yT))

  return squares

def propagation_cycle(infgrid, start, cache):
  orthogonals = None
  diagonals = None

  # since the start has infinite free propagation it should take 133 steps
  # for it to create a front on the orthogonal grids, and have them all reach
  # it's starting position.

  assert infgrid.rows == infgrid.cols, f"uneven rows vs colums: {infgrid.rows} x {infgrid.cols}"

  steps = infgrid.rows - (infgrid.rows % 2)
  rStart = reachable(infgrid, start, steps, ring=False, cache=cache)
  if infgrid.rows % 2 != 0:
    rStart = steponce(infgrid, rStart)

  # Check which "infinite" grid squares have things in them, we should only
  # see points with length 1.

  first_part = partition_grid_cells(infgrid, rStart)
  assert set(first_part.keys()) == set([Point(0, 0)] + list(DIRECTIONS.values()))

  # When we go to 266 squares we should see a stable diagonal front.
  rDouble = reachable(infgrid, start, infgrid.rows * 2, ring=False, cache=cache)
  second_part = partition_grid_cells(infgrid, rDouble)

  # Check that this actually creates a cycle on the orthogonals.
  assert len(second_part) == 13
  assert Point(-2, -2) not in second_part
  assert second_part[Point(-2, 0)] == first_part[Point(-1, 0)]
  assert second_part[Point(+2, 0)] == first_part[Point(+1, 0)]
  assert second_part[Point(0, -2)] == first_part[Point(0, -1)]
  assert second_part[Point(0, +2)] == first_part[Point(0, +1)]

  # If we do it a third time, we should see this for the diagonals too.
  if False:
    steps3 = infgrid.rows * 3 - (infgrid.rows % 2)
    rThree = reachable(infgrid, start, steps3, ring=False, cache=cache)
    if infgrid.rows % 2 != 0:
      rThree = steponce(infgrid, rThree)

    third_part = partition_grid_cells(infgrid, rThree)
    assert len(third_part) == 25
    # The orthogonals should still match.
    assert third_part[Point(-3, 0)] == first_part[Point(-1, 0)]
    assert third_part[Point(+3, 0)] == first_part[Point(+1, 0)]
    assert third_part[Point(0, -3)] == first_part[Point(0, -1)]
    assert third_part[Point(0, +3)] == first_part[Point(0, +1)]
    # Check the diagonals.
    # Left + Up
    assert third_part[Point(-2, -1)] == third_part[Point(-1, -2)]
    assert third_part[Point(-2, -1)] == second_part[Point(-1, -1)]
    # Right + Up
    assert third_part[Point(-2, +1)] == third_part[Point(-1, +2)]
    assert third_part[Point(-2, +1)] == second_part[Point(-1, +1)]
    # Right + Down
    assert third_part[Point(+2, +1)] == third_part[Point(+1, +2)]
    assert third_part[Point(+2, +1)] == second_part[Point(+1, +1)]
    # Left + Down
    assert third_part[Point(+2, -1)] == third_part[Point(+1, -2)]
    assert third_part[Point(+2, -1)] == second_part[Point(+1, -1)]

  return second_part

def cell_coverage(cycles):
  # How many grid cells get covered? Each cycle we expand out "one step" like the
  # elf in the puzzle, but have no rocks to check.
  # 1 -> 5 -> 13 -> 25 -> 41  : y = ?
  #   +4   +8   +12   +16     : y = 4x
  #   +4   +4   +4    ...     : y = 4
  #
  # > -1
  # 0 -> 4 -> 12 -> 24 -> 40  : y = 2 * x ( x + 1)
  # > / 4
  # 0 -> 1 ->  3 ->  6 -> 10  : y = 1/2 x ( x + 1 ) = 1/2 x^2 + x/2
  #   +1   +2    +3    +4     : y = x + c
  #   +1   +1    +1    +1     : y = 1
  #
  # We end up with y = 2 * x ( x + 1 ) + 1
  #  y = 2x^2 + 2x + 1
  total = 2 * cycles * (cycles + 1) + 1
  # Number of items in the outer ring, will have partial coverage.
  prev = 2 * (cycles - 1) * cycles + 1
  ring = total - prev
  return (ring, total)


def PART2(inputs):
  size, grid = inputs
  start = next(filter(lambda x: x[1] == "S", grid.items()))[0]
  # grid is infinite, and repeats forever.
  g = RepeatingGrid(size[0], size[1], grid)

  # Part two is waaaaaay too many steps for even the "pretty efficient" solution
  # that I have for part 1. I computed at ~30s for the first 800 steps, and it
  # was clearly getting slower.
  #
  # This visualization [1] shows how you have to do caching & point propagation
  # to make this efficient vs doing it slowly. Basically, there are 8 different
  # components to the propagation front: four arrows (top, bottom, sides) and
  # also four diagonals.
  #
  # 1: https://www.reddit.com/r/adventofcode/comments/18njrqf/2023_day_21_a_diamond_in_the_rough/
  #
  # Once the pattern has propagated into the first loop on the top, bottom, and
  # sides, we will see what those look like at some cycle point (ideally some
  # middle point), after that cycle length passes again, we will see a stable
  # diagonal propagation front as well.
  #
  # At that point, we can compute the number of items in each of our 8 fronts,
  # the number of items in each full grid cell, and then we can go compute how
  # far each of the fronts goes, to find how many of each of the diagonals exist,
  # as well as how many full cells are enclosed by the fronts.
  #
  # Note: this is made easier because the start point can travel straight in all
  # directions, and never gets blocked. yay.

  for row in range(size[0]):
    p = Point(row, start.y)
    if grid_rock(g, p):
      print(f"blocked at {p}")
  for col in range(size[1]):
    p = Point(start.x, col)
    if grid_rock(g, p):
      print(f"blocked at {p}")

  print()
  print(printgrid(size, grid))
  print()

  steps = 26501365

  # It turns out that there is a state cycle!
  # So this becomes a problem of cycle lengths! yay!
  #cells = propagation_cycle(g, start, {})
  cycleLen = g.rows
  cycles, cycleOffset = divmod(steps, cycleLen)

  # here is the ridiculous solution that some other folks came to, by doing
  # polynomial extrapolation. wtf?!

  #r1 = stepforward(g, [start], cycleOffset)
  #r2 = stepforward(g, r1, cycleLen)
  #r3 = stepforward(g, r2, cycleLen)
  #r4 = stepforward(g, r3, cycleLen)

  #p0 = len(r1)
  #p1 = len(r2) - len(r1)
  #p2 = len(r3) - len(r2)
  #p3 = len(r4) - len(r3)
  #print(len(r1), len(r2), len(r3), len(r4))
  #print(p0, p1, p2, p3)

  # p0 and p1 represent the value offset, and then stable offset
  # that exists in the cycles.
  # p1 to p2 is the beginning of the deltas evening out.
  # As evidenced by computing another point and delta.

  # compute sum from (1..x) but for the cycle.
  # this assumes the expansion is linear.
  #return p0 + (p1 * cycles) + (p2 - p1) * (cycles) * (cycles - 1) / 2

  # This is the solution I came to, it is outlined in this [1] post, and I got
  # some of the math wrong at the beginning. :( ouch, it hurts. I managed to
  # correct the math a bit, but it's still wrong.
  #
  # 1: https://www.reddit.com/r/adventofcode/comments/18o4y0m/2023_day_21_part_2_algebraic_solution_using_only/

  #print(cycles, cycleOffset) > 202300 65
  # 65 here is a magic number.
  # I recall that the grid given to us looks like a diamond, and that at 65 iterations
  # different corners of that diamond aren't covered. So we can probably take more
  # shortcuts. yay!
  ringCells, fullCells = cell_coverage(cycles) # 809200, 81850984601
  #print(ringCells, fullCells)

  # We need to compute the number of items in a full cell, and then do something
  # about all the ring cells.
  #twoCycleState = reachable(g, start, cycleLen * 2)
  # If we partition the points, the center cell will be full.
  #pStates = partition_grid_cells(g, twoCycleState)
  # But we must remember that the total step offset is odd!
  centerOnCycle = partition_grid_cells(g, stepforward(g, [start], 3 * cycleLen))[Point(0,0)]
  centerOffCycle = partition_grid_cells(g, steponce(g, centerOnCycle))[Point(0, 0)]

  # Now to determine what happens with the orthogonals and diagonals.
  edges = [Point(start.x, 0), Point(start.x, g.cols - 1), Point(0, start.y), Point(g.rows - 1, start.y)]
  orthogonals = []
  for p in edges:
    # -1 because it reaches that position after 1 step.
    reach = partition_grid_cells(g, stepforward(grid, [p], cycleLen - 1))[Point(0,0)]
    orthogonals.append(len(reach))
  
  #orth = partition_grid_cells(g, stepforward(g, [start], cycleLen + cycleOffset))
  #assert sum(orthogonals) == sum([len(orth[p]) for p in DIRECTIONS.values()])

  # Hypothesis: two kinds of diagonal.
  # * ones that cover all but one corner,
  # * ones that only cover one corner.
  #
  # The first kind are 65 steps forward of the existing diagonals.
  # The second appear as we step the first kind forward 65 steps,
  # and have 1 item in the corner generated on the first step, then
  # 64 more steps.

  corners = [Point(0, 0), Point(0, g.cols - 1), Point(g.rows - 1, 0), Point(g.rows - 1, g.cols - 1)]
  newDiagonalCounts = []
  for p in corners:
    reach = reachable(g, p, cycleOffset - 1)
    #assert reach == stepforward(g, [p], cycleOffset - 1)
    reach = partition_grid_cells(g, reach)[Point(0, 0)]
    newDiagonalCounts.append(len(reach))

  coreDiagonals = []
  for p in corners:
    r = stepforward(g, [p], cycleLen + cycleOffset - 1)
    #assert r == reachable(g, p, cycleLen + cycleOffset)
    r = partition_grid_cells(g, r)[Point(0, 0)]
    coreDiagonals.append(len(r))
      
  # remove orthogonals, and don't double count each diagonal.
  #diagonalCount = (ringCells - 4) // 4
  # assertion from reddit.
  #assert diagonalCount + 1 == cycles, f"{diagonalCount} + 1 == {cycles}"
  #assert fullCells == oddCenterCount + evenCenterCount, f"{fullCells} == {oddCenterCount} + {evenCenterCount}"
  # Attempt 1: 615789441023276 - too low. :(
  #  Maybe it's an off by one?
  # Attempt 2: 615789441027117 - no, too low.
  #  Oh, we forgot to multiply by the number of cycles.
  # Attempt 3: 124574203919008734800 - too high.
  #  oh... no we don't need to multiply by cycles.
  # Looking it up on reddit, the math is wrong.
  # There are two center states, and some of the state math is wrong.
  # Attempt 4: 618267545511408 - also wrong. :(

  answer = (0
      + ((cycles - 1) ** 2) * len(centerOnCycle)
      + ((cycles - 0) ** 2) * len(centerOffCycle)
      + (cycles - 1) * sum(coreDiagonals)
      + (cycles) * sum(newDiagonalCounts)
      + sum(orthogonals)
      + 0)
  # cheating:  618261433219147 is right.
  print("       ", 618261433219147)
  print(f"delta: {618261433219147 - answer}")
  return answer

