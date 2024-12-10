#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

import bisect

LOAD = "content"
def REWRITE(lines):
  assert(len(lines) == 1)
  return splitit(lines[0])

def splitit(line):
  return [int(c) for c in line]

def TEST(inputs):
  disk = splitit("0099811188827773336446555566")
  assert(checksum(disk) == 1928)
  disk = move_files(splitit("2333133121414131402"))
  assert(checksum(disk) == 2858)

def checksum(disk):
  x = 0
  for index, item in enumerate(disk):
    x += index * item
  return x


def compaction(descriptor):
  # Copy!
  descriptor = list(descriptor)
  # Easiest to conceive of this as a generator...
  max_id = len(descriptor) // 2
  end = len(descriptor) - 1
  index = 0
  curid = 0
  empty = False

  while index < end:
    count = descriptor[index]
    if not empty:
      for _ in range(count):
        yield curid
      curid += 1
    else:
      while count > 0:
        m = min(count, descriptor[end])
        count -= m
        descriptor[end] -= m
        for _ in range(m):
          yield max_id
        if descriptor[end] == 0:
          end -= 2 # skip over the zeros.
          max_id -= 1
    index += 1
    empty = not empty

  if index == end:
    for _ in range(descriptor[index]):
      yield curid

def PART1(inputs):
  cmp = list(compaction(inputs))
  # 6283170117911
  return checksum(compaction(inputs))

def explode(descriptor):
  # Longest it can possibly be...
  exploded = [0] * len(descriptor) * 9
  starts = {}
  idnum = 0
  idx = 0
  empty = False
  for count in descriptor:
    if not empty:
      starts[idnum] = idx
      for offset in range(count):
        exploded[idx + offset] = idnum
      idnum += 1
    idx += count
    empty = not empty

  # Truncate down.
  #print("delta", len(exploded) - idx)
  return exploded[:idx], starts
  
def emptyIndex(descriptor):
  # Gap size -> list<sorted>(indexes)
  index = defaultdict(list)

  i = 0
  empty = False
  for count in descriptor:
    if empty:
      bisect.insort(index[count], i)
    i += count
    empty = not empty

  return index

def move_files(descriptor):
  gaps = emptyIndex(descriptor)
  disk, starts = explode(descriptor)
  firstdisk = list(disk)

  def move(idx, dest, count):
    for offset in range(count):
      assert(disk[dest + offset] == 0)
      disk[dest + offset] = disk[idx + offset]
      disk[idx + offset] = 0

  # find and reduce the gap.
  def fr_gap(search, curpos):
    # Find the first gap that fits the search size.
    lowest = curpos
    foundsize = None
    for size in range(search, 10):
      #print(f"fr_gap({search}): {size} {gaps[size]}")
      newer = gaps[size]
      if newer and newer[0] < lowest:
        lowest = newer[0]
        foundsize = size

    if lowest == curpos:
      return None # can't be moved.

    assert(lowest == gaps[foundsize].pop(0))

    if foundsize > search:
      # There is some space left, add it to the index.
      bisect.insort(gaps[foundsize - search], lowest + search)

    return lowest

  idx = len(descriptor) - 1
  while idx > 0:
    idnum = idx // 2
    count = descriptor[idx]
    curpos= starts[idnum]
    space = fr_gap(count, curpos)
    #print(f"searching for {idnum} len {count}, found: {space}")
    if space is not None:
      #print(disk)
      move(starts[idnum], space, count)
    idx -= 2

  # This print surfaced the issue in the first attempt, not surfaced by the test case.
  #for i in range(len(disk)):
  #  print(disk[i], firstdisk[i])
  return disk

def PART2(inputs):
  #print(to_il(inputs).raw())
  #move_files(inputs)

  # Attempt 1: 8450064123278 - too high
  #  - this attempt would move early blocks later than they started.
  # 6307653242596
  return checksum(move_files(inputs))
