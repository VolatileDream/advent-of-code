#!/usr/bin/env python3

import argparse
import collections
import math
import sys

def part_to_tuple(p):
  count, name = p.strip().split(" ")
  return (name, int(count))

class Recipy(object):
  def __init__(self, ins, out):
    # inputs: dict of name -> count
    self.inputs = ins
    # output: tuple(name, count)
    self.output = out

  @property
  def name(self):
    return self.output[0]

  @property
  def outc(self):
    return self.output[1]

  def __repr__(self):
    return "Recipy(%s => %s)" % (", ".join(map(str, self.inputs.items())), self.output)

  @staticmethod
  def parse_from(line):
    inputs, outputs = [ i.strip() for i in line.split("=>") ]
    ingredients = {}
    for part in inputs.split(","):
      name, count = part_to_tuple(part)
      ingredients[name] = count
    return Recipy(ingredients, part_to_tuple(outputs))


class RecipyBook(object):
  def __init__(self, recipies):
    self.recipies = recipies

  def __getitem__(self, key):
    return self.recipies[key]

  @staticmethod
  def parse_from(f):
    recipies = {}
    for line in f:
      r = Recipy.parse_from(line)
      recipies[r.name] = r
    return RecipyBook(recipies)


def d(indent, *args):
  if indent is not None:
    print(indent, *args)

def inc(indent):
  if indent is None:
    return None
  return indent + "\t"

class Resevoir(object):
  def __init__(self, init=None):
    if init is None:
      init = {}
    self.storage = dict(init)

  def __repr__(self):
    return "Resevoir(%s)" % self.storage

  def __contains__(self, key):
    return key in self.storage

  def has(self, val, count):
    if val not in self.storage:
      return False
    return self.storage[val] > count

  def take(self, val, count):
    "Returns the number of items taken, if any."
    if val not in self.storage:
      return 0
    amount = self.storage[val]
    remove = 0
    if self.storage[val] < count:
      remove = self.storage[val]
    else:
      remove = count
    self.storage[val] -= remove
    return remove

  def put(self, val, count):
    if val not in self.storage:
      self.storage[val] = 0
    self.storage[val] += count


class Chef(object):
  def __init__(self, book, base):
    self.book = book
    self.base = base

  def make(self, val, count):
    indent = "> "
    indent = None
    extras = Resevoir()
    made = self.create(extras, val, count, indent)
    d(indent, "needed", made, self.base)
    d(indent, "created extras:", extras)
    return made

  def create(self, extras, val, count, indent):
    if val == self.base:
      if val not in extras:
        d(indent, "can supply", count, val)
        return count
      else:
        # we're pretending ORE is limited. (part 2)
        if not extras.has(val, count):
          raise Exception("out of fuel")
    extra_count = extras.take(val, count)
    if extra_count > 0:
      d(indent, "had extra", val, "need to make", extra_count, "fewer")
    count -= extra_count

    # Minimum number of these that can be made.
    r = self.book[val]
    making = math.ceil(count / r.outc) * r.outc
    over = making - count
    d(indent, "making", val, "with", r)
    d(indent, "need", count, val)

    if over > 0:
      d(indent, "going to produce an extra", over, "of", val)
      extras.put(val, over)
    # Number of `base` that need to get made to create `making` number of `val`

    base_count = 0
    for ingredient in r.inputs.keys():
      n = making * r.inputs[ingredient] // r.outc
      d(indent, "creating", n, ingredient, "to fulfill dependencies")
      c = self.create(extras, ingredient, n, indent=inc(indent))
      base_count += c
    return base_count


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', type=argparse.FileType('r'), nargs='?', default=sys.stdin)

  args = parser.parse_args(sys.argv[1:])

  r = RecipyBook.parse_from(args.input)
  c = Chef(r, 'ORE')
  r.recipies['ORE'] = Recipy({}, ('ORE', 1))
  ore_for_fuel = c.make('FUEL', 1)
  print("needed", ore_for_fuel, "total ORE to create 1 FUEL")

  # With limited ORE, how much fuel can we make?
  ORE_IN_STORAGE = 1000000000000 
  extras = Resevoir({'ORE': ORE_IN_STORAGE})
  fuel = ORE_IN_STORAGE // ore_for_fuel
  #fuel = 13107621 # answer to the puzzle
  c.create(extras, 'FUEL', fuel, None)
  print(extras)
  make = 1
  try:
    while True:
      #print(extras)
      print("remaining ORE:", extras.storage['ORE'], "fuel:", fuel)
      c.create(extras, 'FUEL', make, None)
      fuel += make
      #print(".", end="", flush=True)
  except Exception as e:
    print("made a total of", fuel, "fuel")
    print(e)

