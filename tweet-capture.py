import datetime
import os
import time
import tweetstream
import json
import argparse

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

# --- Main ---
parser = argparse.ArgumentParser(description='Capture tweets containing keywords')
parser.add_argument('-u', '--username', required=True, help='Twitter username')
parser.add_argument('-p', '--password', required=True, help='Twitter password')
group = parser.add_mutually_exclusive_group(required=True)
group.add_argument('-f', '--termfile', help='file with terms to capture, one per line')
group.add_argument('-t', '--terms',    help='terms to capture')
args = parser.parse_args()

if args.termfile:
  words = [line.strip() for line in open(args.termfile)]
else
  words = [term.strip() for word in args.terms.split(',')]  

stream = tweetstream.FilterStream(args.username, args.password, track=words)

while True:
  logstart,f = logFile()
  try:
    for tweet in stream:
      f.write(json.dumps(tweet)+"\n")
      if newDay(logstart):
        f.close()
        break
  except tweetstream.ConnectionError, e:
    f = open('tweet-capture-error.log', 'a')
    tm = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    f.write(tm + " -- " + e.reason +  "\n")
    f.close
    time.sleep(15) # chill for a moment, don't reconnect ceaselessly


    


