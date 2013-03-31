import fileinput
import json
import urlresolver
import urltitle
import codecs
import math
from concurrent.futures import ThreadPoolExecutor

urlresolver.load_resolved_urls()
urltitle.load_url_titles()

# we build the graph with only the top N URLs, in terms of tweets/retweets 
numTopURLs = 100

# configure output, URL resolution
verbose = False
resolved_cache_only = True     # if true, we never go across the network to try to resolve a URL
max_pending_resolutions = 10    # maximum number of URL resolves we try at once

# global state
tweetedurls = {}
numtweets = 0


# maps URL to number of times tweeted, and list of users who have tweeted/retweeted
class TweetedURL:
  def __init__(self):
    self.users = set()
    self.count = 0
    self.title = ""


# If we've seen both http and https versions of the same URL, use just the http
def canonicalize_https(url):

  if url[:7] == "http://":
    https_url = "https://" + url[7:]
    if https_url in tweetedurls:  # urls is http, but we have https in the dict, so replace with http
      t = tweetedurls[https_url] 
      del tweetedurls[https_url]
      tweetedurls[url] = t
    return url                    # always return http if the input is http

  elif url[:8] == "https://":
    http_url = "http://" + url[8:]
    if http_url in tweetedurls:  # urls is https, but http in dict, so return http
      return http_url
    else:
      return url  # we only return https unchanged if we haven't also seen http

  else:
    return url    # not http, not https, good luck with that. 



# resolve (follow redirects) and remove tracking information following ?, also trailing /, and canonicalize https vs. http
def clean_url(url):
  url = urlresolver.resolve_url(url, resolved_cache_only)

  junk = ["?utm_", "?_r=", "?source=", "?i=", "?s=", "?cache", "?xg_source", "&feature=youtu.be"]
  for j in junk:
    if url.find(j) != -1:
      url = url[:url.find(j)]
      break
  if url[-1:] == '/':
    url = url[:-1]

  url = canonicalize_https(url)
  return url


# add a single URL to the global tweetedurls map, given a line of json
def process_url(line):
  t = json.loads(line)
  user = t['user']['screen_name']

  for u in t['entities']['urls']:
    url = clean_url(u['expanded_url'])
    tu = tweetedurls.get(url, TweetedURL())
    tu.users.add(user) 
    tu.count += 1
    tweetedurls[url] = tu



# ---- main ----

# first count all URLs, generate list of users for each
# run async, because we need to resolve urls and we want to have multiple HTTP requests pending, for massive speedup

with ThreadPoolExecutor(max_workers=max_pending_resolutions+1) as executor:   # +1 for main thread (this thread)
  for x in executor.map(process_url, fileinput.input()):
    numtweets +=1 

  
print("Found " + str(len(tweetedurls)) + " distinct URLs in " +  str(numtweets) + " tweets.")

if resolved_cache_only == False:
  urlresolver.save_resolved_urls()


# take the top N urls, by number of tweets, and retrieve titles
def mycmp(url):
  return tweetedurls[url].count

topurls = sorted(tweetedurls, key=mycmp, reverse=True)[:numTopURLs]
for u in topurls:
  tweetedurls[u].title = urltitle.get_url_title(u)
  if verbose:
    print(str(tweetedurls[u].count) + "\t" + tweetedurls[u].title)

urltitle.save_url_titles()

# now generate graph between all URLs
#   edge weight is number of users who tweeted both
url_graph = {}
for url1 in topurls:
  for url2 in topurls:
    if url1<url2: # count each pair only once
      weight = len(tweetedurls[url1].users & tweetedurls[url2].users)
      if weight > 0:
        url_graph[(url1,url2)] = weight
        #print("Users " + str(tweetedurls[url1].users & tweetedurls[url2].users) + " all tweeted " + url1 + " and " + url2)


print("Found " + str(len(url_graph)) + " instances where a top URL tweeted by a pair of users.")

 # Write out GML 
 #   node weight is total tweets for url
f = codecs.open("urlgraph.gml", "w", "utf-8")
f.write("graph\n[\n")

for u in topurls:
  tweetcount = tweetedurls[u].count
  nodesize = math.sqrt(tweetcount)  # take sqrt to help with dynamic range
  title = tweetedurls[u].title.replace('"', "'")  # double qoutes to single, for Gephi's sake
  f.write("  node\n  [\n    id " + u + "\n    label \"" + title + "\"\n    size " + str(nodesize) + "\n    count " + str(tweetcount) + "\n  ]\n")

for (a,b) in url_graph:
  f.write("  edge\n  [\n    source " + a + "\n    target " + b + "\n    weight " + str(url_graph[(a,b)]) + "\n  ]\n")

f.write("]\n")
f.close()
