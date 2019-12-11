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
  ROTATION = [
    (0,1),
    (1,0),
    (0,-1),
    (-1,0),
  ]
  def __init__(self, start=0):
    self.grid = collections.defaultdict(lambda: 0)
    self.pos = (0,0)
    self.direction = (0, 1)

    self[self.pos] = start

  def rotate(self, val):
    assert val == 1 or val == 0
    if val == 0:
      val = -1
    idx = World.ROTATION.index(self.direction)
    idx += val
    self.direction = World.ROTATION[idx % len(World.ROTATION)]

  def move(self):
    x1, y1 = self.pos
    x2, y2 = self.direction
    self.pos = (x1 + x2, y1 + y2)

  def __getitem__(self, pos):
    return self.grid[pos]

  def __setitem__(self, pos, value):
    self.grid[pos] = value


class Robot(object):
  def __init__(self, brain_file, world):
    self.brain = IntCode(0, lambda: self.read(), lambda x: self.write(x))
    self.brain.memory = load(brain_file) + [0] * 4096
    self.world = world
    self.io_count = 0

  def run(self):
    self.brain.run()

  def read(self):
    r =  self.world[self.world.pos]
    #print("reading:", r)
    return r

  def write(self, val):
    if self.io_count % 2 == 0:
      #print("painting", self.world.pos, "to", val)
      self.world[self.world.pos] = val
    else:
      #print("rotating", val)
      self.world.rotate(val)
      self.world.move()
    self.io_count += 1


def load(f):
  contents = []
  for line in f:
    contents.extend(line.split(','))
  return [ int(i) for i in contents ]


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('program', type=argparse.FileType('r'), nargs='?', default=sys.stdin)
  parser.add_argument('--steps', default=None, type=int)

  args = parser.parse_args(sys.argv[1:])

  # Set to 0 for part 1
  # Set to 1 for part 2
  w = World(1)
  rob = Robot(args.program, w)
  rob.run()

  print("painted panels:", len(w.grid))

  # visualize the World.
  xs = [ x for x,y in w.grid.keys() ]
  x_min, x_max = min(xs), max(xs)
  ys = [ y for x,y in w.grid.keys() ]
  y_min, y_max = min(ys), max(ys)

  print("min", x_min, y_min)
  print("max", x_max, y_max)

  # was upside down when goin ymin -> ymax,
  # so instead go the other way.
  for y in reversed(range(y_min, y_max + 1)):
    for x in range(x_min, x_max + 1):
      paint = w[(x,y)]
      if paint:
        print('#', end='')
      else:
        print(' ', end='')
    print()

