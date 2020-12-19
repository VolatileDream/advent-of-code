#!/usr/bin/python3

import argparse
import collections
import functools
import itertools
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


def load_groups(filename):
  # because some files follow this format instead.
  contents = []
  acc = [] 
  for line in load_file(filename):
    if line:
      acc.append(line)
    else:
      contents.append(acc)
      acc = []

  if acc:
    contents.append(acc)

  return contents


# FROM: https://docs.python.org/3/library/itertools.html#itertools-recipes
def grouper(iterable, n, fillvalue=None):
    "Collect data into fixed-length chunks or blocks"
    # grouper('ABCDEFG', 3, 'x') --> ABC DEF Gxx"
    args = [iter(iterable)] * n
    return itertools.zip_longest(*args, fillvalue=fillvalue)


class MessageParser:
  @staticmethod
  def __rule_match(line):
    s = line.split(" ")
    return tuple([int(i) for i in line.split(" ")])

  @staticmethod
  def from_lines(lines):
    # the dict has the following structure:
    # [int] = list(value)
    # value = str | tuple(int+)
    rules = {}
    for line in lines:
      key, match = line.split(": ")
      key = int(key)
      if "\"" in match:
        rules[key] = [match[1:-1]]
      elif "|" in match:
        m1, m2 = match.split(" | ")
        rules[key] = [MessageParser.__rule_match(m1), MessageParser.__rule_match(m2)]
      else:
        rules[key] = [MessageParser.__rule_match(match)]

    return MessageParser(rules)

  def __init__(self, rules):
    self.rules = rules
    self.matches = None

  def __repr__(self):
    return "MessageParser({})".format(repr(self.rules))

  def __matching(cache, rules, num):
    if num in cache:
      return cache[num]

    # generate all the matches for this rule.
    assert type(num) == int
    #print("generating", num, flush=True)

    rule = rules[num]

    # every rule is a list of matching things.
    matches = []
    for subrule in rule:
      if type(subrule) == str:
        matches.append(subrule)
      else:
        submatches = [MessageParser.__matching(cache, rules, r) for r in subrule]
        #print("submatch", num, submatches, flush=True)
        expanded = ["".join(t) for t in itertools.product(*submatches)]
        #print("expanded", num, expanded, flush=True)
        matches.extend(expanded)

    #print("generated", num, "value", matches, "from", rules[num], flush=True)
    cache[num] = matches
    return cache[num]

  def __gen_matches(self):
    # generate all matches.
    cache = {}
    return (cache, MessageParser.__matching(cache, self.rules, 0))

  def allmatching(self):
    if self.matches is None:
      self.matches = self.__gen_matches()
    return self.matches[1]

  def part2_match(self, value):
    assert self.rules[0] == [(8, 11)]
    cache = self.matches[0]
    rule42 = cache[42]
    rule31 = cache[31]

    # The new 8 & 11 rules:
    # 8: 42 | 42 8
    # 11: 42 31 | 42 11 31
    #
    # equivalent (ish):
    #
    # 8 can be seen as: 42 +
    # 11 is approximately matching brackets
    #
    # this makes rule 0:
    # 42 + 42 {n} 31 {n}

    # since everything in rule42 and rule31 has length 8 we can chunk the input. :)
    if len(value) % 8 != 0:
      return False

    chunked = ["".join(g) for g in grouper(value, 8)]
    #print("chunked", chunked)

    if len(chunked) == 3:
      # easy case
      return chunked[0] in rule42 and chunked[1] in rule42 and chunked[2] in rule31

    # recall we are trying to match:
    # 42 + 42 {n} 31 {n}
    for c in range(1, len(chunked)):
      n = (len(chunked) - c) // 2
      if n * 2 + c != len(chunked):
        continue

      # check the first `c` items for being in 42.
      # then the next `n` in 42, and the last `n` in 31.
      #
      # > c + n in 42, n in 31.

      match = True
      for i, v in enumerate(chunked):
        if i < c + n:
          match = match and v in rule42
        else:
          match = match and v in rule31

      if match:
        return True

    return False


def parseit(things):
  return (MessageParser.from_lines(things[0]), things[1])


def part1(things):
  parser, messages = things

  matches = parser.allmatching()

  count = 0
  for m in messages:
    #print("checking", m)
    if m in matches:
      #print("matches!")
      count += 1

  return count


def part2(things):
  parser, messages = things

  # part2 changes 2 rules at the root of matching stuff.
  print("42:", len(parser.matches[0][42]))
  print("31:", len(parser.matches[0][31]))

  # all of the rules have length 8
  for r in parser.matches[0][42]:
    assert len(r) == 8
  for r in parser.matches[0][31]:
    assert len(r) == 8

  count = 0
  for m in messages:
    #print("checking", m)
    if parser.part2_match(m):
      #print("matches!")
      count += 1

  return count

def main(filename):
  things = parseit(load_groups(filename))

  print(things[0])
  print(len(things[0].allmatching()))
  print()

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
