#!/usr/bin/env python3
import plotly
import requests

saved = requests.get("https://pub.ytvwld.de/dorfleaks.json").json()

plotly.offline.plot({
	"data": [plotly.graph_objs.Bar(
		x = list(saved["count"].keys()),
		y = list(saved["count"].values())
	)],
	"layout": {
		"title": "tweets containing #dorfleaks per day"
	}
})
