#!/usr/bin/python3

import sys

def find_sum1(target_sum):
  seen = set()
  for line in sys.stdin.readlines():
    value = int(line)
    seen.add(value)
    if (target_sum - value) in seen:
      return (value, target_sum - value)

  return None


def find_sum2(target_sum):
  # This is called 3SUM in computer science.

  # Keep track of everything we see.
  seen = set()
  for line in sys.stdin.readlines():
    value = int(line)
    seen.add(value)

  # Not a lot of values, sorting after the fact is fine.
  values = list(sorted(seen))

  # O(n^2) is the best we can do.
  for first in range(len(values)):
    for second in range(first, len(values)):
      v1 = values[first]
      v2 = values[second]
      v3 = target_sum - v1 - v2
      # Check if we've seen target - *start - *end.
      if v3 in seen:
          return (v1, v2, v3)

  return None


def product(iterable):
  p = 1
  for i in iterable:
    p *= i
  return p


def main():
  answer = find_sum2(2020)
  if answer is None:
    print("error: no pair found")
    return

  print(answer)
  print(product(answer))

if __name__ == "__main__":
  main()
