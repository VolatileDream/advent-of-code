#!/usr/bin/env python-mr

from collections import defaultdict
from _.data.formatting.blocks import Block

class BingoMarker:
  def __init__(self, size):
    self._size = size
    self._mask = (1 << size) - 1 # mask of width size
    self._rows = [0] * size
    self._columns = [0] * size

  def mark(self, row, column) -> bool:
    self._rows[row] |= 1 << column
    self._columns[column] |= 1 << row
    return (self._rows[row] & self._mask) == self._mask \
           or (self._columns[column] & self._mask) == self._mask

  def __contains__(self, pos) -> bool:
    row, column = pos
    return bool(self._rows[row] & (1 << column))

  def values(self, marked):
    for row, value in enumerate(self._rows):
      for column in range(self._size):
        bit = bool(value & (1 << column))
        if bit == marked:
          yield (row, column)


class BingoBoard:
  @staticmethod
  def parse(values):
    squares = []
    for line in values:
      numbers = [int(i) for i in line.split()]
      squares.append(numbers)

    for s in squares:
      assert len(s) == len(squares[0])
    return BingoBoard(squares)

  def __repr__(self):
    columns = [Block()] * len(self._board)
    for r, row in enumerate(self._board):
      for c, val in enumerate(row):
        if (r, c) in self._marks:
          columns[c] |= f"[{val}]"
        else:
          columns[c] |= f" {val} "
    return str(Block.space().hjoin(columns))

  def __init__(self, values):
    self._marks = BingoMarker(len(values))
    self._board = values
    self._index = {}
    for row, line in enumerate(values):
      for column, v in enumerate(line):
        pos = (row, column)
        self._index[v] = pos

  def values(self, marked=True):
    # tuple(marked, unmarked)
    return [self._board[r][c] for r, c in self._marks.values(marked)]

  def mark(self, value) -> bool:
    # Returns true if this completed a row or column.
    pos = self._index.get(value, None)
    if not pos:
      return False

    row, column = pos
    return self._marks.mark(row, column)


def mark_boards(values, boards):
  # marks until a winner.
  marked = []
  for v in values:
    marked.append(v)
    for b in boards:
      if b.mark(v):
        return (marked, b)

  return (marked, None)


def score(board, last_mark):
  return sum(board.values(marked=False)) * last_mark

LOAD = "groups"

def REWRITE(groups):
  draws, *boards = groups
  return ([int(i) for i in draws[0].split(",")],
          [BingoBoard.parse(b) for b in boards])


def PART1(inputs):
  values, boards = inputs
  print(values)
  for b in boards:
    print(b)
    print()

  marks, board = mark_boards(values, boards)

  # sum unmarked spots, and multiply by last one.
  return score(board, marks[-1])


def last_winner(values, boards):
  remaining = list(boards)
  for v in values:
    for b in list(remaining):
      if b.mark(v):
        if len(remaining) == 1:
          return (b, v)
        remaining.remove(b)

  raise Exception("Bad board setup")


def PART2(inputs):
  values, boards = inputs
  last_board, last_mark = last_winner(values, boards)
  print(last_mark)
  print(last_board)
  return score(last_board, last_mark)
