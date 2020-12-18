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
    contents.append(line)

  return contents


NUMBERS = set("0123456789")
OPS = set("+*-/")
SUBEXPR = set("()")

def tokenize(expression):
  # remove spaces so we only have numbers and operators
  expression = expression.replace(" ", "")

  tokens = []
  offset = 0
  while offset < len(expression):
    
    n = expression[offset]

    if n in OPS or n in SUBEXPR:
      tokens.append(n)
    elif n in NUMBERS:
      whole = n
      while offset + 1 < len(expression) and expression[offset + 1] in NUMBERS:
        offset += 1
        whole += expression[offset]
      tokens.append(int(whole))

    offset += 1

  return tokens


def find_matching(array, start, end):
  assert array[0] == start
  index = 0
  count = 0
  while index < len(array):
    item = array[index]
    if item == start:
      count += 1
    elif item == end:
      count -= 1

    if count == 0:
      return index + 1

    index += 1

  raise Exception("could not find matching {}{} pair in {}".format(start, end, array))


def nest_tokens(tokens):
  # for a list of tokens, convert (...) into a list
  out = []
  index = 0
  while index < len(tokens):
    t = tokens[index]
    if t in SUBEXPR:
      end_offset = find_matching(tokens[index:], "(", ")")
      subset = tokens[index + 1:index + end_offset - 1]
      out.append(nest_tokens(subset))
      index += end_offset - 1
    else:
      out.append(t)

    index += 1

  return out


def precedent_nesting(nested_tokens):
  # rewrite to put + before *

  if type(nested_tokens) != list:
    return nested_tokens

  output = []

  index = 0
  while index < len(nested_tokens):
    item = nested_tokens[index]
    if item == "+":
      left = output.pop()
      right= precedent_nesting(nested_tokens[index + 1])
      #print("mult", left, right)
      output.append([left, item, right])
      index += 1 # we took an extra item
    elif type(item) == list:
      output.append(precedent_nesting(item))
    else:
      output.append(item)

    index += 1

  if len(output) == 1:
    return output[0]
  return output
      

def easy_value(expr):
  if type(expr) == int:
    return expr
  elif type(expr) == list:
    return easy_eval(expr)
  raise Exception("found {} when expecting value".format(expr))


def easy_eval(nested_tokens):
  #print("eval", nested_tokens)
  left, op, right, *rest = nested_tokens

  left = easy_value(left)
  right= easy_value(right)

  val = None
  if op == "+":
    val = left + right
  elif op == "*":
    val = left * right

  #print("val", val)

  if len(rest) > 0:
    return easy_eval([val] + rest)
  else:
    return val


def part1(things):
  return sum([easy_eval(nest_tokens(tokenize(e))) for e in things])


def part2(things):
  return sum([easy_eval(precedent_nesting(nest_tokens(tokenize(e)))) for e in things])


EXAMPLES = [
  ("1 + (2 * 3)", 7),
  ("1 + 2 * 3 + 4 * 5 + 6", 71),
  ("1 + (2 * 3) + (4 * (5 + 6))", 51),
  ("2 * 3 + (4 * 5)", 26),
  ("5 + (8 * 3 + 9 + 3 * 4 * 3)", 437),
  ("5 * 9 * (7 * 3 * 3 + 9 * 3 + (8 + 6 * 4))", 12240),
  ("((2 + 4 * 9) * (6 + 9 * 8 + 6) + 6) + 2 + 4 * 2", 13632),
]

EXAMPLES2 = [
    ("1 + (2 * 3) + (4 * (5 + 6))", 51),
    ("2 * 3 + (4 * 5)", 46),
    ("5 + (8 * 3 + 9 + 3 * 4 * 3)", 1445),
    ("5 * 9 * (7 * 3 * 3 + 9 * 3 + (8 + 6 * 4))", 669060),
    ("((2 + 4 * 9) * (6 + 9 * 8 + 6) + 6) + 2 + 4 * 2", 23340),
]

def main(filename):
  things = load_file(filename)

  for expr, out in EXAMPLES2:
    #assert evaluate(expr) == out
    print(expr)
    nested = precedent_nesting(nest_tokens(tokenize(expr)))
    print(nested)
    #rpolish = rewrite_rpolish(nested)
    value = easy_eval(nested)
    print("value", value)
    assert out == value
    print()

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
