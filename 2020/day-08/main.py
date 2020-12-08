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


class VM:
  def __init__(self, instructions):
    self.pc = 0
    self.acc = 0
    self.instructions = instructions

  @staticmethod
  def instr_from_line(line):
    instr, number = line.split(" ")
    return (instr, int(number))

  @staticmethod
  def load(filename):
    lines = load_file(filename)
    instrs = [VM.instr_from_line(l) for l in lines]
    return VM(instrs)

  @staticmethod
  def __cycles_remain(cycle_count):
    return cycle_count is None or cycle_count > 0

  @staticmethod
  def __cycles_decr(cycle_count):
    if cycle_count is None:
      return None
    return cycle_count - 1

  def terminated(self):
    return self.pc >= len(self.instructions)

  def exec(self, cycles=None):
    while VM.__cycles_remain(cycles):
      cycles = VM.__cycles_decr(cycles)

      if self.terminated():
        return None # Termination
  
      # sometimes we need the pc before increment,
      # and referring to it with a different variable
      # makes it easier
      start_pc = self.pc # pc for the current cycle
      self.pc += 1 # update pc for next cycle
      instr, delta = self.instructions[start_pc]

      if instr == "nop":
        pass # do nothing
      elif instr == "acc":
        self.acc += delta
      elif instr == "jmp":
        self.pc = start_pc + delta

    return self.pc # not clear this is a good idea.


def run_to_loop(things):
  seen = set()

  while things.pc not in seen:
    seen.add(things.pc)
    things.exec(1)

  return things


def part1(things):
  return run_to_loop(things).acc


def instruction_index(vm):
  d = collections.defaultdict(set)

  for i in range(len(vm.instructions)):
    instr, delta = vm.instructions[i]
    d[instr].add(i)

  return d


def find_funny_jmp_nop(things):
  test_instr = set()
  index = instruction_index(things)

  test_instr.update(index["jmp"]) # all jmp are ok.

  # filter nops
  for i in index["nop"]:
    instr, delta = things.instructions[i]
    # For nop check that it won't self loop.
    if delta != 0:
      test_instr.add(i)

  return test_instr
  

def part2(things):
  def create_modified_vm(vm, index):
    instr, delta = things.instructions[index]
    # swap the instruction type.
    if instr == "nop":
      instr = "jmp"
    else:
      instr = "nop"

    copy = list(things.instructions)
    copy[index] = (instr, delta)
    return VM(copy)

  modifications = find_funny_jmp_nop(things)
  # Now we have all the indices to modify

  # hopefully we find it before the termination
  while len(modifications) > 0:
    modify_index = modifications.pop()
    vm = create_modified_vm(things, modify_index)
    run_to_loop(vm)

    if vm.terminated():
      # yay!
      return "index: {}, acc: {}".format(modify_index, vm.acc)

  return -1


def main(filename):
  things = VM.load(filename)

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
