#!/usr/bin/python

import sys
import json
import urllib
import urllib2
import time

from tinydb import TinyDB, where

# Multiple Projects, each with multiple Events (release, blog post...), each with multiple Links (Reddit, HN, FB, Twitter...)
# A Record is a set of numbers related to a Link at a point in time.

# TODO
# - single cong file for all projects
# - add WP, Twitter, FB support (for Twitter: https://github.com/bear/python-twitter), GitHub release pages?
# - run as a daemon, updating records periodically (use http://stackoverflow.com/questions/16420092/how-to-make-python-script-run-as-service ?)
# - web interface?
# - save comments?
# - keep conf in DB
# - automatically get new posts from Reddit/HN from user page?

db = TinyDB('records.json')

def main():
	conf = load_config()

	print '===', conf['project_name'], '==='

	for event in conf['events']:
		print '[', event['event_name'], ']'

		for url in event['urls']:
			record = get_record(url)
			db.insert(record.to_json())
			print record
		

class Record:
	def __init__(self, score=0, num_comments=0, site='unknown site', timestamp=time.time()):
		self.site = site
		self.score = score
		self.num_comments = num_comments
		self.timestamp = timestamp
		# TODO project, event, link_url, target_url, section (eg subreddit)

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
	if len(sys.argv) == 2:
		project_conf = sys.argv[1]

		with open(project_conf, 'r') as f:
			conf = json.loads(f.read())
		f.closed

		return conf

	else:
		print 'Usage: ./monitor.py conf/conf_file.json'
		exit(0)

main()