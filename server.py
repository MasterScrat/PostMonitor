#!/usr/bin/python

import json
import itertools

from flask import Flask, request, redirect, url_for
from tinydb import TinyDB, where

db = TinyDB('records.json')
app = Flask(__name__, static_url_path='')

@app.route('/all')
def all():
	return json.dumps(db.all(), sort_keys=True, indent=4, separators=(',', ': '))

@app.route('/series')
def series():
	data = db.all()

	data = sorted(data, key=lambda r: r['timestamp']) 

	grouped = {}
	for record in data:
		grouped.setdefault(to_unique_id(record), []).append(dict((key,value) for key, value in record.iteritems() if key in ('timestamp', 'score', 'num_comments')))

	return json.dumps(grouped, sort_keys=True, indent=4, separators=(',', ': '))

def to_unique_id(record):
		return record['project'] +'.'+ record['event'] +'.'+ record['url']

@app.route('/clear')
def clear():
	db.purge_tables()
	return 'ok'

if __name__ == "__main__":
	app.debug = True
	app.run(host= '0.0.0.0', port=8080)