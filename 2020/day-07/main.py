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

class BagRules:

  LINE_RE = re.compile("^([^ ]+) ([^ ]+) bags contain((,? [0-9]+ [^ ]+ [^ ]+ bags?)+| no other bags).$")
  COUNT_RE = re.compile("([0-9]+) ([^ ]+) ([^ ]+) bags?")

  def __init__(self):
    self.bags = set()
    self.rules = collections.defaultdict(lambda: [])
    # reverse index (x -> y) if y contains x, names only.
    self.rrules = collections.defaultdict(lambda: [])

  def __repr__(self):
    return 'BagRules({}, {})'.format(str(self.bags), str(self.rules.items()))

  def add(self, bag, rules=None):
    self.bags.add(bag)
    if rules:
      self.rules[bag].extend(rules)
      for count, child in rules:
        self.rrules[child].append(bag)

  @staticmethod
  def parse_bag_count(line):
    m = BagRules.COUNT_RE.fullmatch(line)
    count, adjective, colour = m.groups()
    return (int(count), adjective + " " + colour)

  def add_from_line(self, line):
    assert BagRules.LINE_RE.fullmatch(line), line
    bag, rules = line.strip(".").split(" bags contain ")
    if rules == "no other bags":
      self.add(bag)
    else:
      rules = [BagRules.parse_bag_count(r.strip()) for r in rules.split(",")]
      self.add(bag, rules)


def holds(bag_rules, bag):
  # find the bags that can hold onto this coloured bag.
  seen = set()
  lookup = [bag]
  while len(lookup) > 0:
    current = lookup.pop(0)
    seen.add(current)

    for r in bag_rules.rrules[current]:
      if r not in seen:
        lookup.append(r)

  # gets added to avoid hitting it twice, but makes no sense in the output.
  seen.remove(bag)
  return seen


def total_bags(bag_rules, bag):
  # count the number of bags that are contained in the specified bag.
  bag_count = 0
  for count, child_bag in bag_rules.rules[bag]:
    # + 1 to count the bag itself
    #print("contains:", count, child_bag)
    bag_count += count * (total_bags(bag_rules, child_bag) + 1)

  return bag_count

def part1(things):
  seen = holds(things, "shiny gold")
  return len(seen)


def part2(things):
  return total_bags(things, "shiny gold")


def main(filename):
  things = BagRules()

  lines = load_file(filename)
  for l in lines:
    things.add_from_line(l)

  #print(things)
  #print(things.rrules)

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
