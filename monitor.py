#!/usr/bin/python

import sys
import json
import urllib
import urllib2
import time

from tinydb import TinyDB, where

# Multiple Projects, each with multiple Events (release, blog post...), each with multiple Links (Reddit, HN, FB, Twitter...)
# A Record is a set of numbers related to a Link at a point in time.

db = TinyDB('db.json')

def main():
	conf = load_config()

	print '=', conf['name'], '='

	for url in conf['urls']:
		print get_stats(url)



class Record:
	def __init__(self, score=0, num_comments=0, site='unknown site'):
		self.site = site
		self.score = score
		self.num_comments = num_comments

	def __str__(self):
		return self.site + ': ' + str(self.score) + ' points, ' + str(self.num_comments) + ' comments'



def get_stats(url):
	if "reddit.com" in url:
		record = reddit_stats(url)
		record.site = "Reddit"

	elif "hacker-news.firebaseio.com" in url:
		record = hn_stats(url)
		record.site = "HackerNews"

	elif "news.ycombinator.com" in url:
		record = hn_stats('https://hacker-news.firebaseio.com/v0/item/' + url.split("=")[1] + '.json')
		record.site = "HackerNews"

	else:
		print "Unkown site."
		return

	#db.insert({'site': site, 'points': results[0], 'comments': results[0], 'time': time.time()})

	return record

def reddit_stats(url):
	data = json.loads(read_url(url))
	data = data[0]['data']['children'][0]['data']
	return Record(data['score'], data['num_comments'])

def hn_stats(url):
	data = json.loads(read_url(url))
	return Record(data['score'], data['descendants'])

def read_url(url):
	hdr = { 'User-Agent' : 'PostMonitor' }
	req = urllib2.Request(url, headers=hdr)
	return urllib2.urlopen(req).read()

def load_config():
	if len(sys.argv) == 2:
		with open(sys.argv[1], 'r') as f:
			conf = json.loads(f.read())
		f.closed
		return conf

	else:
		print 'Usage: ./monitor.py conf/conf_file.json'
		exit(0)

main()




