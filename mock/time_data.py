import sys
import datetime
import random
from collections import deque

def make_mock_data(size):
  def _get_same_time():
    d = datetime.datetime.now()
    return d, d
  def _get_first_than_second():
    d1 = datetime.datetime.now()
    d2 = datetime.datetime.now()
    return d1, d2
  def _get_second_than_first():
    d2 = datetime.datetime.now()
    d1 = datetime.datetime.now()
    return d1, d2  
  func = [_get_same_time, _get_first_than_second, _get_second_than_first]
  
  out1, out2 = deque(), deque()
  i = 0
  while len(out1) < size:
    f = random.choice(func) 
    d1, d2 = f()
    out1.append((d1, "a{}".format(i)))
    out2.append((d2, "b{}".format(i)))
    i += 1
  return out1, out2


if __name__=='__main__':
  sys.path.append('../app')
  from app import pair_images
  
  test1, test2 = make_mock_data(int(sys.argv[1]))
  print "example data:\n{}\n{}\n\n".format(test1, test2)
  pair_images(test1, test2)
  
