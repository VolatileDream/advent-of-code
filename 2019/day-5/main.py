#!/usr/bin/env python3

import argparse
import sys

# General day 2 stuff

def maybe_indir(ctx, pinstr, pos, arg):
  mode = (pinstr // pos) % 10
  if mode == 0:
    return ctx[arg]
  elif mode == 1:
    return arg
  else:
    raise Exception("bad mode: %s" % mode)


def exec(ctx, idx):
  # pad out ctx if we're at the end.
  if len(ctx) < idx+4:
    ctx = ctx + [0,0,0,0]
  # Technically not all of these get used...
  # But this is easier than doing it differently.
  pinstr, p1, p2, p3 = ctx[idx:idx+4]
  # do immediate mode calculations.
  instr = pinstr % 100
  if instr == 1 or instr == 2:
    arg1 = maybe_indir(ctx, pinstr, 100, p1)
    arg2 = maybe_indir(ctx, pinstr, 1000, p2)
    if instr == 1:
      ctx[p3] = arg1 + arg2
    elif instr == 2:
      ctx[p3] = arg1 * arg2
    return idx + 4
  elif instr == 3 or instr == 4:
    if instr == 3:
      ctx[p1] = int(input("> "))
    elif instr == 4:
      arg1 = maybe_indir(ctx, pinstr, 100, p1)
      print(arg1)
    return idx + 2
  elif instr == 5 or instr == 6:
    # jumps...
    arg1 = maybe_indir(ctx, pinstr, 100, p1)
    arg2 = maybe_indir(ctx, pinstr, 1000, p2)
    if instr == 5 and arg1 != 0:
      return arg2
    if instr == 6 and arg1 == 0:
      return arg2
    return idx + 3
  elif instr == 7:
    arg1 = maybe_indir(ctx, pinstr, 100, p1)
    arg2 = maybe_indir(ctx, pinstr, 1000, p2)
    ctx[p3] = int(arg1 < arg2)
    return idx + 4
  elif instr == 8:
    arg1 = maybe_indir(ctx, pinstr, 100, p1)
    arg2 = maybe_indir(ctx, pinstr, 1000, p2)
    ctx[p3] = int(arg1 == arg2)
    return idx + 4
    
  elif instr == 99:
    return -1

  raise Exception("bad instruction: %s (%s) at index %d" % (instr, pinstr, idx))



def load(f):
  contents = []
  for line in f:
    contents.extend(line.split(','))
  return [ int(i) for i in contents ]


def run(ctx, continue_fn):
  idx = 0
  while continue_fn():
    idx = exec(ctx, idx)
    if idx < 0:
      break
  return ctx


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', type=argparse.FileType('r'), nargs='?', default=sys.stdin)
  parser.add_argument('--steps', default=None, type=int)

  args = parser.parse_args(sys.argv[1:])

  def for_count():
    args.steps -= 1
    return args.steps >= 0
  def forever():
    return True

  stepfn = forever
  if args.steps is not None:
    stepfn = for_count

  for line in args.input:
    contents = line.split(',')
    ctx = [ int(x) for x in contents ]
    res = run(ctx, stepfn) 
    print("---")
    print(res)

