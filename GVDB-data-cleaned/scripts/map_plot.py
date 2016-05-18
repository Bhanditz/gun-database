import sys
import json
import csv

counts = {}

for row in csv.DictReader(open(sys.argv[1]), delimiter='\t'):
  data = json.loads(row['Json'])
  city = ' '.join(data['date-and-time']['city']['value'].strip().lower().encode('utf-8').split())
  if '"' in city or "'" in city:
    continue
#  if not(city.isalpha()):
#    continue
  if not city == '':
    if city not in counts:
      counts[city] = 0
    counts[city] += 1

print "<html>"
print "<head>"
print '<script type="text/javascript" src="https://www.gstatic.com/charts/loader.js"></script>'
print '<script type="text/javascript" src="https://www.google.com/jsapi"></script>'
print '<script type="text/javascript">'
print "google.charts.load('current', {'packages':['geochart']});"
print "google.charts.setOnLoadCallback(drawRegionsMap);"
print "function drawRegionsMap() {"
print "var data = google.visualization.arrayToDataTable(["
print "['Country', 'Popularity'],"

for city, count in sorted(counts.items(), key=lambda e:e[1], reverse=True):
  print "['%s', %d],"%(city, count)

print "]);"
print "var options = {"
print "displayMode: 'markers',"
print "region: 'US',"
print "resolution: 'provinces',"
print "colorAxis: {colors: ['#64B5F6', '#0D47A1']}"
print "};"
print "var chart = new google.visualization.GeoChart(document.getElementById('regions_div'));"
print "chart.draw(data, options);"
print "}"
print "</script>"
print "</head>"
print "<body>"
print '<div id="regions_div" style="width: 900px; height: 500px;"></div>'
print "</body>"
print "</html>"
