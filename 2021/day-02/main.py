#!/usr/bin/env python-mr

from _.command_line.app import APP
import _.games.advent_of_code.util as util


def move(pos, instr):
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


def day1(instrs):
  pos = (0, 0)
  for i in instrs:
    pos = move(pos, i)

  return pos


def day2(instrs):
  pass

def main():
  instrs = util.load_input()
  print(day1(instrs))
  print(day2(instrs))


if __name__ == "__main__":
  APP.run(main)
