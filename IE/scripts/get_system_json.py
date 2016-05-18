"""
{"circumstances":{
    "number-of-shots-fired":{"endIndex":-1,"startIndex":-1,"value":""},
    "type-of-gun":{"endIndex":-1,"startIndex":-1,"value":""}
  },
  "date-and-time":{
    "city":{"endIndex":56,"startIndex":45,"value":"Los Angeles"},
    "clock-time":{"endIndex":-1,"startIndex":-1,"value":""},
    "date":"2005-06-23",
    "details":{"endIndex":165,"startIndex":149,"value":"East Los Angeles"},
    "state":"CA - California",
    "time-day":{"endIndex":-1,"startIndex":-1,"value":""}
  },
  "shooter-section":[
    {
     "age":{"endIndex":84,"startIndex":82,"value":"23"},
     "gender":"",
     "name":{"endIndex":78,"oldEnd":78,"oldStart":-28,"startIndex":-28,"value":"Issac Greg Gomez"},
     "race":{"endIndex":100,"startIndex":94,"value":"Latino"},
    }],
  "victim-section":[
   {
     "age":{"endIndex":84,"startIndex":82,"value":"23"},
     "gender":"",
     "name":{"endIndex":78,"oldEnd":78,"oldStart":-28,"startIndex":-28,"value":"Issac Greg Gomez"},
     "race":{"endIndex":100,"startIndex":94,"value":"Latino"},
     "victim-was":["killed"]
   }]
  }
"""

import os
import sys
import json
from timex_util import * 
import xml.etree.ElementTree as et

arg_types = {'Injure': ('Agent', 'Victim'), 'Attack': ('Attacker', 'Target'), 'Die': ('Agent', 'Victim')}

rootdir = 'heng_ie_output/output_ere/'

MAX = 10

dates = json.load(open('dates.json'))

for num,f in enumerate(os.listdir(rootdir)):
#  if num >= MAX: 
#    continue
  if f.endswith('xml'):
    i = f.split('.')[0]
    sys.stderr.write('%s\n'%f)
    try: 
      tree = et.parse(rootdir+f).getroot()
      doc = tree.find('document')
    except et.ParseError:
      sys.stderr.write('Error parsing %s\n'%f)
      continue
    #Date and time from Timex extractor
    if i in dates:
      datetimes = dates[i]
      if datetimes is not None:
        date_json = { "date-and-time": { "date": "", "time-day": {"endIndex":-1,"startIndex":-1,"value":""} } }
        for typ, datetime in datetimes:
          updated = False
          date = get_day(typ, datetime)
	  if date is not None:
  	    date_json['date-and-time']['date'] = date
            updated = True
	  time = get_time(typ, datetime)
 	  if time is not None:
	    date_json['date-and-time']['time-day']['value'] = time
	    date_json['date-and-time']['time-day']['startIndex'] = 0
	    date_json['date-and-time']['time-day']['endIndex'] = 0
            updated = True
          if updated:
            print '%s\t%s'%(i, json.dumps(date_json))
      
    for event in doc.findall('event'):
      updated = False
      event_json = {  "circumstances": { "type-of-gun": {"endIndex":-1,"startIndex":-1,"value":""} }, 
		      "date-and-time": { 
			      "city": {"endIndex":-1,"startIndex":-1,"value":""}, 
			      "clock-time": {"endIndex":-1,"startIndex":-1,"value":""}, 
			      "details": {"endIndex":-1,"startIndex":-1,"value":""}, 
			      "state": "", 
			      "date": "", 
			      "time-day": {"endIndex":-1,"startIndex":-1,"value":""} }, 
		      "shooter-section":[ { "name": {"endIndex":-1,"startIndex":-1,"value":""}, }], 
		      "victim-section":[ { "name": {"endIndex":-1,"startIndex":-1,"value":""}, "victim-was": [] }]}

      etype = event.attrib['SUBTYPE'].encode('utf-8')
      if etype in ['Injure', 'Attack', 'Die']:
      
	#For debugging
        trigger = event.find('event_mention').find('anchor').find('charseq').text.encode('utf-8')
        txt = event.find('event_mention').find('extent').find('charseq').text.encode('utf-8')
        eid = event.attrib['ID'].encode('utf-8')

        #Was the victim injured or killed?
	if etype == 'Injure':
	  event_json['victim-section'][0]['victim-was'].append('injured')
	  updated = True
	if etype == 'Die':
	  event_json['victim-section'][0]['victim-was'].append('injured')
	  event_json['victim-section'][0]['victim-was'].append('killed')
	  updated = True
   
	shooter_type, victim_type = arg_types[etype]
        for arg in event.find('event_mention').findall('event_mention_argument'):
  	  if 'ROLE' in arg.attrib:
            role = arg.attrib['ROLE'].encode('utf-8')
            argex = arg.find('extent').find('charseq')
            name = argex.text.encode('utf-8')
            sidx = argex.attrib['START']
            eidx = argex.attrib['END']
	    #Name of shooter
	    if role == shooter_type:
	      event_json['shooter-section'][0]['name']['value'] = name
	      event_json['shooter-section'][0]['name']['startIndex'] = sidx
	      event_json['shooter-section'][0]['name']['endIndex'] = eidx
	      updated = True
	    #Name of victim
	    if role == victim_type:
	      event_json['victim-section'][0]['name']['value'] = name
	      event_json['victim-section'][0]['name']['startIndex'] = sidx
	      event_json['victim-section'][0]['name']['endIndex'] = eidx
	      updated = True
	    #Type of gun
	    if role == 'Instrument':
	      event_json['circumstances']['type-of-gun']['value'] = name
	      event_json['circumstances']['type-of-gun']['startIndex'] = sidx
	      event_json['circumstances']['type-of-gun']['endIndex'] = eidx
	      updated = True
	    #Time of day
	    #if role == 'Time':
	    #  event_json['date-and-time']['time-day']['value'] = name
	    #  event_json['date-and-time']['time-day']['startIndex'] = sidx
	    #  event_json['date-and-time']['time-day']['endIndex'] = eidx
	    #  updated = True
	    #Location details
	    if role == 'Place':
	      event_json['date-and-time']['details']['value'] = name
	      event_json['date-and-time']['details']['startIndex'] = sidx
	      event_json['date-and-time']['details']['endIndex'] = eidx
	      updated = True
        if updated:
          print '%s\t%s'%(i, json.dumps(event_json))
