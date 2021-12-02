#!/usr/bin/env python-mr

from _.command_line.app import APP


def move1(pos, instr):
  depth, horiz = pos
  direction, distance = instr.split(" ")
  distance = int(distance)
  if direction == "down":
    depth += distance
  elif direction == "forward":
    horiz += distance
  elif direction == "up":
    depth -= distance

  return (depth, horiz)


def PART1(instrs):
  pos = (0, 0)
  for i in instrs:
    pos = move1(pos, i)

  return pos

def move2(pos, instr):
  depth, horiz, aim = pos
  direction, distance = instr.split(" ")
  distance = int(distance)
  if direction == "down":
    aim += distance
  elif direction == "up":
    aim -= distance
  elif direction == "forward":
    horiz += distance
    depth += distance * aim

  return (depth, horiz, aim)


def PART2(instrs):
  pos = (0, 0, 0)
  for i in instrs:
    pos = move2(pos, i)

  return pos


def main():
  import _.games.advent_of_code.main as util
  instrs = util.load_input()
  print(PART1(instrs))
  print(PART2(instrs))


if __name__ == "__main__":
  APP.run(main)
