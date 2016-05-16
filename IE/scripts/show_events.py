import os
import sys
import xml.etree.ElementTree as et

rootdir = 'heng_ie_output/output_ere/'

MAX = 10

for i,f in enumerate(os.listdir(rootdir)):
  if i >= MAX: 
    continue
  if f.endswith('xml'):
    sys.stderr.write('%s\n'%f)
    try: 
      tree = et.parse(rootdir+f).getroot()
      doc = tree.find('document')
    except et.ParseError:
      sys.stderr.write('Error parsing %s\n'%f)
      continue

    for event in doc.findall('event'):
      event_json = {}
      etype = event.attrib['SUBTYPE'].encode('utf-8')
      eid = event.attrib['ID'].encode('utf-8')
      trigger = event.find('event_mention').find('anchor').find('charseq').text.encode('utf-8')
      txt = event.find('event_mention').find('extent').find('charseq').text.encode('utf-8')
      #print txt
      #print '%s\t%s\t%s\t%s'%(i, trigger, etype)
      print '%s\t%s\t%s'%(i, eid, etype)
      for arg in event.find('event_mention').findall('event_mention_argument'):
        argex = arg.find('extent')
	if 'ROLE' in arg.attrib:
          role = arg.attrib['ROLE'].encode('utf-8')
	else:
          role = 'NA'
        name = argex.find('charseq').text.encode('utf-8')
        print '%s\t%s'%(role, name)
      print
