import sqlite3, sys
import json
import os.path
import datetime

path = os.path.dirname(os.path.realpath(__file__))
db = path + "/tweetkampen.db" 
jsonpath = path + "/output/"


if not os.path.isfile(db):
	print("No database")
	sys.exit()
	
try:
	con = sqlite3.connect(db)
except Error as e:
	print(e)

cur = con.cursor()
cur.execute(f"SELECT * FROM tweetkampen ORDER BY datum")
data = cur.fetchall()
con.close()

print("Exporting data to json...")

delta = datetime.timedelta(days=1)
sd = datetime.date(datetime.datetime.now().year, 1, 1)
ed = datetime.date.today() - delta


parti = {}
label = []

for d in data:
	if d[0] not in parti:
		parti.update({d[0]: []})

while sd <= ed:
	date = str(sd)
	label.append(date)
	for p in parti:
		c = 0
		for d in data:
			#print(d[1],"=", d)
			if d[0] == p and d[1] == date:
				c += 1
		if len(parti[p]) > 0:
			l = parti[p][-1]
		else:
			l = 0
		parti[p].append(c + l)
				
	sd += delta

data = {
	"label" : label
	}

datasets = []
sets = []
for p in parti:
	datasets.append(p.capitalize())
	sets.append(parti[p])
	
	
data.update({ "datasets" : datasets })
data.update({ "sets" : sets })

json_string = json.dumps(data)
file = jsonpath + "tweetkampen.json"
with open(file, "w", encoding="utf8") as f:
	f.write(json_string)
	
print("Done")
