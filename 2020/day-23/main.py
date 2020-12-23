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


class FastCupGame:
  def __init__(self, start, verbose=False):
    self.verbose = verbose
    self.length = max(start)
    self.current = start[0]
    # map of index -> next index
    self.next = {}
    for index, value in enumerate(start):
      current = start[index]
      next = start[(index + 1) % len(start)]
      self.next[current] = next

  def p(self, *args):
    if self.verbose:
      print(*args)

  def __get_item__(self, key):
    return self.next[key]

  def p1(self, length=8):
    out = []
    n = 1
    for _ in range(length):
      n = self.next[n]
      out.append(n)

    return out

  def p2(self):
    return self.p1(2)

  def move(self, count=1):
    for _ in range(count):
      self.__move()
      self.p()

  def __move(self):
    # n1 -> n2 -> n3 will stay as they are.
    # we're going to update two links: current -> n1, and n3 -> n4,
    # thus removing n1..n3 from the circle of cups
    n1 = self.next[self.current]
    n2 = self.next[n1]
    n3 = self.next[n2]
    n4 = self.next[n3]

    # update current -> n4,
    # now n1 -> n2 -> n3 -> n4, and nothing points to n1
    self.next[self.current] = n4

    dest = self.current - 1
    picked = set([n1, n2, n3, 0])
    while dest in picked:
      dest -= 1
      if dest <= 0:
        dest = self.length

    # now we have dest -> next[dest]
    # we need to insert n1..n3 into this.
    self.next[n3] = self.next[dest]
    self.next[dest] = n1

    self.current = self.next[self.current]


class CupGame:
  def __init__(self, start, verbose=False):
    self.state = collections.deque(start, maxlen=len(start))
    self.length = max(self.state)
    self.verbose = verbose

  def __repr__(self):
    i = iter(self.state)
    out = ["({})".format(next(i))]
    for cup in i:
      out.append(str(cup))
    return " ".join(out)

  def p1(self, length=8):
    s = collections.deque(self.state)
    s.rotate(-1 - s.index(1))
    out = []
    for i in range(length):
      out.append(s[i])
    return out

  def p2(self):
    return self.p1(2)

  def p(self, *args):
    if self.verbose:
      print(*args)

  def move(self, count=1):
    for _ in range(count):
      self.__move()
      self.p()

  def __move(self):
    self.p("Cups:", self)

    current = self.state[0]
    self.state.rotate(-1)

    n1 = self.state.popleft()
    n2 = self.state.popleft()
    n3 = self.state.popleft()

    picked = set([n1, n2, n3, 0])
    self.p("current:", current)
    self.p("Pickup:", n1, n2, n3)

    dest = current - 1
    while dest in picked:
      dest -= 1
      if dest <= 0:
        dest = self.length

    self.p("Destination:", dest)

    insertion = self.state.index(dest) + 1
    self.state.insert(insertion, n3)
    self.state.insert(insertion, n2)
    self.state.insert(insertion, n1)


def equivalent(start, moves=1000):
  m = max(start)
  start = start + list(range(m + 1, 1000001))
  game = CupGame(start)
  fast = FastCupGame(start)

  for i in range(moves):
    #print(game)
    slower = game.p2()
    faster = fast.p2()

    if slower != faster:
      print("found mismatch", slower, "!=", faster, "after", i, "moves")
      break

    game.move()
    fast.move()


def part1(things):
  fast = FastCupGame(things)
  fast.move(100)
  return fast.p1()


def part2(things):
  m = max(things)
  things += range(m + 1, 1000001)

  things = FastCupGame(things)

  moves = 0
  while moves < 10000000:
    m = 1000000
    things.move(m)
    moves += m
    #print("after", moves, "moves:", things.state[0])
    print("after", moves, "moves:", things.current)

  #one_index = things.state.index(1)
  #return things.state[one_index + 1] * things.state[one_index + 2]
  answer = things.p2()
  print(answer)
  return answer[0] * answer[1]


def main(filename):
  things = [int(i) for i in load_file(filename)[0]]
  print(things)

  #equivalent(things, 1000)

  print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
