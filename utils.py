import re

__Digits = re.compile("-?\d+")

def read_numbers(line, kind=int):
  nums = []
  for d in __Digits.finditer(line):
    nums.append(kind(d.group()))
  return nums
