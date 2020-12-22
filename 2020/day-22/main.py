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


class SpaceCardDeck:
  @staticmethod
  def from_lines(lines):
    name = int(lines[0].rstrip(":").split(" ")[1])
    cards = [int(i) for i in lines[1:]]
    return SpaceCardDeck(name, cards)

  def __init__(self, player, cards):
    self.player = player
    self.cards = cards

  def __repr__(self):
    out = [str(c) for c in self.cards]
    out.insert(0, "Player {}:".format(str(self.player)))
    return "\n".join(out)
    
  def draw(self):
    # return the top card of the deck, removes it from the deck.
    return self.cards.pop(0)

  def add(self, *cards):
    self.cards.extend(cards)

  def __len__(self):
    return len(self.cards)

  def copy(self):
    return SpaceCardDeck(self.player, list(self.cards))

  def state(self):
    # returns a hashable state.
    return tuple(self.cards)

  def subdeck(self, size):
    return SpaceCardDeck(self.player, self.cards[:size])

  @staticmethod
  def play_combat(deck1, deck2):
    # outputs (deck1 after game, deck2 after game, pairs)
    deck1 = deck1.copy()
    deck2 = deck2.copy()
    while len(deck1) > 0 and len(deck2) > 0:
      c1 = deck1.draw()
      c2 = deck2.draw()

      if c1 > c2:
        deck1.add(c1, c2)
      else:
        # c1 < c2
        deck2.add(c2, c1)

    return (deck1, deck2)

  @staticmethod
  def play_recursive_combat(start1, start2, previous_states=None):
    if previous_states is None:
      previous_states = set()

    deck1 = start1.copy()
    deck2 = start2.copy()

    while len(deck1) > 0 and len(deck2) > 0:
      state = (deck1.state(), deck2.state())
      if state in previous_states:
        return (deck1, SpaceCardDeck(deck2.player, []))
      previous_states.add(state)

      c1 = deck1.draw()
      c2 = deck2.draw()

      # do sub round?
      if len(deck1) >= c1 and len(deck2) >= c2:
        win1, win2 = SpaceCardDeck.play_recursive_combat(deck1.subdeck(c1), deck2.subdeck(c2))
        if len(win1) > len(win2):
          # winner = deck 1
          deck1.add(c1, c2)
        else:
          deck2.add(c2, c1)
      else:
        # normal round of combat
        if c1 > c2:
          deck1.add(c1, c2)
        else:
          # c1 < c2
          deck2.add(c2, c1)

    return (deck1, deck2)
 

def deck_score(deck):
  cards = list(deck.cards)
  cards.reverse()
  return sum([(index + 1) * card for index, card in enumerate(cards)])
  

def part1(things):
  d1, d2 = things

  result1, result2 = SpaceCardDeck.play_combat(d1, d2)

  return max(deck_score(result1), deck_score(result2))

def part2(things):
  d1, d2 = things
  result1, result2 = SpaceCardDeck.play_recursive_combat(d1, d2)
  return max(deck_score(result1), deck_score(result2))


def main(filename):
  things = [SpaceCardDeck.from_lines(g) for g in load_groups(filename)]

  #print("part 1:", part1(things))
  print("part 2:", part2(things))


if __name__ == "__main__":
  parser = argparse.ArgumentParser()
  parser.add_argument('input', nargs='?', default='/dev/stdin')

  args = parser.parse_args(sys.argv[1:])
  main(args.input)
