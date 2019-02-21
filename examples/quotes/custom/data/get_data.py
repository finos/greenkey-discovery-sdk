
import os
#import logging
import mmap
import random
import sys
#from os.path import exists
#from collections import defaultdict

#logger = logging.getLogger(__name__)   


#def linecount_wc(   ):
#    return int(os.popen('wc -l nuc').read().split(   )[0])

#num_lines = sum(1 for line in open(infile))

def mapcount(filename):
  f = open(filename, "r+")
  buf = mmap.mmap(f.fileno(), 0)
  lines = 0
  readline = buf.readline
  while readline():
    lines += 1
  return lines


#q1 = quotes = 'quotes.txt'
#q2 = 'new_quotes.txt'

#nq1 = not_quotes = 'not_quotes.txt'
#nq2 = 'new_not_quotes'


def shuffle_and_split_data(infile, size=0.9):
  """
  :param infile: str, path to txt file containing new-line separated strings
  :param size: float; split-size, default 0.9
  """
  with open(infile, 'r+', encoding='utf-8') as f:
    data = [line.strip() for line in f.readlines()]
    random.shuffle(data)
    train_size = int(len(data)*size)
    train, test = data[:train_size], data[train_size:]
    return train, test


def write_file(outfile, data):
  with open(outfile, 'w+', encoding='utf-8') as f:
    for line in data:
      f.write(line + "\n")


def main(directory=None, size=0.9, ext='.txt'):
  if not directory:
    directory = os.getcwd()
  data_files = [f for f in os.listdir(directory) if f.endswith(ext)]
  for infile in data_files:
    train, test = shuffle_and_split_data(infile, size)
    base = infile.split('.')[0]

    train_outfile  = "{}_{}.txt".format(base, int(size*100))
    test_outfile = "{}_{}.txt".format(base, int(100-size*100))

    write_file(data=train, outfile=train_outfile)
    write_file(data=test, outfile=test_outfile)


if __name__ == '__main__':
  main()



#for i, infile in enumerate([q1, q2, q3, q4]):
#    train, test = shuffle_and_split_data(infile, p=0.9)
#    write_file(data=train, infile=f"{infile}_90.txt")
#    write_file(data=test, infile=f"{infile}_10.txt")

