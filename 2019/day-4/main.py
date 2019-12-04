#!/usr/bin/env python3

import itertools

def pairwise(iterable):
  """s -> (s0, s1), (s1,s2), [s2,s3], ...

  from python3 itertools docs"""
  a, b = itertools.tee(iterable)
  next(b, None)
  return zip(a, b)


def naive_gen():
  values = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
  return itertools.combinations_with_replacement(values, 6)


def cmp(p1, p2):
  zipped = itertools.zip_longest(p1, p2)
  for v1, v2 in zipped:
    if v1 < v2:
      return -1
    elif v1 > v2:
      return 1
  return 0


def runs(pw):
  # convert (int,) into (int,)
  # (1,1,1,1,1,2,2,2) -> (5,3)
  out = []
  val = pw[0]
  cnt = 0
  for p in pw:
    if p == val:
      cnt += 1
    else:
      out.append(cnt)
      val = p
      cnt = 1
  out.append(cnt)
  return out


def gen_passwords(start, stop):
  # 6 digit number
  # 2 adjacent digits are the same
  # left -> right digits don't decrease
  for pw in naive_gen():
    if cmp(pw, start) < 0:
      continue
    if cmp(pw, stop) > 0:
      break

    # check other things

    # decrease check
    for first, second in pairwise(pw):
      if first > second:
        continue

    # Double check
    # Done the naive way for part 1
    #has_double = False
    #for first, second in pairwise(pw):
    #  if first == second:
    #    has_double = True
    #    break
    #if not has_double:
    #  continue

    # Better runs check.
    r = runs(pw)
    if 2 not in r:
      continue

    yield(pw)
    
  return

def str_to_password(s):
  return [ int(c) for c in s ]


def count_between(start, end):
  p1 = str_to_password(start)
  p2 = str_to_password(end)

  return len(list(gen_passwords(p1, p2)))

if __name__ == "__main__":
  print(count_between("254032", "789860"))
