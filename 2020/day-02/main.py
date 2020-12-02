#!/usr/bin/python3

import argparse
import sys
import typing

class PasswordPolicy(typing.NamedTuple):
  start: int
  end: int
  character: str
  password: str

  @staticmethod
  def from_string(string):
    string = string.strip()
    r, password = string.split(":")
    range, character = r.strip().split(" ")
    start, end = range.strip().split("-")

    return PasswordPolicy(int(start), int(end), character.strip(), password.strip())

  def valid(self):
    c = self.password.count(self.character)
    return self.start <= c and c <= self.end

#  def __repr__(self):
#    return "{start}-{end} {character}: {password}".format_map(self)


def load_file(filename):
  contents = []
  with open(filename, 'r') as f:
    for line in f:
      contents.append(PasswordPolicy.from_string(line))
      print(contents[-1], contents[-1].valid())
  return contents


def part1(policies):
  valid = 0
  for p in policies:
    if p.valid():
      valid += 1

  print("valid:", valid)

def part2(policies):
  pass

def main(filename):
  policies = load_file(filename)
  part1(policies)

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
