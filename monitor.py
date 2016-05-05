#!/usr/bin/python

import sys
import json
import urllib
import urllib2

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

def print_stats(url):
	if "reddit.com" in url:
		results = reddit_stats(url)
		print "Reddit:",

	elif "hacker-news.firebaseio.com" in url:
		results = hn_stats(url)
		print "HackerNews:",

	else:
		print "Unkown site."
		return

	print results[0], 'points,', results[1], 'comments'


if len(sys.argv) == 2:
	conf_file = sys.argv[1]

	with open(conf_file, 'r') as f:
		conf = json.loads(f.read())

		for url in conf['urls']:
			print_stats(url)

	f.closed
else:
	print 'Usage: ./monitor.py conf/conf_file.json'