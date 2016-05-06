#!/usr/bin/python

import sys
import json
import urllib
import urllib2
import time
import logging

from tinydb import TinyDB, where
from apscheduler.schedulers.blocking import BlockingScheduler

# Multiple Projects, each with multiple Events (release, blog post...), each with multiple Links (Reddit, HN, FB, Twitter...)
# A Record is a set of numbers related to a Link at a point in time.

# TODO
# - add WP, Twitter, FB support (for Twitter: https://github.com/bear/python-twitter), GitHub release pages?
# - web interface?
# - keep conf in DB

logging.basicConfig()
db = TinyDB('records.json')

def main():
	"""
	sched = BlockingScheduler()
	sched.add_job(get_records, 'interval', id='monitor', seconds=5, max_instances=1)
	sched.start()
	"""
	get_records()

def get_records():
	conf = load_config()
	timestamp = time.time()

	print
	print '===', conf['monitor_name'], '==='

	for project in conf['projects']:
		print
		print '=', project['project_name'], '='

		for event in project['events']:
			print '[', event['event_name'], ']'

			for url in event['urls']:
				record = get_record(url)
				record.timestamp = timestamp
				record.project = project['project_name']
				record.event = event['event_name']
				record.url = url

				db.insert(record.to_json())
				print record


class Record:
	def __init__(self, score=0, num_comments=0):
		self.score = score
		self.num_comments = num_comments

		self.timestamp = 0
		self.site = ''
		self.project = ''
		self.event = ''
		self.url = ''
		self.target = '' # TODO
		self.section = '' # TODO

	def __str__(self):
		return self.site + ': ' + str(self.score) + ' points, ' + str(self.num_comments) + ' comments'

	def to_json(self):
		return json.loads(json.dumps(self, default=lambda o: o.__dict__))



def get_record(url):
	if "reddit.com" in url:
		if ".json" not in url:
			url = url + '.json'

		record = reddit_stats(url)
		record.site = "Reddit"

	elif "hacker-news.firebaseio.com" in url:
		record = hn_stats(url)
		record.site = "HackerNews"

	elif "news.ycombinator.com" in url:
		record = hn_stats('https://hacker-news.firebaseio.com/v0/item/' + url.split("=")[1] + '.json')
		record.site = "HackerNews"

	elif "api.github.com" in url:
		record = gh_stats(url)
		record.site = "GitHub"

	else:
		raise NameError('Unkown site URL ' + url)

	return record

def reddit_stats(url):
	data = json.loads(read_url(url))
	data = data[0]['data']['children'][0]['data']
	return Record(data['score'], data['num_comments'])

def hn_stats(url):
	data = json.loads(read_url(url))
	return Record(data['score'], data['descendants'])

def gh_stats(url):
	data = json.loads(read_url(url))
	return Record(data['watchers_count'], data['subscribers_count'])

def read_url(url):
	hdr = { 'User-Agent' : 'PostMonitor' }
	req = urllib2.Request(url, headers=hdr)
	return urllib2.urlopen(req).read()

def load_config():
	with open('conf.json', 'r') as f:
		conf = json.loads(f.read())
	f.closed

	return conf

if __name__ == "__main__":
	main()