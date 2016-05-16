import sys
import csv
import json

#Article url	Article title	Full text	Json	Worker

MAX = 100
outdir = 'html-files'

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

print '\t'.join(['Article id', 'Article url', 'Article title', 'Full text', 'Json', 'Worker'])
seen = set()
for i,row in enumerate(csv.DictReader(open(sys.argv[1]), delimiter='\t')):
  url = row['Article url']
  title = preproccess_text(row['Article title']).encode('utf-8')
  raw_text = preproccess_text(row['Article title'] + row['Full text']).encode('utf-8')
  data = row['Json'].encode('utf-8')
  worker = row['Worker']
  if title not in seen:
    seen.add(title)
    print '\t'.join(['%s'%(i+1), url, title, raw_text, data, worker])
