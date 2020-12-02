#!/usr/bin/env python3

import argparse
import enum
import functools
import collections
import sys

# General day 2 stuff

class IntCodeProgramType(object):
  def __repr__(self):
    return 'IntCodeProgramType'

  def __call__(self, string):
    f = None
    if string == "-":
      f = sys.stdin
    else:
      f = open(string, mode='r')

    # We plan to consume all of the contents. 
    try:
      contents = []
      for line in f:
        line = line.strip()
        if not line or line.startswith("#"):
          continue
        contents.extend(line.split(','))
      return [ int(i) for i in contents ]
    finally:
      f.close()


IntCodeStatus = collections.namedtuple("IntCodeStatus", ["status", "value"])

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
      recv=self.io_in()
      self.mem(args[0], mode0, val=recv)
      return IntCodeStatus("io", recv)
    elif instr == 4:
      send = self.mem(args[0], mode0)
      self.io_out(send)
      return IntCodeStatus("io", send)
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
      # Reset the PC, we won't ever do anything again.
      # This is _just_ in case something funny happens.
      self.program_counter = pc
      return IntCodeStatus("exit", 0)
    else:
      raise Exception("invalid instruction: %s at index: " % (str(instr), self.program_counter))
    return IntCodeStatus("running", pc)

  def run(self):
    out = None
    while True:
      if out.status == "exit" or self.steps == self.cycle_counter:
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


def aa(size):
  "Creates an array of arrays for the given size"
  a = []
  for i in range(size):
    a.append([])
  return a


class Router(object):
  def __init__(self, size, handler=None):
    self.packets = aa(size)
    self.outgoing= aa(size)
    self.size = size
    self.handler = handler
    self.nat = (0, 0)

  def raw_send(self, addr, *args):
    self.packets[addr].extend(args)

  def network_idle(self):
    print("idle!")
    print("send:", 255, "->", 0, "==", *self.nat)
    self.raw_send(0, *self.nat)

  def do_send(self, sender, v):
    out = self.outgoing[sender]
    out.append(v)
    if len(out) >= 3:
      addr, x, y, *rest = out
      print("send:", sender, "->", addr, "==", x, y)
      if addr == 255:
        self.nat = (x, y)
      elif addr >= self.size:
        # Bad addr.
        self.handler(addr, x, y)
      else:
        # Send x,y to addr
        self.raw_send(addr, x, y)
        # Replace the outgoing list with whatever was left.
        self.outgoing[sender] = rest

  def do_recv(self, addr):
    if self.pending(addr):
      return self.packets[addr].pop(0)
    return -1

  def any_pending(self):
    result = False
    for i in range(self.size):
      result = result or self.pending(i)
    return result

  def pending(self, addr):
    return len(self.packets[addr]) > 0

  def bind_send(self, addr):
    # Create a function to bind sending from a particular address
    def send_func(val):
      self.do_send(addr, val)
    return send_func

  def bind_recv(self, addr):
    def recv_func():
      return self.do_recv(addr)
    return recv_func


class Network(object):
  def __init__(self, size, program):
    self.read_count = { i: 0 for i in range(size) }
    self.size = size
    self.executing = True
    self.router = Router(size, self.error_handler)
    self.machines = []

    # Initialize the initial packets
    for i in range(size):
      self.router.raw_send(i, i)

    # Initialize the machines.
    for i in range(size):
      m = IntCode(0, self.router.bind_recv(i), self.router.bind_send(i))
      m.memory = list(program) # SUPER IMPORTANT TO CREATE A COPY
      self.machines.append(m)

  def error_handler(self, addr, x, y):
    print("error:", addr, x, y)
    self.executing = False

  def all_reading(self, threshold=5):
    result = True
    for r in self.read_count.values():
      result = result and r > threshold
    return result

  def exec(self):
    # Execute a single instruction across all the IntCode computers.
    for i in range(self.size):
      m = self.machines[i]
      (status, value) = m.exec()
      if status == "io":
        if value == -1:
          self.read_count[i] += 1
        else:
          self.read_count[i] = 0

  def run(self):
    i = 0
    while self.executing:
      i += 1
      if i % 10000 == 0:
        print('.', end='', flush=True)
      self.exec()

      if self.all_reading(15) and not self.router.any_pending():
        self.router.network_idle()


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('program', type=IntCodeProgramType(), nargs='?', default=[99,0,0,0])

  args = parser.parse_args(sys.argv[1:])

  # Pad out the program to 4096 bytes.
  program = args.program
  program.extend([0] * (4096 - len(program)))
  #print(args.program)
  n = Network(size=50, program=program)

  n.run()
  #for i in range(100):
  #  n.exec()
