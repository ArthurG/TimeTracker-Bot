# https://stackoverflow.com/questions/62376753/how-would-i-create-a-bar-plot-with-multiple-start-and-end-points-on-a-single-dat

import numpy as np
import datetime as dt

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.collections import PolyCollection
import matplotlib.patches as mpatches

import csv
import json

import pytz  # to manage timezones

from PIL import Image

with open('config.txt') as json_file:
    data = json.load(json_file)

    timezoneName = data["timezone"]
    timezoneoffset = int(data['timezoneoffset'])

tz = pytz.timezone(timezoneName)


def getCalendarBuffer():
    timestampnow = dt.datetime.utcnow().timestamp() + timezoneoffset

    data = []
    with open("activity.csv") as csvfile:
        reader = csv.reader(csvfile, delimiter=";")
        for row in reader:
            try:
                if int(row[1]) > timestampnow - 604800:
                    data.append(row)
            except ValueError:
                pass

    # removing the header from the array.
    data = data[1:]

    newdata = []
    for entry in data:
        newdata.append([entry[0], "caca", str(dt.datetime.utcfromtimestamp(int(entry[1])+timezoneoffset))[:-3], str(dt.datetime.utcfromtimestamp(int(entry[2])+timezoneoffset))[:-3]])

    data = np.array(newdata)[:, :]  # converting to a numpy array

    # Afterward, we need to get all unique days in a sorted list and make dictionary using this:
    days_list = sorted(list(set([date[:10] for date in data[:, 2]])))[::-1]

    days = {day: i+1 for i, day in enumerate(days_list)}

    # Then a colormapping based on the client is made:
    clients = sorted(list(set(data[:, 0])))
    colormapping = {client: f"C{i}" for i, client in enumerate(clients)}

    # As a final setup, we need to save the start and end time for each entry:
    start_times = [dt.datetime.strptime(date[11:], "%H:%M") for date in data[:, 2]]
    end_times = [dt.datetime.strptime(date[11:], "%H:%M") for date in data[:, 3]]

    # Now we can iterate through all data points and add a vertice, color and the text location for that:
    verts, colors, texts = [], [], []
    for i, d in enumerate(data):
        client, task, date_str = d[0], d[1], d[2]
        day_num = days[date_str[:10]]
        start_date = mdates.date2num(start_times[i])
        end_date = mdates.date2num(end_times[i])

        v = [(start_date, day_num - .4),
             (start_date, day_num + .4),
             (end_date, day_num + .4),
             (end_date, day_num - .4),
             (start_date, day_num - .4)
             ]
        verts.append(v)
        colors.append(colormapping[client])
        texts.append((start_date, day_num, task[-1].upper()))

    # When you have this, it's basic Matplotlib stuff afterwards:
    # Make PolyCollection and scale
    bars = PolyCollection(verts, facecolors=colors, edgecolors=("black",))
    fig, ax = plt.subplots(figsize=(14.40, 9.00))
    ax.add_collection(bars)
    ax.autoscale()

    # Set ticks to show every 30 minutes and in specific format
    xticks = mdates.MinuteLocator(byminute=[0, 30])
    ax.xaxis.set_major_locator(xticks)
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%H:%M"))
    fig.autofmt_xdate()

    # Set y-axis to be dates
    ax.set_yticks(range(1, len(days_list) + 1))
    ax.set_yticklabels(days_list)

    # Create legend based on activites
    plt.legend(handles=[mpatches.Patch(color=color, label=client)
                        for client, color in colormapping.items()])

    # Add grid and save/show
    plt.grid()
    plt.savefig("fig.jpg", dpi=500)
