# Cache of URL titles 
# not meant to be used at volume, so not designed to be multi-threaded
import csv
import urllib2
import BeautifulSoup
import HTMLParser

# internal state
url_titles = {}

p = HTMLParser.HTMLParser()
opener = urllib2.build_opener() 
opener.addheaders = [('User-agent', 'Mozilla/5.0')] # try to reduce HTTP Error 403: Bad Behavior by mimicking WebKit

# interpret as UTF-8, unescape HTML characters, strip leading and trailing space
def clean_title(title):
    return p.unescape(title).lstrip().rstrip()

def load_url_titles(filename="url-titles.csv"):
    try:
        reader = csv.reader(open(filename, 'rb'))
        for row in reader:
            url_titles[row[0]] = unicode(row[1], 'utf-8')
        print("Loaded " + str(len(url_titles)) + " URL titles")
    except IOError:
        print("No URL title file found")


def save_url_titles(filename="url-titles.csv"):
    f = open(filename, 'wb')
    writer = csv.writer(f)
    for key, value in url_titles.items():
        writer.writerow([key, value.encode('utf-8')])
    f.close()
    print("Saved " + str(len(url_titles)) + " URL titles")

# Retrieve page title for URL. Expensive, slow.
def get_url_title_core(url):
    try:
        response = urllib2.urlopen(url, None, 15) # 15s timeout
        html = response.read()
        soup = BeautifulSoup.BeautifulSoup(html)
        title = clean_title(soup.title.string)
        if title != None and len(title)>0:
            return title
        else:
            return url
    except Exception as e:
        print("Failed to get URL title " +  url + ", error: " + str(e))
        return url  # failed, oops

# --- Main ---
def get_url_title(url):
    if url not in url_titles:
        url_titles[url] = get_url_title_core(url)
    return url_titles[url]
