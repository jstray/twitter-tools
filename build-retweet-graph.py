import fileinput
import json

users = set()
edges = {}

for line in fileinput.input():
  t = json.loads(line)
  

  user = t['user']['screen_name']
  otheruser = None

  if 'retweeted_status' in t:
  	# retweeted 
    otheruser = t['retweeted_status']['user']['screen_name']
    action = "retweeted"

  elif t['in_reply_to_screen_name'] != None:
  	# replied to 
    otheruser = t['in_reply_to_screen_name']
    action = "replied to"

  elif len(t['entities']['user_mentions'])>0:
    # mentioned
    otheruser = t['entities']['user_mentions'][0]['screen_name']
    action = "mentioned"

  #if otheruser != None:
  #   print(user + " " + action + " " + otheruser) 
  if user != None and otheruser != None:
    users.add(user)
    users.add(otheruser)
    edges[(user,otheruser)] = edges.get((otheruser,user), 0) + 1


print("Found " + str(len(users)) + " users in " +  str(len(edges)) + " events.")
 # Write out GML now
f = open("tweetgraph.gml", "w")
f.write("graph\n[\n")

for n in users:
  f.write("  node\n  [\n    id " + n + "\n    label \"" + n + "\"\n  ]\n")

for (a,b) in edges:
  f.write("  edge\n  [\n    source " + a + "\n    target " + b + "\n    weight " + str(edges[(a,b)]) + "\n  ]\n")

f.write("]\n")
