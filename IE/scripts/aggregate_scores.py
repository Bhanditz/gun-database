import sys

#victim-section	name	0.0	1	0.0	['Kail Miramontes']	None

scores = {}

for line in sys.stdin:
  aid, sec, field, found, skipped, total, gold, system = line.strip().split('\t')
  field = '%s %s'%(sec, field)
  if field not in scores:
    scores[field] = [0., 0., 0.] #correct, skipped, total
  scores[field][0] += float(found)
  scores[field][1] += float(skipped)
  scores[field][2] += float(total)


for c in scores:
  f, s, t = scores[c]
  attempted = t - s
  P = f/attempted
  R = f/t
  #print f
  #print s
  #print t
  print '%s\t%.04f\t%.04f\t%s\t%s'%(c, P, R, attempted, t)




    

