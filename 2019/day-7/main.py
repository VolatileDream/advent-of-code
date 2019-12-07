#!/usr/bin/env python3

import argparse
import itertools
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


def exec(ctx, idx, io_in, io_out):
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
      ctx[p1] = int(io_in())
    elif instr == 4:
      arg1 = maybe_indir(ctx, pinstr, 100, p1)
      io_out(arg1)
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


def run(ctx, continue_fn, io_in, io_out):
  instr = 0
  idx = 0
  while continue_fn():
    idx = exec(ctx, idx, io_in, io_out)
    instr += 1
    if idx < 0:
      break
  return (ctx, instr)


def read():
  return input("> ")

def io_out(p):
  print(p)


def p1_main(args, stepfn):
  for line in args.input:
    contents = line.split(',')
    ctx = [ int(x) for x in contents ]

    max_phase = None
    maximum = 0 
    for phases in itertools.permutations([0,1,2,3,4]):
      prev_input = [0]
      for idx in range(5):
        prev_input.append(phases[idx])
        next_input = []
        # Reorder so that it makes sense to the reader of the output
        print("input>", prev_input[::-1])
        mem, instrcnt = run(ctx, stepfn, lambda: prev_input.pop(), lambda x: next_input.append(x))
        prev_input = next_input
      print(prev_input[0], phases)
      if prev_input[0] > maximum:
        maximum = prev_input[0]
        max_phase = phases
    print("---")
    print(maximum, max_phase)


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

  p1_main(args, stepfn)
