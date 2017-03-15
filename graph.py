#!/usr/bin/env python3
import plotly
import argparse
import sys

parser = argparse.ArgumentParser(description="Plots various statistics about #dorfleaks")
parser.add_argument("--what", type=str, choices=["per_date", "per_weekday", "per_weekday_week"], default='per_date')
parser.add_argument("--from_url", type=str, help="path to dorfleaks-saved.json", default="https://pub.ytvwld.de/dorfleaks.json", metavar="URL")
parser.add_argument("--from_file", type=str, help="path to dorfleaks-saved.json", default="dorfleaks-saved.json", metavar="FILE")
parser.add_argument("--to_file", type=str, help="output filename", default="plot.html", metavar="FILE")
parser.add_argument("--fetch_offline", help="load the data from the specified file", action="store_true")
parser.add_argument("--plot_online", help="plot the data using plot.ly", action="store_true")
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

if args.what == "per_date":
    data = plotly.graph_objs.Data([plotly.graph_objs.Bar(
        x = list(saved["count"].keys()),
        y = list(saved["count"].values())
    )])
    layout = plotly.graph_objs.Layout(title="tweets containing #dorfleaks per date")
elif args.what == "per_weekday":
    import datetime
    count = {}
    for day in range(0, 7):
        count[day] = 0
    for date_iso in saved["count"].keys():
        date = datetime.date(*map(int, date_iso.split("-"))) # Why is there no fromiso?
        count[date.weekday()] += saved["count"][date_iso]
    data = plotly.graph_objs.Data([plotly.graph_objs.Bar(
        x = list(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]),
        y = list(count.values())
    )])
    layout = plotly.graph_objs.Layout(title="tweets containing #dorfleaks per weekday")
elif args.what == "per_weekday_week":
    import datetime
    count = {}
    for date_iso in saved["count"].keys():
        date = datetime.date(*map(int, date_iso.split("-"))) # Why is there no fromiso?
        week = date.isocalendar()[1]
        if not week in count.keys():
            count[week] = {}
            for day in range(0, 7):
                count[week][day] = 0
        count[week][date.weekday()] += saved["count"][date_iso]
    data = []
    for week in count.keys():
        data += [plotly.graph_objs.Bar(
            x = list(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]),
            y = list(count[week].values()),
            name = "week #{}".format(week)
        )]
    layout = plotly.graph_objs.Layout(
        title="tweets containung #dorfleaks per weekday in each week",
        barmode="stack"
    )
else:
    raise Exception


figure = plotly.graph_objs.Figure(data=data, layout=layout)

if args.plot_online:
    url = plotly.plotly.plot(figure, auto_open=False)
    print("Saved to {}.".format(url), file=sys.stderr)
else:
    # If you installed python3-plotly via apt, this will fail.
    # Please see https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=834528.
    if args.to_file == "-":
        print(plotly.offline.plot(figure, output_type="div"))
    else:
        plotly.offline.plot(figure, output_type="file", filename=args.to_file, auto_open=False)
        print("Saved to {}.".format(args.to_file), file=sys.stderr)


