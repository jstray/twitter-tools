import datetime
import os
import time
import tweetstream
import json

def curDateFilename(count):
  now = datetime.datetime.now()
  base = now.strftime("tweets-%Y-%m-%d")
  if count==0:
    return now, base + ".json"
  else:
    return now, base + "-part-" + str(count) + ".json"

def logFile():
  count = 0
  now,fname = curDateFilename(count)
  while os.path.exists(fname):
    count += 1
    now,fname = curDateFilename(count)
  return now, open(fname, "w")

def newDay(oldNow):
  now = datetime.datetime.now()
  return now.day != oldNow.day
      
words = ["gun violence","gun control","backround check","second amendment","2nd amendment","2nd amend","gun owner","gun owners","NRA","gun law","gun laws","run rights","gun crimes","firearm violence","gun makers","gun speech"]
stream = tweetstream.FilterStream("overviewproject", "srslywtf?", track=words)

while True:
  logstart,f = logFile()
  try:
    for tweet in stream:
      f.write(json.dumps(tweet)+"\n")
      if newDay(logstart):
        f.close()
        break
  except tweetstream.ConnectionError, e:
    print "Disconnected from twitter. Reason:", e.reason
    time.sleep(15)


    


