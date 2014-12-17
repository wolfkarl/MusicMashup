import json
from pprint import pprint
json_data=open('clutchconcerts.json')

data = json.load(json_data)
# pprint(data)
# json_data.close()

print data["resultsPage"]["results"]["event"][0]["displayName"]
print len(data["resultsPage"]["results"]["event"])

print "================"

print data["resultsPage"]["totalEntries"]

numberOfConcerts = len(data["resultsPage"]["results"]["event"])

for i in range(numberOfConcerts):
	print data["resultsPage"]["results"]["event"][i]["displayName"]