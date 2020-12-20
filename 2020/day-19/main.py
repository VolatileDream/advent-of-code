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


# re-implement itertools.product to better handle our use case
# only handles length 
def specialized_product(*args):
  l = len(args)
  assert l == 1 or l == 2
  if l == 1:
    for a in args[0]:
      yield a
    return
  for a in args[0]:
    for b in args[1]:
      yield a + b


def grouper(string, n):
  l = len(string)
  assert l % n == 0
  out = []
  for i in range(l // n):
    offset = i * n
    sub = string[offset:offset + n]
    out.append(sub)
  return out


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
    for i, subrule in enumerate(rule):
      if type(subrule) == str:
        #print("str match", "{}.{}".format(num, i), subrule, flush=True)
        matches.append(subrule)
      else:
        submatches = [MessageParser.__matching(cache, rules, r) for r in subrule]
        #print("submatch", "{}.{}".format(num, i), submatches, flush=True)
        expanded = specialized_product(*submatches)
        #print("expanded", "{}.{}".format(num, i), expanded, flush=True)
        matches.extend(expanded)

    #print("generated", num, "value", matches, "from", rules[num], flush=True)
    cache[num] = matches
    return cache[num]

  def __gen_matches(self):
    # generate all matches.
    cache = {}
    assert self.rules[0] == [(8, 11)]
    assert self.rules[8] == [(42,)]
    assert self.rules[11] == [(42, 31)]
    # This evaluates almost everything, and these rules are needed later.
    MessageParser.__matching(cache, self.rules, 31)
    MessageParser.__matching(cache, self.rules, 42)
    # convert rules 42 and 31 into sets, because we perform a bunch of contains
    # checks with those in particular.
    cache[42] = frozenset(cache[42])
    cache[31] = frozenset(cache[31])

    matches = None
    if False:
      # Generating this takes a considerable amount of time, that's not worth it.
      #
      # 1) generating all the values for rule 0 is slow: ~330ms
      # 2) converting the list to a set is slow: ~550ms
      #
      # Lookups in the set aren't slow, but amortized over construction time, it's not really worth it.
      #
      # Using the optimized 3 set lookup, we avoid ~880ms of overhead. See MessageParser.part1_match
      #
      # aside) not converting to a set and doing lookups is really slow: ~8s

      MessageParser.__matching(cache, self.rules, 0)
      matches = frozenset(cache[0])
      #matches = cache[0]
      # remove rules 0, 8, and 11 from the cache. They are changed in part 2
      # and we don't want to accidentally rely on them for part 1.
      del cache[0]
      del cache[8]
      del cache[11]

    # We take advantage of this property as well.
    # check it only once.
    p = len(any_item(cache[42]))
    for r in cache[42]:
      assert p == len(r)
    for r in cache[31]:
      assert p == len(r)

    # making the matching values into a set speeds up all contains checks.
    # 200% worth it.
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
    return len(any_item(rule42))

  def count(self):
    self.gen_cache()
    c42 = self.matches[0][42]
    c31 = self.matches[0][31]
    return len(c42) * len(c42) * len(c31)

  def part1_match(self, value):
    # This strategy is _much_ faster than evaluating all the strings that match rule 0
    # and checking if the string we are passed is in that set.
    self.gen_cache()

    # were going to abuse the rule structure, 
    # make sure it matches our expectations.
    assert self.rules[0] == [(8, 11)]
    assert self.rules[8] == [(42,)]
    assert self.rules[11] == [(42, 31)]
    rule31 = self.matches[0][31]
    rule42 = self.matches[0][42]

    chunk_size = self.chunk_size()
    if len(value) % chunk_size != 0 or len(value) // chunk_size != 3:
      return False

    chunked = grouper(value, chunk_size)

    # if you noticed above:
    # rule 0 = 8 11
    #        = 42 42 31
    return chunked[0] in rule42 and chunked[1] in rule42 and chunked[2] in rule31

  def part2_match(self, value):
    self.gen_cache()
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

    chunked = grouper(value, chunk_size)
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
