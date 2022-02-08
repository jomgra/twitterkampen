import os.path
import requests
import json
#import unicodedata
import time
import sqlite3
import configparser
from datetime import date

year = str(date.today().year)

path = os.path.dirname(os.path.realpath(__file__))

db = path + '/tweetkampen.db'

partierna = {
	"vänsterpartiet": "17233550",
	"liberalerna": "18687011",
	"socialdemokraterna": "3801501",
	"moderaterna": "19226961",
	"kristdemokraterna": "19014898",
	"centerpartiet": "3796501",
	"sverigedemokraterna": "97878686",
	"miljöpartiet": "18124359"
	}
	
def createconnection(db_file):
	conn = None
	try:
		conn = sqlite3.connect(db_file)
	except Error as e:
		print(e)
	
	return conn


def createdb(db):
	conn = createconnection(db)
	cursor = conn.cursor()
	sql = '''
	CREATE TABLE "tweetkampen" (
		"parti" TEXT,
		"datum" TEXT,
		"id" TEXT,
		PRIMARY KEY("id")
		)
	'''
	cursor.execute(sql)
	
	conn.close()
	return


def auth():
	config = configparser.ConfigParser()
	config.read("default.ini")
	token = config["twitter"]["bearer_token"]
	return token
    
def create_headers(bearer_token):
	headers = {"Authorization": "Bearer {}".format(bearer_token)}
	return headers

def create_url(userid):
	search_url = f"https://api.twitter.com/2/users/{userid}/tweets" 

	query = {
    	'max_results': 100,
    	'tweet.fields': 'created_at'
	}
	
	return (search_url, query)
    
def connect_to_endpoint(url, headers, params, next_token = None):
	time.sleep(5)
	params['pagination_token'] = next_token   #params object received from create_url function
	response = requests.request("GET", url, headers = headers, params = params)
	if response.status_code != 200:
		raise Exception(response.status_code, response.text)
	return response.json()

def addTweet(e):
	try:
		conn = createconnection(db)
		cursor = conn.cursor()
		sql = f'INSERT INTO tweetkampen ( parti, datum, id ) values ("{e[0]}","{e[1]}", "{e[2]}")'
		cursor.execute(sql)
		conn.commit()
		conn.close()
	except:
		pass
	
	return


def getLatest(parti):
	try:
		conn = createconnection(db)
		cursor = conn.cursor()
		sql = f'SELECT * FROM tweetkampen WHERE parti="{parti}" ORDER BY datum DESC'
		cursor.execute(sql)
		r = cursor.fetchone()
		conn.close()
	except:
		r = []
		pass
	
	return r


if not os.path.isfile(db):
	createdb(db)
	
	for parti in partierna:
		print("\n" + parti, end="")
		ntoken = None
		date = year
		bearer_token = auth()
		headers = create_headers(bearer_token)
		url = create_url(partierna[parti])
		
		while date == year and ntoken != "empty":
			print(".", end="")
			r = connect_to_endpoint(url[0], headers, url[1], ntoken)
			if "next_token" in r["meta"]:
				ntoken = r["meta"]["next_token"]
			else:
				ntoken = "empty"
				
			for tweet in r["data"]:
				a = []
				a.append(parti)
				a.append(tweet["created_at"][0:10])
				date = tweet["created_at"][0:4]
				a.append(tweet["id"])
				if date == year:
					addTweet(a)
else:
	bearer_token = auth()
	headers = create_headers(bearer_token)
	
	for parti in partierna:
		print(parti, end="")
		url = create_url(partierna[parti])
		latest = getLatest(parti)
		if len(latest)==3:
			param = {"since_id" : latest[2]}
			
			url[1].update(param)
		
		r = connect_to_endpoint(url[0], headers, url[1])
		if "data" in r:
			print(" (" + str(len(r["data"])) + " tweets added)")
			for tweet in r["data"]:
				a = []
				a.append(parti)
				a.append(tweet["created_at"][0:10])
				a.append(tweet["id"])
				addTweet(a)
		else:
			print(" (0 tweets added)")
