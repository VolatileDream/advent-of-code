#!/usr/bin/env python-mr

from _.command_line.app import APP
import _.games.advent_of_code.util as util


def adjacent(iterable):
  i1 = iter(iterable)
  i2 = iter(iterable)
  next(i2) # advance by 1
  return zip(i1, i2)


def day1(depths):
  increased = 0
  for prev, now in adjacent(depths):
    if prev < now:
      increased += 1

  return increased


def sum3(iterable):
  i1 = iter(iterable)
  i2 = iter(iterable)
  i3 = iter(iterable)
  next(i2) # advance by 1
  next(i3); next(i3) # advance by 2
  contents = []
  for v1, v2, v3 in zip(i1, i2, i3):
    contents.append(v1 + v2 + v3)
  return contents


def day2(depths):
  sum_of_depths = sum3(depths)
  increased = 0
  for prev, now in adjacent(sum_of_depths):
    if prev < now:
      increased += 1

  return increased


def main():
  depths = [int(d) for d in util.load_input()]
  print(day1(depths))
  print(day2(depths))


if __name__ == "__main__":
  APP.run(main)
