import csv
import sys
import json
import pdb

goldfile = 'Articles-with-extracted-info.tsv'
systemfile = 'system.json'
fuzzy = False
if len(sys.argv) > 1:
  fuzzy = (sys.argv[1] == 'fuzzy')


checkfields = [("victim-section", "name"), ("date-and-time", "time-day"), ("date-and-time", "details"), ("shooter-section", "name"), ("circumstances", "type-of-gun"), ("date-and-time", "date")]

system = {}
for line in open(systemfile).readlines():
  docid, data = line.strip().split('\t')
  if docid not in system:
    system[docid] = []
  system[docid].append(json.loads(data))

def find_field(g, eid, section, field, value):
  total = len(g)
  found = 0.
  was_found = set()
  attempted = set()
  if eid not in system:
    return found, 0, total, None
  for d in system[eid]:
    s = get_value(section, field, d)
    #sometimes we want to check other fields
    if s is not None:
      for _gg in g:
	gg = _gg[0] #ignore the indicies for now
	attempted.add(gg)
        if gg not in was_found:	
          for _ss in s:
	    ss = _ss[0]
	    if is_match(gg, ss, field, section, fuzzy):
	      found += 1
	      was_found.add(gg)
	    #else:
              #if field == 'time-day': 
	        #sys.stderr.write("Not equal %s | %s\n"%(gg, ss))
  skipped = len(g) - len(attempted)
  return found, skipped, total, s
  
def date_eq(g, s, fuzzy=False):
  dmy_g = g.split('-')
  if len(dmy_g) < 3:
    sys.stderr.write("Skipping %s | %s\n"%(g, s))
    return True
  dmy_s = s.split('-')
  if not fuzzy:
    if len(dmy_g) == len(dmy_s):
      for ge, se in zip(dmy_g, dmy_s):
        if not(ge == se):
          #sys.stderr.write("Not equal %s | %s\n"%(g, s))
  	  return False
      return True
    #sys.stderr.write("Not equal %s | %s\n"%(g, s))
    return False
  else:
    years = False
    months = False
    days = False
    #sys.stderr.write("%s | %s\n"%(dmy_g, dmy_s))
    if dmy_g[0] == dmy_s[0] or dmy_g[0] == 'XXXX' or dmy_s[0] == 'XXXX': #year matches
      years = True
    if len(dmy_s) > 1 and ((dmy_g[1] == dmy_s[1]) or (dmy_g[1] == 'XX') or (dmy_s[1] == 'XX')): #months matches
      months = True
    if len(dmy_s) > 2 and ((dmy_g[2] == dmy_s[2]) or (dmy_g[2] == 'XX') or (dmy_s[2] == 'XX')): #days matches
      days = True
    if (years and months) or (months and days):
      return True
    return False

def time_eq(g, s, fuzzy=False):
  morning = set(['morning'])# 'am', 'a.m.'])
  afternoon = set(['afternoon']) #, 'pm', 'p.m.'])
  evening = set(['evening']) #, 'pm', 'p.m.'])
  night = set(['night']) #, 'pm', 'p.m.'])
  #sys.stderr.write("%s | %s\n"%(g, s))
  if not fuzzy:
    #Try to match time-day
    gtoks = set(g.lower().split())
    if s == 'MO':
      return (len(gtoks.intersection(morning)) > 0)
    if s == 'AF':
      return (len(gtoks.intersection(afternoon)) > 0)
    if s == 'EV':
      return (len(gtoks.intersection(evening)) > 0)
    if s == 'NI':
      return (len(gtoks.intersection(night)) > 0)
    #Try to match a clock time
    gt = g.split()
    st = s.split()
    if len(gt) == len(st):
      for ge, se in zip(gt, st):
        if not(ge == se):
          #sys.stderr.write("Not equal %s | %s\n"%(g, s))
          return False
      return True
    #sys.stderr.write("Not equal %s | %s\n"%(g, s))
    return False
  else:
    return False

def is_match(g, s, field, section, fuzzy):
  if field == 'date': 
    return date_eq(g,s,fuzzy)
  elif field == 'time-day' or field == 'clock-time':
    return time_eq(g,s)
  if fuzzy:
    return ((g in s) or (s in g))
  return g == s

def get_value(section, field, data):
  gold = []
  #print section, field, data
  if section in data: #date "events" are extracted separately from all of the other "events"
    if section in ['victim-section', 'shooter-section']:
      for d in data[section]:
        if field == 'victim-was':
          g = d[field]
	  if len(g) > 0:
            gold.append(g)
        else: 
          g = d[field]['value'].strip().encode('utf-8')
          sidx = d[field]['startIndex']
          eidx = d[field]['endIndex']
          if not(g.strip() == ''):
            gold.append((g,sidx,eidx))
    else:
      if True: #field in data[section]:
	if field == 'date' and (isinstance(data[section][field], str) or isinstance(data[section][field], unicode)):
          g = data[section][field].strip().encode('utf-8')
          sidx = 1
          eidx = 1
          if not(g.strip() == ''):
            gold.append((g,sidx,eidx))
        else:
	  #print section, field, data[section][field], type(data[section][field])
          g = data[section][field]['value'].strip().encode('utf-8')
          sidx = data[section][field]['startIndex']
          eidx = data[section][field]['endIndex']
          if not(g.strip() == ''):
            gold.append((g,sidx,eidx))

  if len(gold) == 0:
    return None
  return list(set(gold))

#Article id	Article url	Article title	Full text	Json	Worker
for row in csv.DictReader(open(goldfile), delimiter='\t'):
  eid = row['Article id']
  title = row['Article title']
  data = row['Json']
  data = json.loads(data)
  for section, field in checkfields:
    gold = get_value(section, field, data)
    if gold is not None:
      #print gold
      found, skipped, total, s = find_field(gold, eid, section, field, data)
      if field == 'details' and found == 0: #for location, try to match city if details failed
        found, skipped, total, s = find_field(gold, eid, section, 'city', data)
      if field == 'time-day' and found == 0: #for time of day, try to match clock time if time of day failed
        found, skipped, total, s = find_field(gold, eid, section, 'clock-time', data)
	sys.stderr.write("Switched to clock time\n")
        sys.stderr.write('\t'.join([eid, section, field, str(found), str(skipped), str(total), str(gold), str(s)])+'\n')
      print '\t'.join([eid, section, field, str(found), str(skipped), str(total), str(gold), str(s)])
  
