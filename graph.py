#!/usr/bin/env python3
from collections import defaultdict
import plotly
import argparse
import sys
import datetime

from save import deserialize

parser = argparse.ArgumentParser(
    description="Plots various statistics about #dorfleaks"
)
parser.add_argument(
    "--what", type=str,
    choices=["per_date", "per_hour", "per_weekday", "per_weekday_week", "per_user"],
    default='per_date',
)
parser.add_argument(
    "--from_url", type=str, help="path to dorfleaks-saved.json",
    default="https://chaosdorf.de/~ytvwld/dorfleaks.json", metavar="URL",
)
parser.add_argument(
    "--from_file", type=str, help="path to dorfleaks-saved.json",
    default="dorfleaks-saved.json", metavar="FILE",
)
parser.add_argument(
    "--to_file", type=str, help="output filename", default="", metavar="FILE",
)
parser.add_argument(
    "--fetch_offline", help="load the data from the specified file",
    action="store_true",
)
parser.add_argument(
    "--plot_online", help="plot the data using plot.ly", action="store_true"
)
parser.add_argument(
    "--template", help="select the design to use", default="plotly"
)
parser.add_argument(
    "--display", help="display the graph after plotting", action="store_true"
)
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

saved = deserialize(saved)

print("Plotting...", file=sys.stderr)


_WEEKDAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")

data = list()

if args.what == "per_date":
    count: dict[str, int] = defaultdict(lambda: 0)
    for toot in saved["toots"].values():
        date = toot.timestamp.date().isoformat()
        count[date] += 1
    data += [plotly.graph_objs.Bar(
        x=list(count.keys()),
        y=list(count.values()),
    )]
    layout = plotly.graph_objs.Layout(
        title="toots containing #dorfleaks per date",
        template=args.template,
    )
elif args.what == "per_hour":
    count: dict[int, int] = defaultdict(lambda: 0)
    for toot in saved["toots"].values():
        hour = toot.timestamp.time().hour
        count[hour] += 1
    data += [plotly.graph_objs.Bar(
        x=list(count.keys()),
        y=list(count.values()),
    )]
    layout = plotly.graph_objs.Layout(
        title="toots containing #dorfleaks per hour",
        template=args.template,
    )
elif args.what == "per_weekday":
    count: dict[int, int] = dict()
    for day in range(0, 7):
        count[day] = 0
    for toot in saved["toots"].values():
        count[toot.timestamp.weekday()] += 1
    data += [plotly.graph_objs.Bar(
        x=_WEEKDAYS,
        y=list(count.values()),
    )]
    layout = plotly.graph_objs.Layout(
        title="toots containing #dorfleaks per weekday",
        template=args.template,
    )
elif args.what == "per_weekday_week":
    count: dict[str, dict[int, int]] = defaultdict(lambda: {
        day: 0
        for day in range(0, 7)
    })
    for toot in saved["toots"].values():
        week = toot.timestamp.date().isocalendar().week
        weekday = toot.timestamp.date().weekday()
        count[week][weekday] += 1
    for week, days in count.items():
        data += [plotly.graph_objs.Bar(
            x=_WEEKDAYS,
            y=list(days.values()),
            name="week #{}".format(week),
        )]
    layout = plotly.graph_objs.Layout(
        title="toots containing #dorfleaks per weekday in each week",
        barmode="stack",
        template=args.template,
    )
elif args.what == "per_user":
    count = defaultdict(lambda: 0)
    for toot in saved["toots"].values():
        count[toot.author] += 1
    data += [plotly.graph_objs.Bar(
        x=list(count.keys()),
        y=list(count.values())
    )]
    layout = plotly.graph_objs.Layout(
        title="tweets containing #dorfleaks per user",
        xaxis=plotly.graph_objs.layout.XAxis(
            type="category",
            categoryorder="category ascending"
            # "value ascending" would be nice, but it isn't implemented in plotly, yet.
            # see https://github.com/plotly/plotly.js/blob/388287b09dd88634b9603a8599321ad73d95c352/src/plots/cartesian/layout_attributes.js#L495
        ),
        template=args.template,
    )
else:
    raise Exception

figure = plotly.graph_objs.Figure(data=data, layout=layout)

filename = (
    args.to_file if args.to_file else "dorfleaks_{}.html".format(args.what)
)

if args.plot_online:
    # You will need to login to plot.ly beforehand.
    # Please see https://plot.ly/python/getting-started/.
    url = plotly.plotly.plot(figure, auto_open=False, filename=filename)
else:
    # If you installed python3-plotly via apt, this will fail.
    # Please see https://bugs.debian.org/cgi-bin/bugreport.cgi?bug=834528.
    if args.to_file == "-":
        print(plotly.offline.plot(figure, output_type="div"))
        url = "-"
    else:
        url = plotly.offline.plot(
            figure, output_type="file", filename=filename, auto_open=False
        )
print("Saved to {}.".format(url), file=sys.stderr)
if args.display:
    if args.to_file == "-":
        print("[ERR] Can't open stdout to display the graph.", file=sys.stderr)
    else:
        print("Opening {}...".format(url))
        import webbrowser
        webbrowser.open(url)
