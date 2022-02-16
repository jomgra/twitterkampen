import json, sys, os.path, sqlite3
import datetime

#  SITE CLASS  ====================
#
#  x = site(output_path)
#  x.addPage(id, title, desc)
#  x.removePage(id)
#  x.save()

class site():
	def __init__(self, path):
		self.path = self._fixpath(path)
		self.id = "index"
		self.file = self.path + self.id + ".cfg"
		self._loadcfg()
		return
	
	def _fixpath(self, path):
		if path[-1] != "/":
			path += "/"
		return path
				
	def _loadcfg(self):
		
		try:
			with open(self.file, "r", encoding="utf8") as f:
				content = f.read()
				c = json.loads(content)
				self.title = c["title"]
				self.pages = c["pages"]
				self.exist = True
		except:
			self.title = ""
			self.pages = []
			self.exist = False
		return
		
	def addPage(self, index, id, title, desc):
		page = {
			"index": int(index),
			"id": self._cleanid(id),
			"title": title,
			"desc": desc
			}
		for i in range(len(self.pages)):
			if self.pages[i]["id"] == self._cleanid(id):
				self.pages.pop(i)
				break
		self.pages.append(page)	
		self.pages.sort(key=lambda x: x["index"])
		return

	def removePage(self, id):
		for i in range(len(self.pages)):
			if self.pages[i]["id"] == self._cleanid(id):
				self.pages.pop(i)
				break
		return

	def _cleanid(self, idTxt):
		chars = [" ", "å", "ä", "ö"]
		newChars = ["", "a", "a", "o"]
		idTxt = idTxt.lower()
		for i in range(len(chars)):
			idTxt = idTxt.replace(chars[i], newChars[i])
		return idTxt
	
	def dump(self):
		dump = vars(self).copy()
		dump.pop("file")
		dump.pop("path")
		dump.pop("exist")
		return dump
	
	def json(self):
		return json.dumps(self.dump())
		
	def save(self):
		try:
			with open(self.file, "w", encoding="utf8") as f:
				f.write(self.json())
				if self.exist:
					print("Updated:", self.file)
				else:
					print("Created:", self.file)
		except:
			print("Couldn't save file:", self.file)


#  CHARTJS CLASS  =================
#
#  x = chartjs(typeofchart)
#  x.addDataset(label, dataarray, clr)
#  x.addLabels(labelsarray)
#  x.save()
#  x.options - attributes
				
class chartjs:
	defaultColor = "#fff"
	
	def __init__(self, type="line"):
		self.type = type.lower()
		self.data = {
			"labels": [],
			"datasets": []
			}
		self.options = {
			"maintainAspectRatio": False,
			"tension": 0.1,
			"plugins": {
				"legend": {},
				"tooltip": {}
			},
			"scales": {
				"y": {
					"beginAtZero": True
					}
			},
			"animations": {}
			}
		return
		
	def _fixpath(self, path):
		if path[-1] != "/":
			path += "/"
		return path
		
	def _cleanid(self, idTxt):
		chars = [" ", "å", "ä", "ö"]
		newChars = ["", "a", "a", "o"]
		idTxt = idTxt.lower()
		for i in range(len(chars)):
			idTxt = idTxt.replace(chars[i], newChars[i])
		return idTxt
		
	def dump(self):
		return vars(self)
	
	def json(self):
		return json.dumps(vars(self))
	
	def addDataset(self, label, dataList, color=defaultColor):
		dset = {
			"label": label,
			"data": dataList,
			"backgroundColor": color,
			"borderColor": color
		}
		if len(dataList) > 0:
			self.data["datasets"].append(dset)
		return
	
	def addLabels(self, labels):
		if len(labels) > 0:
			self.data["labels"] = labels
		return
		
	def save(self, path, id):
		file = self._fixpath(path) + self._cleanid(id) + ".chart"
		try:
			with open(file, "w", encoding="utf8") as f:
				f.write(self.json())
			print("Saved:", file)
		except:
			print("Couldn't save file:", self.file)

#  SET DATABASE PATH ===========

path = os.path.dirname(os.path.realpath(__file__))
db = path + "/tweetkampen.db" 

if not os.path.isfile(db):
	print("No database")
	sys.exit()
	

#  SET OUTPUT PATH =============

if len(sys.argv) > 1:
	opath = sys.argv[1]
else:
	opath = path + "/"

#  GET DATA ====================

try:
	con = sqlite3.connect(db)
except Error as e:
	print(e)

cur = con.cursor()
cur.execute(f"SELECT * FROM tweetkampen ORDER BY datum")
data = cur.fetchall()
con.close()

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
			if d[0] == p and d[1] == date:
				c += 1
		if len(parti[p]) > 0:
			l = parti[p][-1]
		else:
			l = 0
		parti[p].append(c + l)
				
	sd += delta

dname = []
dset = []
for p in parti:
	dname.append(p.capitalize())
	dset.append(parti[p])


#  CHART SETUP  =================

chart = chartjs("line")

color = {
	"Vänsterpartiet": "#AF0000",
	"Socialdemokraterna": "#EE2020",
	"Miljöpartiet": "#83CF39",
	"Centerpartiet": "#009933",
	"Liberalerna": "#6BB7EC",
	"Moderaterna": "#1B49DD",
	"Kristdemokraterna": "#231977",
	"Sverigedemokraterna": "#DDDD00"
	}

chart.addLabels(label)
for p in color:
	for i in range(len(dname)):
		if p == dname[i]:
			chart.addDataset(p, dset[i], color[p])
			
chart.options = {
	"maintainAspectRatio": False,
	"plugins": {
		"legend": {
			"display": True,
			"padding": 10,
			"position": "chartArea",
			"labels": {
				"boxWidth": 30,
				"color": "#ddd",
				"padding": 15,
				"font": {
					"family": "'Segoe UI', 'Arial', 'Helvetica', sans-serif"
					}
				}
			}
		}
	}

chart.save(opath, "tweetkampen")

#  SITE SETUP  ===================

minasiffror = site(opath)

minasiffror.addPage(
	10,
	"tweetkampen",
	"Tweetkampen",
	"Vilket parti är mest aktivt på Twitter? Följ det ackumulerade antalet tweets från riksdagspartiernas officiella twitterkonton. Uppgifterna uppdateras automatiskt varje dag."
	)

minasiffror.save()
