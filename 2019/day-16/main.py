#!/usr/bin/env python3

import argparse
import collections
import itertools
import math
import sys

def take(c, iterable):
  out = []
  for x in iterable:
    out.append(x)
    if len(out) == c:
      return out
  return out

def skip(c, iterable):
  iterable = iter(iterable)
  for x in iterable:
    if c > 0:
      c -= 1
    else:
      yield x
      break
  for x in iterable:
    yield x

def repeated(c, iterable):
  for x in iterable:
    for _ in range(c):
      yield x

def m(x, y):
  if x == 0:
    return 0
  elif x == 1:
    return y
  elif x == -1:
    return -y

PROGRESS = "---///|||\\\\\\"

def FFT(phase, sequence):
  for i in range(phase):
    sequence = FFT2(i, sequence)
    print("\x08..", end="", flush=True)
  print()
  return "".join(map(str, sequence))

def FFT2(phase, sequence):
  base = [0, 1, 0, -1]
  out = []
  # Compute the secondary sequence we multiply with.
  for pos, val in enumerate(sequence):
    l = skip(1, itertools.cycle(repeated(pos + 1, base)))
    s = 0
    for x, y in zip(l, sequence):
      s += m(x, y)
    out.append(abs(s) % 10)
    print("\x08" + PROGRESS[pos % len(PROGRESS)], end="", flush=True)
  return out

if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', type=argparse.FileType('r'), nargs='?', default=sys.stdin)

  args = parser.parse_args(sys.argv[1:])

  print(repeated(2, [0,1,0,-1]))
  print(list(skip(2, [0,1,0,-1])))
  print(list(skip(2, repeated(3, [0,1,0,-1]))))

  sequence = args.input.read().strip()
  #print(FFT(0, list(map(int, "12345678"))))
  #print(FFT(1, list(map(int, "12345678"))))
  #print(FFT(2, list(map(int, "12345678"))))
  #print(FFT(3, list(map(int, "12345678"))))
  #print(FFT(100, list(map(int, "80871224585914546619083218645595"))))
  #print(FFT(100, list(map(int, "03036732577212944063491565474664" * 10000))))
  print(sequence)
  offset = int(sequence[:8])
  print(offset)
  p1 = FFT(100, list(map(int, sequence)))
  print(p1)
