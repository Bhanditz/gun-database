import sys
import csv
import json

#Article url	Article title	Full text	Json	Worker

MAX = 100
outdir = 'all-html-files'

def preproccess_text(text, to_html=True):
    # article text that are in db are already escaped
    # because of sqlalchemy text extraction in crawler
    # but before we check matching indexes first we need to
    # unescape html
    text = text.decode('utf-8')
    text = text.replace('\n', ' ')
    text = ' '.join(text.split())
    if not to_html:
        text = HTMLParser.HTMLParser().unescape(text)
        # HTMLParser().unescape(...) doesn't replace uppercases
        symbols = {
            '&GT;': '>',
            '&LT;': '<',
            "&QUOT;": '"',
            "&APOS;": "'",
        }
        for symbol, char in symbols.iteritems():
            text = text.replace(symbol, char)

    return text

def marktext(text, w, sidx, eidx, cls):
  if sidx > 0 and eidx > 0:
    text[sidx] = '<span class=%s>'%cls + text[sidx]
    text[eidx] = text[eidx] + '</span>'
    return text
  return text

victimcolor = '#BBDEFB'
shootercolor = '#FFCDD2'
locationcolor = ' #C8E6C9'
timecolor = '#FFECB3'
circumstancescolor = '#D1C4E9'

for i,row in enumerate(csv.DictReader(open(sys.argv[1]), delimiter='\t')):
  if i < MAX:
    print "Processing article %s"%i
    url = row['Article url']
    title = row['Article title']
    raw_text = preproccess_text(title + row['Full text'])
    text = {}
    for n,char in enumerate(list(raw_text)):
      text[n] = char
    data = json.loads(row['Json'])
    worker = row['Worker']
    outfile = open('%s/%s.html'%(outdir, i), 'w')

    outfile.write('<head><style>')
    outfile.write('span.victimname { background-color: %s; }'%victimcolor)
    outfile.write('span.shootername { background-color: %s; }'%shootercolor)
    outfile.write('span.location { background-color: %s; }'%locationcolor)
    outfile.write('span.time { background-color: %s; }'%timecolor)
    outfile.write('span.circumstances { background-color: %s; }'%circumstancescolor)
    outfile.write('</style></head>')
    outfile.write('<body>')

    #Meta information
    outfile.write('<a href="%s">%s</a>'%(url, title))
    outfile.write('<p>Workder ID: %s</p>'%worker)
    outfile.write('<p><span class=victimname>Victim Info</span></p>')
    outfile.write('<p><span class=shootername>Shooter Info</span></p>')
    outfile.write('<p><span class=location>Location Info</span></p>')
    outfile.write('<p><span class=time>Time Info</span></p>')
    outfile.write('<p><span class=circumstances>Circumstances</span></p>')
    outfile.write('<br>')

    #shooter and victim info
    for role in ['shooter', 'victim']:
      for person in data['%s-section'%role]:
        for info in ['name', 'age', 'race']:
          sidx = int(person[info]['startIndex'])
          eidx = int(person[info]['endIndex'])
          name = person[info]['value'].encode('utf-8')
	  #highlighted = raw_text[sidx:eidx]
	  #print name == highlighted, '\t', '%s-%s'%(sidx, eidx), '\t', name, '\t', highlighted
          text = marktext(text, name, sidx, eidx, '%sname'%role)

    #location info
    for info in ['city', 'details']:
        sidx = int(data['date-and-time'][info]['startIndex'])
        eidx = int(data['date-and-time'][info]['endIndex'])
        name = data['date-and-time'][info]['value'].encode('utf-8')
        text = marktext(text, name, sidx, eidx, 'location')
    for info in ['clock-time', 'time-day']:
        sidx = int(data['date-and-time'][info]['startIndex'])
        eidx = int(data['date-and-time'][info]['endIndex'])
        name = data['date-and-time'][info]['value'].encode('utf-8')
        text = marktext(text, name, sidx, eidx, 'time')

    #circumstances
    for info in ['number-of-shots-fired', 'type-of-gun']:
        sidx = int(data['circumstances'][info]['startIndex'])
        eidx = int(data['circumstances'][info]['endIndex'])
        name = data['circumstances'][info]['value'].encode('utf-8')
        text = marktext(text, name, sidx, eidx, 'circumstances')

    txt = ''
    for n in sorted(text.keys()):
      txt += text[n].encode('utf-8')
    outfile.write('<p>%s</p>'%txt)
    outfile.write('</body>')
    outfile.close()
