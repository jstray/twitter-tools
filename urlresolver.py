# URL resolver - dereferences URL through redirects to determine final actual URL 
import csv
import urllib2

resolved_urls = {}

def load_resolved_urls(filename="resolved-urls.csv"):
    try:
        reader = csv.reader(open(filename, 'rb'))
        for row in reader:
            resolved_urls[row[0]] = row[1]
        print("Loaded " + str(len(resolved_urls)) + " resolved urls.")
    except IOError:
        print("No resolved URL file found")


def save_resolved_urls(filename="resolved-urls.csv"):
    writer = csv.writer(open(filename, 'wb'))
    for key, value in resolved_urls.items():
        writer.writerow([key, value])
    print("Saved " + str(len(resolved_urls)) + " resolved urls.")

def resolve_url(url):
    if url in resolved_urls:
        return resolved_urls[url]
    else:
        try:
            res = urllib2.urlopen(url, None, 5)  # timeout after 5s
            finalurl = res.geturl()
            resolved_urls[url] = finalurl
            res.close()
            print("Resolved " + url + " to " + finalurl)
            return finalurl
        except Exception as e:
            print("Failed to resolve URL " +  url + ", error: " + str(e))
            return url  # failed, oops



