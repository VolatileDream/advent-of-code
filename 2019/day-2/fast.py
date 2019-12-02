#!/usr/bin/env python3

import argparse
import sys

# General day 2 stuff

def exec(ctx, idx):
  # pad out ctx if we're at the end.
  if len(ctx) < idx+4:
    ctx = ctx + [0,0,0,0]
  instr, arg1, arg2, out = ctx[idx:idx+4]
  if instr == 1:
    ctx[out] = ctx[arg1] + ctx[arg2]
    return True
  elif instr == 2:
    ctx[out] = ctx[arg1] * ctx[arg2]
    return True
  elif instr == 99:
    return False
  else:
    raise Exception("bad instruction: %s at index %d" % (instr, idx))


def load(f):
  contents = []
  for line in f:
    contents.extend(line.split(','))
  return [ int(i) for i in contents ]


def run(ctx, noun, verb):
  ctx[1] = noun
  ctx[2] = verb
  idx = 0
  while exec(ctx, idx * 4):
    idx += 1
  return ctx[0]


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', type=argparse.FileType('r'), nargs='?', default=sys.stdin)

  args = parser.parse_args(sys.argv[1:])
  ctx = load(args.input)
  for x in range(len(ctx)):
    for y in range(len(ctx)):
      out = run(list(ctx), x, y)
      print(x, y, out)

