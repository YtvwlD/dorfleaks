#!/usr/bin/env python3
import plotly
import json

saved_file = open("dorfleaks-saved.json", "r")
saved = json.load(saved_file)
saved_file.close()

plotly.offline.plot({
	"data": [plotly.graph_objs.Bar(
		x = list(saved["count"].keys()),
		y = list(saved["count"].values())
	)],
	"layout": {
		"title": "tweets containing #dorfleaks per day"
	}
})
