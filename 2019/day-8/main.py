#!/usr/bin/env python3

import argparse
import sys

class Image(object):
  def __init__(self, layers, width, height):
    for l in layers:
      assert l.width == width
      assert l.height == height
    self.layers = layers
    self.width = width
    self.height = height

  def layer_number(self, l):
    for i in range(len(self.layers)):
      if l == self.layers[i]:
        return i
    return None

  @staticmethod
  def parse_from(data, width, height):
    data = data.strip()
    segment_length = width * height
    print("parsing...")
    print("layers:", len(data) // segment_length, "frame size:", segment_length)
    print("width:", width, "height:", height)
    print(len(data), len(data) / segment_length)
    # Turns out this is a bad assert?
    # assert len(data) == segment_length * (len(data) // segment_length)
    segments = []
    for idx in range(len(data) // segment_length):
      segments.append(data[idx * segment_length:(idx+1) * segment_length])

    return Image([Layer(l, width, height) for l in segments], width, height)


class Layer(object):
  def __init__(self, data, width, height):
    assert len(data) == width * height
    self.data = data
    self.width = width
    self.height = height

  def __repr__(self):
    output = ''
    for r in range(self.height):
      output += self.data[r * self.width : (r+1) * self.width] + "\n"

    mapped = {'0': ' ', '1': '#', '2': ' ', '\n': '\n'}
    return "".join([mapped[x] for x in output])

    
def count(func, iterable):
  c = 0
  for i in filter(func, iterable):
    c += 1
  return c


def p1(img):
  # fewest zeros
  zeros = img.width * img.height + 1
  layer = None
  for l in img.layers:
    c = count(lambda x: x == '0', l.data)
    #print(c, zeros)
    if c < zeros:
      zeros = c
      layer = l

  print("zeros:", zeros)
  ones = count(lambda x: x=='1', layer.data)
  twos = count(lambda x: x=='2', layer.data)
  print("ones:", ones, "twos:", twos)
  print("product:", ones * twos)
  print("from layer:", img.layer_number(layer))
    

def p2(img):
  # flatten the image
  # 0 - black
  # 1 - weight
  # 2 - transparent

  for l in img.layers:
    #print(l)
    pass

  out = []
  for pos in range(img.height * img.width):
    pixel = '2'
    for l in img.layers:
      pixel = l.data[pos]
      if pixel != '2':
        break
    out.append(pixel)
  assert len(out) == img.width * img.height
  print("---")
  out = Layer("".join(out), img.width, img.height)
  print(out)


if __name__ == "__main__":
  
  parser = argparse.ArgumentParser()
  parser.add_argument('input', type=argparse.FileType('r'), nargs='?', default=sys.stdin)
  parser.add_argument('--width', default=25, type=int)
  parser.add_argument('--height', default=6, type=int)

  args = parser.parse_args(sys.argv[1:])

  data = args.input.read()
  img = Image.parse_from(data, args.width, args.height)

  p1(img)
  p2(img)
