# URL resolver - dereferences URL through redirects to determine final actual URL 
import csv
import urllib2
import time
from urlparse import urlparse

# internal state
resolved_urls = {}
failed_urls = set()
pending_resolutions = set()

opener = urllib2.build_opener() 
opener.addheaders = [('User-agent', 'Mozilla/5.0')] # try to reduce HTTP Error 403: Bad Behavior by mimicking WebKit

def load_resolved_urls(filename="resolved-urls.csv"):
    try:
        reader = csv.reader(open(filename, 'rb'))
        for row in reader:
            resolved_urls[row[0]] = row[1]
        print("Loaded " + str(len(resolved_urls)) + " resolved urls.")
    except IOError:
        print("No resolved URL file found")


def save_resolved_urls(filename="resolved-urls.csv"):
    f = open(filename, 'w')
    writer = csv.writer(f)
    for key, value in resolved_urls.items():
        writer.writerow([key, value])
    f.close()
    print("Saved " + str(len(resolved_urls)) + " resolved urls.")

def resolve_url_core(url, domain, cached_only=False):
    try:
        res = opener.open(url, None, 15)  # timeout after 15s -- designed to be threaded
        finalurl = res.geturl()
        resolved_urls[url] = finalurl
        res.close()
        print("Resolved " + url + " to " + finalurl)
        return finalurl
    except Exception as e:
        print("Failed to resolve URL " +  url + ", error: " + str(e))
        failed_urls.add(url)
        return url  # failed, oops


# --- Main --- 
def resolve_url(url, cached_only=False):
    
    # First see if we can shortcut
    domain = urlparse(url).netloc
    if len(domain) > 9:             # not a shortened URL; longest found is nbcnews.to, thebea.st, kazi.info
        return url    
    elif url in resolved_urls:
        return resolved_urls[url]   # hit cache
    elif cached_only:   
        return url                  # cache disabled
    elif url in failed_urls:
        return url                  # tried already, bad

    # We really have to resolve this by going across the network
    # if anyone else is trying to resolve on a particular domain, let them finish first. 
    # Prevents multiple pending requests for same domain (e.g. bit.ly), which can lead to denial of service
    # Also prevents multiple pending requests for same URL; subsequent calls will hit cache
    while domain in pending_resolutions:
        time.sleep(1)

    # we waited for domain to be free -- did we just resolve this URL?
    if url in resolved_urls:
        return resolved_urls[url]   
    elif url in failed_urls:
        return url

    pending_resolutions.add(domain)
    try:
        return resolve_url_core(url,domain,cached_only)
    finally:
        pending_resolutions.remove(domain)



