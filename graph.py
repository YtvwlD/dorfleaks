#!/usr/bin/env python3
import plotly
import argparse
import sys
import datetime

parser = argparse.ArgumentParser(description="Plots various statistics about #dorfleaks")
parser.add_argument("--what", type=str, choices=["per_date", "per_weekday", "per_weekday_week", "per_user"], default='per_date')
parser.add_argument("--from_url", type=str, help="path to dorfleaks-saved.json", default="https://pub.ytvwld.de/dorfleaks.json", metavar="URL")
parser.add_argument("--from_file", type=str, help="path to dorfleaks-saved.json", default="dorfleaks-saved.json", metavar="FILE")
parser.add_argument("--to_file", type=str, help="output filename", default="", metavar="FILE")
parser.add_argument("--fetch_offline", help="load the data from the specified file", action="store_true")
parser.add_argument("--plot_online", help="plot the data using plot.ly", action="store_true")
parser.add_argument("--display", help="display the graph after plotting", action="store_true")
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

def _date_from_iso(date_iso):
    return datetime.date(*map(int, date_iso.split("-"))) # Why is there no fromiso?

_WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

data = list()
count = dict()

if args.what == "per_date":
    data += [plotly.graph_objs.Bar(
        x = list(saved["count"].keys()),
        y = list(saved["count"].values())
    )]
    layout = plotly.graph_objs.Layout(title="tweets containing #dorfleaks per date")
elif args.what == "per_weekday":
    for day in range(0, 7):
        count[day] = 0
    for date_iso in saved["count"].keys():
        date = _date_from_iso(date_iso)
        count[date.weekday()] += saved["count"][date_iso]
    data += [plotly.graph_objs.Bar(
        x = _WEEKDAYS,
        y = list(count.values())
    )]
    layout = plotly.graph_objs.Layout(title="tweets containing #dorfleaks per weekday")
elif args.what == "per_weekday_week":
    for date_iso in saved["count"].keys():
        date = _date_from_iso(date_iso)
        week = date.isocalendar()[1]
        if not week in count.keys():
            count[week] = {}
            for day in range(0, 7):
                count[week][day] = 0
        count[week][date.weekday()] += saved["count"][date_iso]
    for week in count.keys():
        data += [plotly.graph_objs.Bar(
            x = _WEEKDAYS,
            y = list(count[week].values()),
            name = "week #{}".format(week)
        )]
    layout = plotly.graph_objs.Layout(
        title="tweets containing #dorfleaks per weekday in each week",
        barmode="stack"
    )
elif args.what == "per_user":
    data += [plotly.graph_objs.Bar(
        x = list(saved["users"].keys()),
        y = list(saved["users"].values())
    )]
    layout = plotly.graph_objs.Layout(
        title="tweets containing #dorfleaks per user",
        xaxis=plotly.graph_objs.XAxis(
            type="category",
            categoryorder="category ascending"
            # "value ascending" would be nice, but it isn't implemented in plotly, yet.
            # see https://github.com/plotly/plotly.js/blob/388287b09dd88634b9603a8599321ad73d95c352/src/plots/cartesian/layout_attributes.js#L495
        )
    )
else:
    raise Exception

figure = plotly.graph_objs.Figure(data=data, layout=layout)

filename = args.to_file if args.to_file else "dorfleaks_{}".format(args.what)

if args.plot_online:
    url = plotly.plotly.plot(figure, auto_open=False, filename=filename)
else:
    # If you installed python3-plotly via apt, this will fail.
    # Please see https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=834528.
    if args.to_file == "-":
        print(plotly.offline.plot(figure, output_type="div"))
        url = "-"
    else:
        url = plotly.offline.plot(figure, output_type="file", filename=filename, auto_open=False)
print("Saved to {}.".format(url), file=sys.stderr)
if args.display:
    if args.to_file == "-":
        print("[ERR] Can't open stdout to display the graph.", file=sys.stderr)
    else:
        print("Opening {}...".format(url))
        import webbrowser
        webbrowser.open(url)


