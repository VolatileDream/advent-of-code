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


def any_item(iterable, default=None):
  for i in iterable:
    return i
  return default


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
    # This evaluates almost everything, and these rules are needed later.
    assert self.rules[8] == [(42,)]
    assert self.rules[11] == [(42, 31)]
    # convert rules 42 and 31 into sets, because we perform a bunch of contains
    # checks with those in particular.
    MessageParser.__matching(cache, self.rules, 31)
    MessageParser.__matching(cache, self.rules, 42)
    cache[42] = frozenset(cache[42])
    cache[31] = frozenset(cache[31])
    # making the matching values into a set speeds up all contains checks.
    # 200% worth it.
    matches = frozenset(MessageParser.__matching(cache, self.rules, 0))

    # remove rules 0, 8, and 11 from the cache. They are changed in part 2
    # and we don't want to accidentally rely on them for part 1.
    assert self.rules[0] == [(8, 11)]
    del cache[0]
    del cache[8]
    del cache[11]

    return (cache, matches)

  def gen_cache(self):
    assert self.rules[0] == [(8, 11)]
    assert self.rules[8] == [(42,)]
    assert self.rules[11] == [(42, 31)]

    if self.matches is None:
      self.matches = self.__gen_matches()

  def chunk_size(self):
    self.gen_cache()
    rule42 = self.matches[0][42]
    rule31 = self.matches[0][31]
    p = len(any_item(rule42))
    for r in rule42:
      assert p == len(r)
    for r in rule31:
      assert p == len(r)

    return p

  def count(self):
    self.gen_cache()
    return len(self.matches[1])

  def part1_match(self, value):
    self.gen_cache()
    return value in self.matches[1]

  def part2_match(self, value):
    self.gen_cache()
    assert self.rules[0] == [(8, 11)]
    rule42 = self.matches[0][42]
    rule31 = self.matches[0][31]

    # They have overlap.
    #assert len(rule42.union(rule31)) == 0

    # The new 8 & 11 rules:
    #
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

    # since everything in rule42 and rule31 has the same length we can chunk the input. :)
    chunk_size = self.chunk_size()
    if len(value) % chunk_size != 0:
      return False

    chunked = ["".join(g) for g in grouper(value, chunk_size)]
    #print("chunked", chunked)

    # recall we are trying to match:
    #
    # 42+ 42{n} 31{n}
    #
    # Rule 11 looks like bracket matching, but because we have rule 8
    # we can greedily match rule 42, and once we stop matching it, the rest
    # must match rule 31. However (!) we must make sure that we have more
    # matches against rule 42 than 31, because rule 8 requires at least 1
    # match.
    #
    # Therefore we end up with:
    #
    # 42{x} 31{y} ; x > y

    i = 0 # for 
    for i in range(len(chunked)):
      # i isn't shadowed, it updates
      if chunked[i] not in rule42:
        break

    count42 = i

    for i in range(i, len(chunked)):
      if chunked[i] not in rule31:
        return False

    return count42 > len(chunked) - count42


def parseit(things):
  return (MessageParser.from_lines(things[0]), things[1])


def part1(things):
  parser, messages = things

  count = 0
  for m in messages:
    #print("checking", m)
    if parser.part1_match(m):
      #print("matches!")
      count += 1

  return count


def part2(things):
  parser, messages = things

  # part2 changes 2 rules at the root of matching stuff.
  print("42:", len(parser.matches[0][42]))
  print("31:", len(parser.matches[0][31]))

  count = 0
  for m in messages:
    #print("checking", m)
    if parser.part2_match(m):
      #print("matches!")
      count += 1

  return count


def main(filename):
  things = parseit(load_groups(filename))

  #print(things[0])
  print("matching strings (part 1):", things[0].count())
  print()

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
