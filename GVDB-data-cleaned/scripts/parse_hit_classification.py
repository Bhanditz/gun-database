import sys
import csv

csv.field_size_limit(sys.maxsize)

for row in csv.reader(open(sys.argv[1]), delimiter='\t'):
  print '\t'.join([row[0], row[1], row[2]])
  
