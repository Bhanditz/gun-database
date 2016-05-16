import sys


#no	HeadlineHIT	http://www.wapakdailynews.com/ad-type/featured-ad

seen = set()

for line in sys.stdin:
  ans, hit, url = line.strip().split('\t')
  if url not in seen:
    seen.add(url)
    print line.strip()
