#!/usr/bin/python

import sys
import json
import urllib
import urllib2
import time

from tinydb import TinyDB, where

def read_url(url):
	hdr = { 'User-Agent' : 'PostMonitor' }
	req = urllib2.Request(url, headers=hdr)
	return urllib2.urlopen(req).read()

def reddit_stats(url):
	data = json.loads(read_url(url))
	return [data[0]['data']['children'][0]['data']['score'], data[0]['data']['children'][0]['data']['num_comments']]

def hn_stats(url):
	data = json.loads(read_url(url))
	return [data['score'], data['descendants']]

def get_stats(url):
	if "reddit.com" in url:
		results = reddit_stats(url)
		site = "Reddit"

	elif "hacker-news.firebaseio.com" in url:
		results = hn_stats(url)
		site = "HackerNews"

	elif "news.ycombinator.com" in url:
		results = hn_stats('https://hacker-news.firebaseio.com/v0/item/' + url.split("=")[1] + '.json')
		site = "HackerNews"

	else:
		print "Unkown site."
		return

	db.insert({'site': site, 'points': results[0], 'comments': results[0], 'time': time.time()})

	return [site, results[0], results[1]]

# TODO time to move to proper class's!
def print_stats(url):
	stats = get_stats(url)
	print stats[0], ':', stats[1], 'points,', stats[2], 'comments'


db = TinyDB('db.json')

if len(sys.argv) == 2:
	conf_file = sys.argv[1]

	with open(conf_file, 'r') as f:
		conf = json.loads(f.read())
		print '=', conf['name'], '='
		for url in conf['urls']:
			print_stats(url)
	f.closed

else:
	print 'Usage: ./monitor.py conf/conf_file.json'
	exit(0)





