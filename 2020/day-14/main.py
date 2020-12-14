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


class Mask:
  def __init__(self, val):
    self.repr = val
    self.set = int(val.replace("X", "0"), base=2)
    self.unset = int(val.replace("X", "1"), base=2)

  def apply(self, value):
    return (value & self.unset) | self.set

  def __repr__(self):
    return self.repr
    

def part1(instrs):
  mask = Mask("X")
  memory = {}

  for i in instrs:
    command, value = i.split(" = ")
    if command == "mask":
      mask = Mask(value)
    else:
      addr = command[len("mem["):-1]
      value = int(value)
      memory[addr] = mask.apply(value)

  return sum(memory.values())


class Mask2:
  def __init__(self, val):
    self.val = val # original
    # contains only bits to set
    self.ones = int(val.replace("X", "0"), base=2)
    # remove the set bits
    self.float = val.replace("1", "0")
    self.float_mask = ~int(self.float.replace("X", "1"), base=2)

  def __repr__(self):
    return self.val

  def range(self):
    return 2 ** self.val.count("X")

  @staticmethod
  def replace(string, value):
    # replace X with bit from value.
    out = 0
    for c in string:
      if c == "X":
        c = value & 0x1
        value = value >> 1
      else:
        c = int(c, base=2)

      out = out << 1
      out = out | c

    return out

  def apply(self, value):
    # Evaluate floating bits from mask.
    #print("mask", self, "with range", self.range())
    #print("float mask", self.float_mask)
    #print("set mask", self.ones)
    value &= self.float_mask
    value |= self.ones
    for i in range(self.range()):
      val = Mask2.replace(self.val, i)
      yield value | val


def part2(instrs):
  mask = Mask2("X") # gets replaced at first instruction
  memory = {}

  for i in instrs:
    command, value = i.split(" = ")
    if command == "mask":
      mask = Mask2(value)
    else:
      base_addr = int(command[len("mem["):-1])
      value = int(value)
      #print("base address:", base_addr)
      for addr in mask.apply(base_addr):
        #print("mem[", addr, "] =", value)
        memory[addr] = value

  return sum(memory.values())


def main(filename):
  things = load_file(filename)

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
