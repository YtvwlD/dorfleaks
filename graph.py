#!/usr/bin/env python3
import plotly
import argparse
import sys

parser = argparse.ArgumentParser(description="Plots various statistics about #dorfleaks")
parser.add_argument("--what", type=str, choices=["per_date"], default='per_date')
parser.add_argument("--from_url", type=str, help="path to dorfleaks-saved.json", default="https://pub.ytvwld.de/dorfleaks.json", metavar="URL")
parser.add_argument("--from_file", type=str, help="path to dorfleaks-saved.json", default="dorfleaks-saved.json", metavar="FILE")
parser.add_argument("--to_file", type=str, help="output filename", default="plot.html", metavar="FILE")
parser.add_argument("--fetch_offline", help="load the data from the specified file", action="store_true")
parser.add_argument("--plot_online", help="plot the data using plot.ly (not supported yet)", action="store_true")
args = parser.parse_args()

print("Fetching...", file=sys.stderr)

if not args.fetch_offline:
    import requests
    saved = requests.get(args.from_url).json()
else:
    import json
    if args.from_file == "-":
        saved = json.load(sys.stdin)
    else:
        saved = json.load(open(args.from_file, "rt"))

print("Plotting...", file=sys.stderr)

data = plotly.graph_objs.Data([plotly.graph_objs.Bar(
    x = list(saved["count"].keys()),
    y = list(saved["count"].values())
)])
layout = plotly.graph_objs.Layout(title="tweets containing #dorfleaks per day")
figure = plotly.graph_objs.Figure(data=data, layout=layout)

if args.plot_online:
    raise Exception("not supported yet")
else:
    # If you installed python3-plotly via apt, this will fail.
    # Please see https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=834528.
    if args.to_file == "-":
        print(plotly.offline.plot(figure, output_type="div"))
    else:
        plotly.offline.plot(figure, output_type="file", filename=args.to_file, auto_open=False)
        print("Saved to {}.".format(args.to_file), file=sys.stderr)


