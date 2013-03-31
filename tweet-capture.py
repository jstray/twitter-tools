import datetime
import os
import time
import tweetstream
import json
import argparse

def curDateFilename(capturename, count):
  now = datetime.datetime.now()
  base = now.strftime(capturename + "-%Y-%m-%d")
  if count==0:
    return now, base + ".json"
  else:
    return now, base + "-part-" + str(count) + ".json"

def logFile(capturename):
  count = 0
  now,fname = curDateFilename(capturename, count)
  while os.path.exists(fname):
    count += 1
    now,fname = curDateFilename(capturename, count)
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
  capturename = os.path.basename(args.termfile).split('.')[0]  # filename without path and extension
else:
  words = [term.strip() for term in args.terms.split(',')]  
  capturename = "tweets"

print "Capturing " + str(len(words)) + " words to file " + capturename

stream = tweetstream.FilterStream(args.username, args.password, track=words)

while True:
  logstart,f = logFile(capturename)
  try:
    for tweet in stream:
      print tweet['text']
      f.write(json.dumps(tweet)+"\n")
      if newDay(logstart):
        f.close()
        break
  except tweetstream.ConnectionError, e:
    f = open(capturename + '-error.log', 'a')
    tm = strftime("%Y-%m-%d %H:%M:%S", gmtime())
    f.write(tm + " -- " + e.reason +  "\n")
    f.close
    time.sleep(15) # chill for a moment, don't reconnect ceaselessly


    


