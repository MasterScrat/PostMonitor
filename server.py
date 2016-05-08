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

@app.route('/projects')
def projects():
	data = db.all()
	data = sorted(data, key=lambda r: r['timestamp'])

	# TODO should output series as 3 concatenated levels
	grouped = {}
	for record in data:
		record_values = dict((key,value) for key, value in record.iteritems() if key in ('timestamp', 'score', 'num_comments'))
		grouped.setdefault(to_event_url(record), []).append(record_values)

	return print_json(grouped)


# Dygraphs specific format
@app.route('/dygraphs')
@app.route('/dygraphs/')
@app.route('/dygraphs/<project>')
def dygraphs(project = None):
	# TODO shouldn't the DB do most of that stuff for us?! use ElasticSearch!
	db.clear_cache()
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
	event_url_num_comments = {}

	for record in data:
		timestamp = format_timestamp(record['timestamp'])
		if timestamp not in all_timestamps:
			all_timestamps.append(timestamp)

		event_url = to_event_url(record)
		if event_url not in all_event_urls:
			all_event_urls.append(event_url)

		# cache
		if event_url not in event_url_score:
			event_url_score[event_url] = {timestamp: {}}
			event_url_num_comments[event_url] = {timestamp: {}}

		event_url_score[event_url][timestamp] = record['score']
		event_url_num_comments[event_url][timestamp] = record['num_comments']

	# then for each timestamp, for each URL: check if there's a value
	# if yes put it, if not put null
	formatted_scores = []
	formatted_num_comments = []

	for timestamp in all_timestamps:
		timestamp = timestamp
		timestamp_scores = [timestamp]
		timestamp_num_comments = [timestamp]

		for event_url in all_event_urls:

			if timestamp in event_url_score[event_url]:
				timestamp_scores.append(event_url_score[event_url][timestamp])
				timestamp_num_comments.append(event_url_num_comments[event_url][timestamp])
			else:
				timestamp_scores.append(None)
				timestamp_num_comments.append(None)

		formatted_scores.append(timestamp_scores)
		formatted_num_comments.append(timestamp_num_comments)

	return print_json({'score': formatted_scores, 'num_comments': formatted_num_comments, 'labels': ['x']+all_event_urls})


def format_timestamp(timestamp):
	return int(timestamp*1000)

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