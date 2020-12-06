#!/usr/bin/python3

import argparse
import collections
import functools
import re
import sys
import typing


def load_file(filename):
  contents = []
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip()
      contents.append(line)
  return contents

def load_answers(filename):
  contents = []
  acc = []
  for line in load_file(filename):
    if line:
      line = Answer(line)
      acc.append(line)
    else:
      contents.append(acc)
      acc = []

  if len(acc) > 0:
    contents.append(acc)

  return contents


class Answer:
  def __init__(self, questions):
    self.questions = set(questions)

  def __len__(self):
    return len(self.questions)

  def union(self, other):
    return Answer(self.questions.union(other.questions))

  def intersect(self, other):
    return Answer(self.questions.intersection(other.questions))

  def __repr__(self):
    return "Answer(questions={})".format(str(self.questions))

  @staticmethod
  def intersect_all(iterable):
    i = iter(iterable)
    first = next(i)
    return functools.reduce(Answer.intersect, i, first)

  @staticmethod
  def union_all(iterable):
    base = Answer(questions=[])
    return functools.reduce(Answer.union, iterable, base)
    

def part1(things):
  count = 0
  for group in things:
    count += len(Answer.union_all(group))

  return count


def part2(things):
  count = 0
  for group in things:
    count += len(Answer.intersect_all(group))

  return count


def main(filename):
  things = load_answers(filename)

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
