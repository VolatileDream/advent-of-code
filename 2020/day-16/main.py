#!/usr/bin/python3

import argparse
import collections
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


def rules(rules):
  # Returns a list of: ("name", [range...])
  out = []
  for rule in rules:
    name, rest = rule.split(": ")
    ranges = rest.split(" or ")
    rs = []
    for r in ranges:
      start, end = r.split("-")
      rs.append(range(int(start), int(end) + 1))

    out.append((name, *rs))

  return out


def parse_all(things):
  rs = rules(things[0])
  ticket = [int(i) for i in things[1][1].split(",")]
  others = [[int(i) for i in s.split(",")] for s in things[2][1:]]
  return (rs, ticket, others)


def bad_indicies(ticket, rules):
  # return a tuple (v, s) such that:
  # v == "invalid", s = bad indices

  invalids = []
  for t in ticket:
    valid = False
    for r in rules:
      name, first, second = r
      if t in first or t in second:
        valid = True
        break

    if not valid:
      invalids.append(t)

  return invalids


def part1(things):
  rules, our_ticket, other_tickets = things

  error_rate = 0
  for t in other_tickets:
    bad = bad_indicies(t, rules)
    error_rate += sum(bad)

  return error_rate


def reduce_orderings(orderings_dict):
  # copy the dict
  odict = { k: list(v) for k,v in orderings_dict.items() }

  # indicies with size >= 1
  unfixed_indicies = set(range(len(odict)))
  # indicies with size == 1, whose items have been removed
  # from all the other indicies
  fixed_indicies = set()

  # don't assume that this will reduce everything down to a
  # single item, so instead keep going until we stop being
  # able to update any indicies.
  changed = True
  while changed:
    changed = False

    # look for options that have length 1
    for i in unfixed_indicies:
      if len(odict[i]) != 1:
        continue

      changed = True
      item = odict[i][0]
      fixed_indicies.add(i)

      for j in unfixed_indicies:
        # don't remove it from itself.
        if i == j:
          continue
        if item in odict[j]:
          odict[j].remove(item)

    # the index has been removed
    unfixed_indicies.difference_update(fixed_indicies)

  return odict


def part2(things):
  rules, our_ticket, other_tickets = things

  good_tickets = []
  for t in other_tickets:
    bad = bad_indicies(t, rules)
    if len(bad) == 0:
      good_tickets.append(t)

  # convert rules to dict
  rdict = {}
  for r in rules:
    name, first, second = r
    rdict[name] = (first, second)

  # for each index we're going to find the possible rules that match.
  # we'll only have the rules that match all of the good tickets.

  valid_rules = collections.defaultdict(list)
  for i in range(len(rdict)):
    for name in rdict:
      first, second = rdict[name]

      valid = True
      for t in good_tickets:
        t = t[i]
        if t not in first and t not in second:
          valid = False
          break

      if valid:
        valid_rules[i].append(name)

  # reducing gets us down to 1 option left.
  valid_rules = reduce_orderings(valid_rules)
  valid_ordering = []
  for i in range(len(rdict)):
    valid_ordering.append(valid_rules[i][0])

  fields = { k:v for k,v in zip(valid_ordering, our_ticket) }

  dep = 1
  for n in rdict.keys():
    if n.startswith("departure"):
      dep *= fields[n]
      
  return dep


def main(filename):
  things = parse_all(load_groups(filename))

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
