import fileinput
import json
import urlresolver
#import interactiongraph

urlresolver.load_resolved_urls()

# we build the graph with only the top N URLs, in terms of tweets/retweets 
numTopURLs = 100

# maps URL to number of times tweeted, and list of users who have tweeted/retweeted
class TweetedURL:
  def __init__(self):
    self.users = set()
    self.count = 0


tweetedurls = {}
numtweets = 0

# resolve (follow redirects) and remove tracking information following ?, also trailing /
def clean_url(url):
  url = urlresolver.resolve_url(url)
  junk = ["?utm_", "?_r=", "?source=", "?i=", "?s=", "?cache", "?xg_source", "?feature=", "&feature=youtu.be"]
  for j in junk:
    if url.find(j) != -1:
      url = url[:url.find(j)]
      break
  if url[-1:] == '/':
    url = url[:-1]
  return url


# measure of similarity of two urls, according to how close in the social network they've been tweeted
#def url_social_similarity(url1, url2):


# first count all URLs, generate list of users for each
for line in fileinput.input():
  t = json.loads(line)
  user = t['user']['screen_name']

  for u in t['entities']['urls']:
    url = clean_url(u['expanded_url'])
    tu = tweetedurls.get(url, TweetedURL())
    tu.users.add(user) 
    tu.count += 1
    tweetedurls[url] = tu

  numtweets+=1

print("Found " + str(len(tweetedurls)) + " distinct URLs in " +  str(numtweets) + " tweets.")

# take the top N urls, by tweets
def mycmp(url):
  return tweetedurls[url].count

topurls = sorted(tweetedurls, key=mycmp, reverse=True)[:numTopURLs]
for u in topurls:
  print(str(tweetedurls[u].count) + "\t" + u)

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
f = open("urlgraph.gml", "w")
f.write("graph\n[\n")

for u in topurls:
  f.write("  node\n  [\n    id " + u + "\n    label \"" + u + "\"\n    weight " + str(tweetedurls[u].count) + "\n  ]\n")

for (a,b) in url_graph:
  f.write("  edge\n  [\n    source " + a + "\n    target " + b + "\n    weight " + str(url_graph[(a,b)]) + "\n  ]\n")

f.write("]\n")


urlresolver.save_resolved_urls()
