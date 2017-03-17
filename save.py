#!/usr/bin/env python3
APP_KEY = ""
APP_SECRET = ""

import twython
import dateutil.parser
import json
from os import environ

if APP_KEY or APP_SECRET:
	print("[WARN]: Please set the api secrets via environment.")

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

twitter = twython.Twython(APP_KEY, APP_SECRET)

if not "users" in saved:
	print("Gathering additional data about existing tweets...")
	users = dict()
	for id in saved["ids"]:
		try:
			status = twitter.show_status(id=id)
			user = status["user"]["screen_name"]
		except twython.exceptions.TwythonError as exc:
			if exc.error_code == 403:
				print("The user who posted {} is no longer publicly visible.".format(id))
				user = "n/a"
			else:
				raise
		if not user in users:
			users[user] = 1
		else:
			users[user] += 1
		print("Saved {} by {}.".format(id, user))
	saved["users"] = users # don't do this partially

dorfleaks = twitter.search(q='#dorfleaks', count=1024, result_type="recent")["statuses"]

for status in dorfleaks:
	#print(status.keys())
	if not status["retweeted"] and not status["text"].startswith("RT @"):
		date = str(dateutil.parser.parse(status["created_at"]).date())
		id = status["id"]
		user = status["user"]["screen_name"]
		if id not in saved["ids"]:
			if not date in saved["count"]:
				saved["count"][date] = 1
			else:
				saved["count"][date] += 1
			if not user in saved["users"]:
				saved["users"][user] = 1
			else:
				saved["users"][user] += 1
			print("Saved {} on {} by {}.".format(id, date, user))
			saved["ids"].append(id)
		#print(status["text"], dateutil.parser.parse(status["created_at"]))

saved_file = open("dorfleaks-saved.json", "w")
json.dump(saved, saved_file)
saved_file.close()
