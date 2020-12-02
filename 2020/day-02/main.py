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


def part1(policies):
  count = 0
  for p in policies:
    c = p.password.count(p.character)
    valid = p.start <= c and c <= p.end
    if valid:
      count += 1

  print("part 1 valid:", count)


def part2(policies):
  count = 0
  for p in policies:
    first = p.password[p.start - 1]
    second= p.password[p.end - 1]
    # Xor
    if (first == p.character) ^ (second == p.character):
      count += 1

  print("part 2 valid:", count)


def main(filename):
  policies = load_file(filename)
  part1(policies)
  part2(policies)


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
