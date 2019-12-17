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


# Add 2 2tuples
def ta(p1, p2):
  x1, y1 = p1
  x2, y2 = p2
  return (x1 + x2, y1 + y2)


class Grid(object):
  MOVEMENT = [
    (0,1),
    (1,0),
    (0,-1),
    (-1,0),
  ]
  def __init__(self):
    self.grid = collections.defaultdict(lambda: -1)

  def dimensions(self):
    if len(self.grid) == 0:
      return (0, 0)
    xs = [ x for x,y in self.grid.keys() ]
    x_min, x_max = min(xs), max(xs)
    ys = [ y for x,y in self.grid.keys() ]
    y_min, y_max = min(ys), max(ys)
    return (x_max - x_min + 1, y_max - y_min + 1)

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
    # visualize the world.
    xs = [ x for x,y in self.grid.keys() ]
    x_min, x_max = min(xs), max(xs)
    ys = [ y for x,y in self.grid.keys() ]
    y_min, y_max = min(ys), max(ys)

    out = ""
    for y in range(y_min, y_max + 1):
      for x in range(x_min, x_max + 1):
        t = self[(x,y)]
        out += t
      out += "\n"

    return out

class RepairDroid(object):
  def __init__(self, brain_source, world):
    self.brain = IntCode(0, lambda: self.read(), lambda x: self.write(x))
    self.brain.memory = load(brain_source) + [0] * 4096
    self.world = world
    self.x = 0
    self.y = 0
    # index for read
    self.r = -1
    self.last = 0

  def run(self):
    self.brain.run()

  def read(self):
    """
  L,10,L,12,R,6, -> A
  R,10,L,4,L,4,L,12, -> B
  L,10,L,12,R,6, -> A
  R,10,L,4,L,4,L,12, -> B
  L,10,L,12,R,6, -> A
  L,10,R,10,R,6,L,4, -> C
  R,10,L,4,L,4,L,12, -> B
  L,10,R,10,R,6,L,4, -> C
  L,10,L,12,R,6, -> A
  L,10,R,10,R,6,L,4, -> C
  """
    data = """A,B,A,B,A,C,B,C,A,C
L,10,L,12,R,6
R,10,L,4,L,4,L,12
L,10,R,10,R,6,L,4
n
"""
    self.r += 1
    return ord(data[self.r])

  def write(self, val):
    self.last = val
    print(chr(val), end="")
    return
    if val != 10:
      self.world[(self.x, self.y)] = chr(val)
      self.x += 1
    else:
      self.x = 0
      self.y += 1


def load(f):
  contents = []
  for line in f:
    contents.extend(line.split(','))
  return [ int(i) for i in contents ]

def intersections(w):
  intersections = []
  mx, my = w.dimensions()
  for y in range(my):
    for x in range(mx):
      pos = (x,y)
      if w[pos] != "#":
        print(w[pos], end="")
        continue
      is_intersection = True
      for neighbour in [w[ta(pos, n)] for n in Grid.MOVEMENT]:
        if neighbour != "#":
          is_intersection = False
          break
      if is_intersection:
        intersections.append(pos)
        print("O", end="")
      else:
        print(w[pos], end="")
    print()

  print("sum of intersection squares", sum([x * y for x,y in intersections]))

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('program', type=argparse.FileType('r'), nargs='?', default=sys.stdin)

  args = parser.parse_args(sys.argv[1:])

  w = Grid()
  droid = RepairDroid(args.program, w)
  # Map out the whole station.
  try:
    droid.run()
    print()
    print("dust", droid.last)
  except Exception as e:
    print(e)
  except KeyboardInterrupt:
    pass

  # Solve the maze by hand, compress later.
  # Starting facing up.

  """
  L,10,L,12,R,6,R,10,L,4,L,4,L,12,
  L,10,L,12,R,6,R,10,L,4,L,4,L,12,
  L,10,L,12,R,6,
  L,10,R,10,R,6,L,4,
       R,10,L,4,L,4,L,12,
  L,10,R,10,R,6,L,4,
  L,10,L,12,R,6,
  L,10,R,10,R,6,L4
  """

  """
  L,10,L,12,R,6,
        R,10,L,4,L,4,L,12,
  L,10,L,12,R,6,
        R,10,L,4,L,4,L,12,
  L,10,L,12,R,6,
  L,10,R,10,R,6,L,4,
        R,10,L,4,L,4,L,12,
  L,10 R,10,R,6,L,4,
  L,10,L,12,R,6,
  L,10,R,10,R,6,L4
  """
  #print(w)
  #print("---")
  #print()

  # Find all the intersection points
  #intersections(w)
