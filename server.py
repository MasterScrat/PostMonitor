#!/usr/bin/python

import json
import itertools
import datetime

from flask import Flask, request, redirect, url_for
from tinydb import TinyDB, where

db = TinyDB('data/records.json')
app = Flask(__name__, static_url_path='')

@app.route('/')
def root():
	return app.send_static_file('www/index.html')

@app.route('/all')
def all():
	return json.dumps(db.all(), sort_keys=True, indent=4, separators=(',', ': '))

@app.route('/series')
def series():
	data = db.all()
	data = sorted(data, key=lambda r: r['timestamp'])

	# TODO should output series as 3 concatenated levels
	grouped = {}
	for record in data:
		record_values = dict((key,value) for key, value in record.iteritems() if key in ('timestamp', 'score', 'num_comments'))
		grouped.setdefault(to_event_url(record), []).append(record_values)

	return print_json(grouped)


@app.route('/projects')
@app.route('/projects/<project>')
def projects(project = None):
	# TODO shouldn't the DB do all that stuff for us?!
	# use ElasticSearch instead!
	# TODO do this processing client-side, return only /series

	if project is None:
		data = db.all()
	else:
		data = db.search(where('project') == project)


	data = sorted(data, key=lambda r: r['timestamp'])

	# first need ordered full lists of timestamps and URLs
	# plus build cache of all values
	all_timestamps = []
	all_event_urls = []
	event_url_score = {}

	for record in data:
		timestamp = record['timestamp']
		if timestamp not in all_timestamps:
			all_timestamps.append(timestamp)

		event_url = to_event_url(record)
		if event_url not in all_event_urls:
			all_event_urls.append(event_url)

		# cache
		if event_url not in event_url_score:
			event_url_score[event_url] = {timestamp: {}}
		event_url_score[event_url][timestamp] = record['score']


	# then for each timestamp, for each URL: check if there's a value
	# if yes put it, if not put null
	formatted_values = []

	for timestamp in all_timestamps:
		timestamp_values = [int(timestamp*1000)]

		for event_url in all_event_urls:

			if timestamp in event_url_score[event_url]:
				timestamp_values.append(event_url_score[event_url][timestamp])
			else:
				timestamp_values.append(None)

		formatted_values.append(timestamp_values)

	return print_json({'values': formatted_values, 'labels': ['x']+all_event_urls})


def format_timestamp(timestamp):
	return datetime.datetime.fromtimestamp(
        int(timestamp)
    ).strftime('%Y/%m/%d %H:%M:%S')

def to_event_url(record):
		return record['project'] +' - '+ record['event'] +' - '+ record['url']

def print_json(obj):
	return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': '))


@app.route('/clear')
def clear():
	db.purge_tables()
	return 'ok'

if __name__ == "__main__":
	app.debug = True
	app.run(host= '0.0.0.0', port=8080)