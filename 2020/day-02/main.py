#!/usr/bin/python3

import argparse
import re
import sys
import typing

class PasswordPolicy(typing.NamedTuple):
  start: int
  end: int
  character: str
  password: str

  extractor = re.compile("(\d+)-(\d+) (.): (.+)")

  @staticmethod
  def from_string(string):
    match = PasswordPolicy.extractor.fullmatch(string)
    start, end, character, password = match.groups()
    return PasswordPolicy(int(start), int(end), character, password)


def load_file(filename):
  contents = []
  with open(filename, 'r') as f:
    for line in f:
      line = line.strip() # remove trailing newline
      contents.append(PasswordPolicy.from_string(line))
  return contents


def part1_valid(p):
  c = p.password.count(p.character)
  return p.start <= c and c <= p.end


def part2_valid(p):
  # policy is 1 indexed, python is zero indexed.
  first = p.password[p.start - 1]
  second= p.password[p.end - 1]
  # Xor
  return (first == p.character) ^ (second == p.character)


def count_valid(policies, validator):
  count = 0
  for p in policies:
    if validator(p):
      count += 1
  return count


def main(filename):
  policies = load_file(filename)
  print("part 1:", count_valid(policies, part1_valid))
  print("part 2:", count_valid(policies, part2_valid))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
