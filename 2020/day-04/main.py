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
      yield line


def load_passports(filename):
  p = []
  for line in load_file(filename):
    # blank line separates passports
    if not line:
      # passport keys & values may have been split by newlines.
      # canonically they are separated by spaces.
      parts = " ".join(p).split(" ")
      # key & value are colon seperated
      yield Passport.from_dict(dict(kv.split(":") for kv in parts))
      p = []
    else:
      p.append(line)

  parts = " ".join(p).split(" ")
  yield Passport.from_dict(dict(kv.split(":") for kv in parts))


class Passport(typing.NamedTuple):
  birth: str
  issue: str
  expiration: str
  height: str
  hair: str
  eye: str
  id: str
  country: str

  def valid(self):
    acceptable = set(["country"])
    if not self.missing_fields().issubset(acceptable):
      return False

    byr = int(self.birth)
    if byr < 1920 or 2002 < byr:
      #print("birth", byr)
      return False

    iyr = int(self.issue)
    if iyr < 2010 or 2020 < iyr:
      #print("issue", iyr)
      return False

    eyr = int(self.expiration)
    if eyr < 2020 or 2030 < eyr:
      #print("expiry", eyr)
      return False

    # height
    h = int(self.height[:-2] or '0')
    if self.height.endswith("cm"):
      if (h < 150 or 193 < h):
        #print("cm height", h)
        return False
    elif self.height.endswith("in"):
      if (h < 59 or 76 < h):
        #print("inches height", h)
        return False
    else:
      #print("bad height", self.height)
      return False

    if not re.fullmatch("#[0-9a-f]{6}", self.hair):
      #print("hair", self.hair)
      return False

    if self.eye not in ["amb", "blu", "brn", "gry", "grn", "hzl", "oth"]:
      #print("eye", self.eye)
      return False

    if not re.fullmatch("[0-9]{9}", self.id):
      #print("pid", self.id)
      return False

    return True

  def missing_fields(self):
    # return a set of fields that are missing
    m = []
    if self.birth is None:
      m.append("birth") 
    if self.issue is None:
      m.append("issue") 
    if self.expiration is None:
      m.append("expiration")
    if self.height is None:
      m.append("height")
    if self.hair is None:
      m.append("hair")
    if self.eye is None:
      m.append("eye")
    if self.id is None:
      m.append("id")
    if self.country is None:
      m.append("country")
    return set(m)

  @staticmethod
  def from_dict(d):
    d = collections.defaultdict(lambda: None, d)
    return Passport(
      d["byr"],
      d["iyr"],
      d["eyr"],
      d["hgt"],
      d["hcl"],
      d["ecl"],
      d["pid"],
      d["cid"])
    

def part1(passports):
  acceptable = set(["country"])
  count = 0
  for p in passports:
    missing = p.missing_fields()
    if missing.issubset(acceptable):
      count += 1
  return count


def part2(passports):
  count = 0
  for p in passports:
    if p.valid():
      count += 1
  return count


def main(filename):
  passports = list(load_passports(filename))

  print("part 1, number of 'valid' passports:", part1(passports))
  print("part 2, number of 'valid'-er passports:", part2(passports))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='-')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
