#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from enum import IntEnum
from typing import NamedTuple
from _.data.formatting.blocks import Block

@dataclass
class CardHand:
  cards: str
  bid: int

  @staticmethod
  def parse(line):
    cards, bid = line.split(" ")
    return CardHand(cards, int(bid))


# Convert a hand value to a number
def CardInt(hand, order):
  v = 0
  for c in hand.cards:
    v = v << 5 | order.find(c)
  return v


class HandValue(IntEnum):
  Highest = 1
  OnePair = 2
  TwoPair = 3
  ThreeKind = 4
  FullHouse = 5
  FourKind = 6
  FiveKind = 7


def rank(hands, clfn, cardvals):
  values = []
  for c in hands:
    v = clfn(c.cards)
    #print(v, c)
    values.append((v, c,))

  grouped = defaultdict(list)
  for v in values:
    val, hand = v
    grouped[val].append(hand)

  for val, hands in grouped.items():
    hands.sort(key=lambda x: CardInt(x, cardvals))

  flattened = []
  for v in HandValue:
    flattened.extend(grouped[v])

  return flattened

LOAD = "content"
def REWRITE(lines):
  return [CardHand.parse(l) for l in lines]


def classify1(cards):
  kinds = defaultdict(int)
  for c in cards:
    kinds[c] += 1

  k = len(kinds)
  if k == 1:
    return HandValue.FiveKind
  elif k == 5:
    return HandValue.Highest
  elif k == 4:
    return HandValue.OnePair
  elif k == 3:
    (i1, v1), (i2, v2), (i3, v3) = kinds.items()
    if 3 in (v1, v2, v3): # 3, 1, 1
      return HandValue.ThreeKind
    return HandValue.TwoPair # 2, 2, 1
  elif k == 2:
    # full or four kind
    (i1, v1), (i2, v2) = kinds.items()
    if v1 == 2 or v1 == 3:
      return HandValue.FullHouse
    return HandValue.FourKind

  assert False, f"no HandValue: {kinds}"


def PART1(inputs):
  flattened = rank(inputs, classify1, "23456789TJQKA")

  s = 0
  for idx, f in enumerate(flattened):
    s += (idx + 1) * f.bid
  #print(grouped)
  return s


def classify2(cards):
  kinds = defaultdict(int)
  for c in cards:
    kinds[c] += 1

  j = kinds["J"]
  del kinds["J"]

  if j > 0:
    # add the jokers to the highest other card.
    # this makes processing it trivial.
    c = None
    m = 0
    for card, count in kinds.items():
      if count > m:
        c = card
        m = count
    kinds[c] += j

  k = len(kinds)
  if k == 1:
    return HandValue.FiveKind
  elif k == 2:
    # full or found kind
    (i1, v1), (i2, v2) = kinds.items()
    if v1 == 2 or v1 == 3:
      return HandValue.FullHouse
    return HandValue.FourKind
  elif k == 3:
    (i1, v1), (i2, v2), (i3, v3) = kinds.items()
    if 3 in (v1, v2, v3): # 3, 1, 1
      return HandValue.ThreeKind
    return HandValue.TwoPair # 2, 2, 1
  elif k == 4:
    return HandValue.OnePair
  elif k == 5:
    return HandValue.Highest

  assert False, f"no HandValue: {kinds}"

def PART2(inputs):
  flattened = rank(inputs, classify2, "J23456789TQKA")

  s = 0
  for idx, f in enumerate(flattened):
    s += (idx + 1) * f.bid
    print(f)
  #print(grouped)
  return s
