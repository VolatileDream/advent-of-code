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


def only_item(iterable):
  assert len(iterable) == 1
  for i in iterable:
    return i


class Food:
  @staticmethod
  def from_line(line):
    ingredients, allergens = line.split(" (contains ")
    ingredients = set(ingredients.split(" "))
    allergens = set(allergens.strip(")").split(", "))
    return Food(ingredients, allergens)

  def __init__(self, ingredients, allergens):
    self.ingredients = ingredients
    self.allergens = allergens

  def __repr__(self):
    return "Food({}, {})".format(self.ingredients, self.allergens)


def all_ingredients(foods):
  out = set()
  for i in foods:
    out.update(i.ingredients)
  return out


def all_allergens(foods):
  out = set()
  for i in foods:
    out.update(i.allergens)
  return out


def find_allergens(foods):
  # Generate sets of ingredients and allergens
  ingredients = all_ingredients(foods)
  allergens = all_allergens(foods)
  # For each allergen, they could be any of the ingredients.
  allergen_options = { a: set(ingredients) for a in allergens }

  # map allergen => all items that contain it
  allergen_to_ingredients = collections.defaultdict(list)
  for f in foods:
    for a in f.allergens:
      allergen_to_ingredients[a].append(f)

  for allergen, fs in allergen_to_ingredients.items():
    for food in fs:
      # this item must have the allergen in it.
      # that means that the allergen is in both allergen_options and i.ingredients
      # take the intersect to keep only those items in both.
      allergen_options[allergen].intersection_update(food.ingredients)

  # some amount of the contents of allergen_to_ingredients have been
  # reduced to exactly a single item! This means we know what that allergen
  # is, so we can remove it from every other item.

  unreduced = set(allergens)
  while len(unreduced) > 0:
    # find the items with length 1 (iterating over unreduced)
    reduced_allergens = set([u for u in unreduced if len(allergen_options[u]) == 1])
   
    # they're correctly reduced. 
    unreduced.difference_update(reduced_allergens)

    # flatten the ingredients that they all contain.
    known_allergens = [only_item(allergen_options[r]) for r in reduced_allergens]

    # remove those ingredients from everything else.
    for u in unreduced:
      allergen_options[u].difference_update(known_allergens)

  return { k: only_item(v) for k, v in allergen_options.items() }


def part1(foods, allergen_options):
  allergic_ingredients = set(allergen_options.values())
  count = 0
  for f in foods:
    # count the number of ingredients that aren't known allergens
    count += len(f.ingredients.difference(allergic_ingredients))

  return count

def part2(foods, allergen_options):
  allergens = list(allergen_options.keys())
  allergens.sort()

  print("canonical list", allergens)
  return ','.join([allergen_options[a] for a in allergens])


def main(filename):
  foods = [Food.from_line(l) for l in load_file(filename)]

  print("Food:")
  for i in foods:
    #print(i)
    pass
  print()

  allergen_options = find_allergens(foods)

  print("part 1:", part1(foods, allergen_options))
  print("part 2:", part2(foods, allergen_options))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
