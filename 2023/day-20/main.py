#!/usr/bin/env python-mr

from collections import defaultdict
from dataclasses import dataclass
from typing import NamedTuple
from _.data.formatting.blocks import Block
from _.games.advent_of_code.utils import read_numbers

import math

class RXException(Exception):
  pass

class Signal(NamedTuple):
  name: str
  state: bool

@dataclass
class Through:
  name: str
  outputs: list[str]

  @staticmethod
  def parse(line):
    name, outs = line.split(" -> ")
    return Through(name, outs.split(", "))

@dataclass
class FlipFlop:
  name: str
  outputs: list[str]
  # TODO: move out of this class, removes state from classes.
  state: bool

  @staticmethod
  def parse(line):
    assert line[0] == "%"
    name, outs = line[1:].split(" -> ")
    return FlipFlop(name, outs.split(", "), False)

@dataclass
class Conjunction:
  name: str
  inputs: list[str]
  outputs: list[str]

  @staticmethod
  def parse(line):
    assert line[0] == "&"
    name, outs = line[1:].split(" -> ")
    return Conjunction(name, list(), outs.split(", "))

LOAD = "content"
def REWRITE(lines):
  items = {}
  for l in lines:
    if l[0] == "%":
      ff = FlipFlop.parse(l)
      items[ff.name] = ff
    elif l[0] == "&":
      c = Conjunction.parse(l)
      items[c.name] = c
    else:
      b = Through.parse(l)
      items["broadcast"] = b

  keys = list(items.keys())
  keys.sort()
  print(keys)

  for i in items.values():
    for o in i.outputs:
      if o in items and type(items[o]) == Conjunction:
        items[o].inputs.append(i.name)

  return items

def TEST(inputs):
  pass

def pulse(histates, signals, thing, hilo, rxsignals=None):
  if rxsignals is not None:
    if (hilo, thing.name) not in rxsignals:
      rxsignals[(hilo, thing.name)] = 0
    rxsignals[(hilo, thing.name)] += 1

  if hilo:
    histates.add(thing.name)
  else:
    histates.discard(thing.name)

  for o in thing.outputs:
    #print("signal", thing.name, f"-{'high' if hilo else 'low'}->", o)
    signals.append(Signal(o, hilo))

def pushbotton(histates, items, rxsignals=None):
  lo = 0
  hi = 0
  signals = []

  pulse(histates, signals, Through("button", ["broadcast"]), False)
  
  while signals:
    name, hilo = signals.pop(0)
    #print(">", name, hilo)

    # Do counting.
    if hilo:
      hi += 1
    else:
      lo += 1

    if name not in items:
      #print(f"signal to missing item {name}")
      continue

    thing = items[name]
    if type(thing) == FlipFlop:
      if not hilo:
        # flip flops ignore high pulses.
        thing.state = not thing.state
        pulse(histates, signals, thing, thing.state, rxsignals=rxsignals)
    elif type(thing) == Conjunction:
      # Conjunctions fire:
      # * lo if all their inputs are true,
      # * hi otherwise.

      any_lo = any(map(lambda x: x not in histates, thing.inputs))
      pulse(histates, signals, thing, any_lo, rxsignals=rxsignals)
    elif type(thing) == Through:
      pulse(histates, signals, thing, False, rxsignals=rxsignals)

  return (lo, hi)

def PART1(inputs):
  # Process
  print(inputs)

  countlo, counthi = (0, 0)
  histates = set()
  for i in range(1000):
    lo, hi = pushbotton(histates, inputs)
    #print("push", i+1, "lo:", lo, "hi:", hi)
    countlo += lo
    counthi += hi

  print(countlo, counthi)
  return countlo * counthi

def PART2(inputs):
  # oops, inputs is stateful...
  for i in inputs.values():
    if type(i) == FlipFlop:
      i.state = False

  # No genealized solution for part two.
  # need to examine the graph to find subcomponents.
  # dump this into dot to visualize it.
  #
  # print("digraph mystuff {")
  # for i in inputs.values():
  #   #print(i.name, ">", ", ".join(i.outputs))
  #   for o in i.outputs:
  #     print(" ", i.name, "-->", o, ";")
  # print("}")

  # Subcomponents: 
  # * nn -> br
  # * lz -> lf
  # * tx -> fk
  # * mj -> rz
  # These feed into lb -> rx
  # lb is a conjunction, requires all inputs lo to fire rx.
  # br, lf, fk, rz are also conjunction, but with a single input

  # So we need to calculate the cycle size for each of the subcomponents.
  # We're looking for when each of the subcomponent ends recieves a hi pulse.

  check = ["br", "lf", "fk", "rz"]
  cycles = {}

  histates = set()

  pushes = 0
  while True:
    pushes += 1

    signals = {}
    pushbotton(histates, inputs, rxsignals=signals)

    if "rx" in signals and signals["rx"] == 1:
      print("oh no, brute force")
      return pushes

    for c in check:
      if signals.get((True, c), 0) == 1 and c not in cycles:
        print(f"{c} @ {pushes}")
        cycles[c] = pushes

    if len(cycles) == len(check):
      break

  # Attempt 1: 1. Wtf, that can't be right. - it is not.
  # Okay, it's exactly 1 low pulse to rx.
  # Attempt 2: 250924073918341 - yes!
  # And once again, AOC only needs simple cycle handling. phew.
  #print(cycles)
  return math.lcm(*cycles.values())

  # Brute force solution, won't work.
  tries = 0
  signals = {}
  histates = set()
  while True:
    tries += 1
    signals = [0]
    pushbotton(histates, inputs, rxsignals=signals)
    if signals[0] == 1:
      break

  return tries

