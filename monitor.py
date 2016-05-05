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
		print "Reddit:"

	elif "hacker-news.firebaseio.com" in url:
		results = hn_stats(url)
		print "HackerNews:"

	else:
		print "Unkown site."
		return

	print results[0], 'points,', results[1], 'comments'

print_stats("http://www.reddit.com/r/github/comments/4hzlt6/a_chrome_extension_to_display_project_activity_on.json")
print_stats("https://www.reddit.com/r/javascript/comments/4hzkxh/a_chrome_extension_to_display_project_activity_on.json")
print_stats("https://hacker-news.firebaseio.com/v0/item/11635339.json")