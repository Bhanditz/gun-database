import csv
import sys
import json
import pdb

goldfile = 'Articles-with-extracted-info.tsv'
systemfile = 'system.json'
fuzzy = False
if len(sys.argv) > 1:
  fuzzy = (sys.argv[1] == 'fuzzy')



#9	Bridgeport man murdered in 9th homocide this year	{"circumstances":{"number-of-shots-fired":{"endIndex":1073,"startIndex":1071,"value":"3 "},"type-of-gun":{"endIndex":1115,"startIndex":1098,"value":"22 caliber pistol"}},"date-and-time":{"city":{"endIndex":59,"startIndex":49,"value":"Bridgeport"},"clock-time":{"endIndex":489,"startIndex":480,"value":"2:30 p.m."},"date":"2014-07-29","details":{"endIndex":470,"startIndex":435,"value":"near Reservoir and Trumbull avenues"},"state":"CT - Connecticut","time-day":{"endIndex":489,"startIndex":485,"value":"p.m."}},"radio1":{"The firearm was used during another crime.":"Not mentioned","The firearm was used in self defense.":"Not mentioned","The incident was a case of domestic violence.":"Not mentioned","The shooter and the victim knew each other.":"Not mentioned"},"radio2":{"Alcohol was involved.":"Not mentioned","Drugs (other than alcohol) were involved.":"Not mentioned","The shooting was a suicide or suicide attempt.":"Not mentioned","The shooting was self-directed.":"Not mentioned"},"radio3":{"The firearm was owned by the victim/victims family.":"Not mentioned","The firearm was stolen.":"Not mentioned","The shooting was by a police officer.":"Not mentioned","The shooting was directed at a police officer.":"No","The shooting was unintentional.":"Not mentioned"},"shooter-section":[],"victim-section":[{"age":{"endIndex":542,"startIndex":540,"value":"26"},"gender":"Male","name":{"endIndex":95,"startIndex":76,"value":"Christopher Pettway"},"race":{"endIndex":-1,"startIndex":-1,"value":""},"victim-was":["killed"]}]}

#checkfields = [("victim-section", "victim-was"), ("victim-section", "name"), ("date-and-time", "time-day"), ("date-and-time", "details"), ("shooter-section", "name"), ("circumstances", "type-of-gun")]
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
    #print "%s NA"%eid
    #return
    return found, 0, total, None
  for d in system[eid]:
    s = get_value(section, field, d)
    #sometimes we want to check other fields
    if s is not None:
      for _gg in g:
	gg = _gg[0] #ignore the indicies for now
	attempted.add(gg)
        if gg not in was_found:	
	  #if gg == 'Anna Roseberry':
	  #  pdb.set_trace()
          for _ss in s:
	    ss = _ss[0]
	    if not fuzzy: 
	      if gg == ss:
	        found += 1
	        was_found.add(gg)
	    else:
  	      if (gg in ss) or (ss in gg): 
	        found += 1
	        was_found.add(gg)
  	      #elif (ss in gg): 
	        #found += 1./len(gg.split())
	        #was_found.add(gg)
    #else:
      #print "S is None"
  skipped = len(g) - len(attempted)
  return found, skipped, total, s
    
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
      if field in data[section]:
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
      print '\t'.join([eid, section, field, str(found), str(skipped), str(total), str(gold), str(s)])
  
