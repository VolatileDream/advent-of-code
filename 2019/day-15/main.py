#!/usr/bin/env python3

import argparse
import collections
import sys

# General day 2 stuff

class IntCode(object):

  INSTR_ZERO= set([99])
  INSTR_ONE = set([3, 4, 9])
  INSTR_TWO = set([5, 6])
  INSTR_THREE= set([1, 2, 7, 8])

  def __init__(self, size, io_in, io_out):
    self.memory = [0] * size
    self.relative_offset = 0
    self.program_counter = 0
    self.cycle_counter = 0
    self.steps = -1
    self.io_in = io_in
    self.io_out = io_out

  def instr_args(self, instr):
    """returns the number of arguments for a given instruction"""
    if instr in IntCode.INSTR_ZERO:
      return 0
    elif instr in IntCode.INSTR_ONE:
      return 1
    elif instr in IntCode.INSTR_TWO:
      return 2
    elif instr in IntCode.INSTR_THREE:
      return 3
    else:
      raise Exception("Illegal instruction: %s" % str(instr))

  def decode_modes(self, instr):
    return ((instr // 10000) % 10,
            (instr // 1000) % 10,
            (instr // 100) % 10,
            (instr % 100))

  def exec(self):
    pc = self.program_counter
    pinstr = self.memory[pc]
    # Not all modes may be applicable, they're fetched anyway.
    mode2, mode1, mode0, instr = self.decode_modes(pinstr)
    argc = self.instr_args(instr)
    args = self.memory[pc + 1:pc + 1 + argc]
    
    self.cycle_counter += 1
    # Jumps reset this later.
    self.program_counter += argc + 1
    if instr == 1:
      self.mem(args[2], mode2,
          val=self.mem(args[0], mode0) + self.mem(args[1], mode1))
    elif instr == 2:
      self.mem(args[2], mode2,
          val=self.mem(args[0], mode0) * self.mem(args[1], mode1))
    elif instr == 3:
      self.mem(args[0], mode0, val=self.io_in())
      #raise Exception("not implemented")
    elif instr == 4:
      self.io_out(self.mem(args[0], mode0))
      #raise Exception("not implemented")
    elif instr == 5:
      if self.mem(args[0], mode0) != 0:
        # we increment program counter later.
        self.program_counter = self.mem(args[1], mode1)
    elif instr == 6:
      if self.mem(args[0], mode0) == 0:
        # we increment program counter later.
        self.program_counter = self.mem(args[1], mode1)
    elif instr == 7:
      self.mem(args[2], mode2,
          val=int(self.mem(args[0], mode0) < self.mem(args[1], mode1)))
    elif instr == 8:
      self.mem(args[2], mode2,
          val=int(self.mem(args[0], mode0) == self.mem(args[1], mode1)))
    elif instr == 9:
      self.relative_offset += self.mem(args[0], mode0)
    elif instr == 99:
      return "exit"
    else:
      raise Exception("invalid instruction: %s at index: " % (str(instr), self.program_counter))
    return None

  def run(self):
    out = None
    while True:
      if out == "exit" or self.steps == self.cycle_counter:
        break
      out = self.exec()

  def mem(self, arg, mode, *, val=None):
    if mode not in [0, 1, 2]:
      raise Exception("bad mode: %s" % mode)
    if val is not None:
      # data write
      if mode == 0:
        self.memory[arg] = val
      elif mode == 1:
        raise Exception("illegal mode for write: %s" % mode)
      elif mode == 2:
        self.memory[arg + self.relative_offset] = val
    else:
      if mode == 0:
        return self.memory[arg]
      elif mode == 1:
        return arg
      elif mode == 2:
        return self.memory[arg + self.relative_offset]


class World(object):
  def __init__(self):
    self.grid = collections.defaultdict(lambda: -1)

  def dimensions(self):
    if len(self.grid) == 0:
      return (0, 0)
    xs = [ x for x,y in self.grid.keys() ]
    x_min, x_max = min(xs), max(xs)
    ys = [ y for x,y in self.grid.keys() ]
    y_min, y_max = min(ys), max(ys)
    return (x_max - x_min, y_max - y_min)

  def keys(self):
    return self.grid.keys()

  def __getitem__(self, pos):
    return self.grid[pos]

  def __setitem__(self, pos, value):
    self.grid[pos] = value

  def __repr__(self):
    if len(self.grid) == 0:
      return ""
    # 3 and -1 are special, 3 is used to mark start. -1 for unexplored.
    charmap = {0: '#', 1:' ', 2:'@', 3:'S', -1: '?'}
    # visualize the world.
    xs = [ x for x,y in self.grid.keys() ]
    x_min, x_max = min(xs), max(xs)
    ys = [ y for x,y in self.grid.keys() ]
    y_min, y_max = min(ys), max(ys)

    out = ""
    for y in range(y_min, y_max + 1):
      for x in range(x_min, x_max + 1):
        t = self[(x,y)]
        out += charmap[t]
      out += "\n"

    return out


class RepairDroid(object):
  # Map of int -> direction is weird, change it.
  DIRECTION = [
    1, # north
    4, # east
    2, # south
    3, # west
  ]
  DIR_EXPLAINER = ["up", "right", "down", "left" ]
  # Tuple of (x,y) vectors to move.
  # Same order as DIRECTION list.
  MOVEMENT = [
    (0,1),
    (1,0),
    (0,-1),
    (-1,0),
  ]
  def __init__(self, brain_source, world):
    self.brain = IntCode(0, lambda: self.read(), lambda x: self.write(x))
    self.brain.memory = load(brain_source) + [0] * 4096
    self.world = world
    # Set a start state, needs to be valid for first read op.
    self.pos = (0, 0)
    self.direction = 0
    self.states = set() # detecting complete exploration

    self.world[self.pos] = 1

  def run(self):
    self.brain.run()

  def read(self):
    # Send the droid a command.
    # Attempt a move in the direction we're currently storing.
    if self.ss() in self.states:
      raise Exception("done searching")
    return RepairDroid.DIRECTION[self.direction]

  def write(self, val):
    # Tells us the status of the previous command passed via read.
    # Sets our current state as explored.
    self.states.add(self.ss())
    if val != 0:
      # We can move!
      self.pos = self.npos()
      self.world[self.pos] = val
      # Rotate clockwise to follow the righthand rule.
      self.direction = self.rotate(True)
      if val == 2:
        print("found oxygen system")
    else:
      # couldn't move, mark next position as impassable.
      self.world[self.npos()] = val
      # rotate our direction anti-clockwise (right hand rule)
      self.direction = self.rotate(False)

  def ss(self):
    return (self.pos[0], self.pos[1], self.direction)

  def rotate(self, clockwise):
    if clockwise:
      return (self.direction + 1) % 4
    return (self.direction - 1) % 4

  def npos(self):
    return ta(self.pos, RepairDroid.MOVEMENT[self.direction])


# Add 2 2tuples
def ta(p1, p2):
  x1, y1 = p1
  x2, y2 = p2
  return (x1 + x2, y1 + y2)

def load(f):
  contents = []
  for line in f:
    contents.extend(line.split(','))
  return [ int(i) for i in contents ]


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('program', type=argparse.FileType('r'), nargs='?', default=sys.stdin)

  args = parser.parse_args(sys.argv[1:])

  w = World()
  droid = RepairDroid(args.program, w)
  # Map out the whole station.
  try:
    droid.run()
  except Exception as e:
    print(e)
  except KeyboardInterrupt:
    pass

  w[(0,0)] = 3
  print(w)

  # Calculate distance from Oxygen station to starting position.
  oxygen = None
  for pos in w.keys():
    if w[pos] == 2:
      oxygen = pos
      break

  # Calculate the distance from all places to oxygen.
  distances = { oxygen: 0 }
  examined = set()
  candidates = set([oxygen])
  while len(candidates) > 0:
    pos = candidates.pop()
    examined.add(pos)
    if w[pos] == 0:
      continue
    # check all neighbours for closer distance
    min_neighbour = float("inf")
    for direction in RepairDroid.MOVEMENT:
      neighbour = ta(pos, direction)
      if neighbour in distances:
        min_neighbour = min(min_neighbour, distances[neighbour])
      if neighbour not in examined:
        candidates.add(neighbour)
    # check for start pos.
    if pos not in distances:
      distances[pos] = min_neighbour + 1

  print("distance:", distances[oxygen], distances[(0,0)])
  # Do part 2. whatever that is.

  

