#!/usr/bin/env python3

import argparse
import sys

# General day 2 stuff

class IntCode(object):

  INSTR_ZERO= set([99])
  INSTR_ONE = set([3, 4, 9])
  INSTR_TWO = set([5, 6])
  INSTR_THREE= set([1, 2, 7, 8])

  def __init__(self, size):
    self.memory = [0] * size
    self.relative_offset = 0
    self.program_counter = 0
    self.cycle_counter = 0
    self.steps = -1

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
      self.mem(args[0], mode0, val=int(input("")))
      #raise Exception("not implemented")
    elif instr == 4:
      print(self.mem(args[0], mode0))
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
    print("exiting...")

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


def load(f):
  contents = []
  for line in f:
    contents.extend(line.split(','))
  return [ int(i) for i in contents ]


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', type=argparse.FileType('r'), nargs='?', default=sys.stdin)
  parser.add_argument('--steps', default=None, type=int)

  args = parser.parse_args(sys.argv[1:])

  ic = IntCode(0)
  ic.steps = args.steps
  ic.memory = load(args.input) + [0] * 4096

  ic.run()

  print("cycles:", ic.cycle_counter)
  print("first mem:", ic.memory[0])

