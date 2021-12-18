#!/usr/bin/env python-mr

from collections import defaultdict
from _.data.formatting.blocks import Block

class BitString:
  def __init__(self, value):
    self._v = value
    self._o = 0

  def __str__(self):
    return self._v

  def remaining(self):
    return len(self._v) - self._o

  def rest(self):
    r = self._v[self._o:]
    self._o = len(self._v)
    return r

  def take(self, n):
    if len(self._v) < self._o + n:
      raise ValueError("Taking too much")

    self._o += n
    r = self._v[self._o - n:self._o]
    return r

  def peek(self, n=1):
    if len(self._v) < self._o + n:
      raise ValueError("Peeking too much")
    return self._v[self._o:self._o + n]


def bits(s):
  M = { v: "{:04b}".format(i) for i, v in enumerate("0123456789ABCDEF")}
  out = ""
  for c in s:
    out += M[c]
  return BitString(out)


def VarIntRead(bt):
  groups = []
  cont = True
  while cont:
    cont = bt.take(1) == "1"
    groups.append(bt.take(4))

  return groups


def ReadAllPackets(bt):
  ps = []
  while bt.remaining():
    ps.append(Packet(bt))

  return ps


def ReadManyPackets(bt, count):
  ps = []
  while len(ps) < count:
    ps.append(Packet(bt))

  return ps


def product(i):
  m = 1
  for value in i:
    m *= value
  return m


def EvalPacket(packet):
  version, typeid, subpackets = packet

  if typeid == 0:
    return sum([EvalPacket(p) for p in subpackets])
  elif typeid == 1:
    return product([EvalPacket(p) for p in subpackets])
  elif typeid == 2:
    return min([EvalPacket(p) for p in subpackets])
  elif typeid == 3:
    return max([EvalPacket(p) for p in subpackets])
  elif typeid == 4:
    return subpackets
  elif typeid in (5, 6, 7):
    s1, s2 = subpackets

    if typeid == 5 and EvalPacket(s1) > EvalPacket(s2):
      return 1
    elif typeid == 6 and EvalPacket(s1) < EvalPacket(s2):
      return 1
    elif typeid == 7 and EvalPacket(s1) == EvalPacket(s2):
      return 1

    return 0
  else:
    raise Exception("Unknown packet type: " + str(typeid))


def Packet(bt):
  version = int(bt.take(3), base=2)
  typeid = int(bt.take(3), base=2)

  if typeid == 4:
    # Literal
    return (version, typeid, int(''.join(VarIntRead(bt)), base=2))
  else:
    # operator
    ps = []
    lentype = bt.take(1)
    if lentype == "0":
      subpacket_bit_length = int(bt.take(15), base=2)
      sub = BitString(bt.take(subpacket_bit_length))
      ps = ReadAllPackets(sub)
    else:
      subpacket_count = int(bt.take(11), base=2)
      ps = ReadManyPackets(bt, subpacket_count)

    return (version, typeid, ps)


def sum_versions(p):
  version, typeid, other = p
  if typeid != 4:
    return sum([sum_versions(sub) for sub in other]) + version
  return version


def PART1(inputs):
  for i in inputs:
    p = Packet(bits(i))
    print(p)
    print("sum", sum_versions(p)) 


def PART2(inputs):
  for i in inputs:
    p = Packet(bits(i))
    print(p)
    print("eval", EvalPacket(p)) 
