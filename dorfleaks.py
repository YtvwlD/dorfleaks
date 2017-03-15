#!/usr/bin/env python3
APP_KEY = ""
APP_SECRET = ""

from twython import Twython
import dateutil.parser
import json
from os import environ
APP_KEY = environ["TWITTER_APP_KEY"] if "TWITTER_APP_KEY" in environ else APP_KEY
APP_SECRET = environ["TWITTER_APP_SECRET"] if "TWITTER_APP_SECRET" in environ else APP_SECRET

saved = None
try:
	saved_file = open("dorfleaks-saved.json", "r")
	saved = json.load(saved_file)
	saved_file.close()
except FileNotFoundError:
	pass

if not saved:
	saved = dict()
	saved["count"] = dict()
	saved["ids"] = list()

twitter = Twython(APP_KEY, APP_SECRET)

dorfleaks = twitter.search(q='#dorfleaks', count=1024, result_type="recent")["statuses"]

for status in dorfleaks:
	#print(status.keys())
	if not status["retweeted"] and not status["text"].startswith("RT @"):
		date = str(dateutil.parser.parse(status["created_at"]).date())
		id = status["id"]
		if id not in saved["ids"]:
			if not date in saved["count"]:
				saved["count"][date] = 1
			else:
				saved["count"][date] += 1
			print("Saved {}.".format(id))
			saved["ids"].append(id)
		#print(status["text"], dateutil.parser.parse(status["created_at"]))

saved_file = open("dorfleaks-saved.json", "w")
json.dump(saved, saved_file)
saved_file.close()
