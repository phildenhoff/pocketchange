import json
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
import http.client, urllib

import requests

POCKET_CONSUMER_KEY=""
POCKET_ACCESS_TOKEN=""

PUSHOVER_TOKEN=""
PUSHOVER_USER=""

RSS_FEEDS = [
    "https://boz.com/rss.xml",
    "https://cprss.s3.amazonaws.com/weekly.statuscode.com.xml",
    "https://ma.ttias.be/cronweekly/index.xml",
    "https://www.strongtowns.org/journal/?format=rss",
    "https://mxb.dev/feed.xml",
    "https://beepb00p.xyz/rss.xml",
    "https://longreads.com/feed/",
    "https://www.jamesshore.com/v2/feed",
    "https://vasilishynkarenka.com/rss/"
]
UNUSED = [
    # Got bored
    "http://sreweekly.com/feed/",
    "https://aeon.co/feed.rss",
    # Haven't listened or read anything since I added it
    "https://www.vicfoodguys.ca/feed/",
    # Either malformed or hates AWS
    "http://www.stilldrinking.org/rss/feed.xml",
]

# This is a comma-separated list of tags to apply in Pocket
TAGS="pocketchange"

# No, I don't WANT to store all the time zones here but I WILL if I have to.
ALL_TIMEZONES = ['ACDT', 'ACST', 'ACT', 'ACT', 'ACWST', 'ADT', 'AEDT', 'AEST', 'AFT', 'AKDT', 'AKST', 'ALMT', 'AMST', 'AMT', 'AMT', 'ANAT', 'AQTT', 'ART', 'AST', 'AST', 'AWST', 'AZOST', 'AZOT', 'AZT', 'BDT', 'BIOT', 'BIT', 'BOT', 'BRST', 'BRT', 'BST', 'BST', 'BST', 'BTT', 'CAT', 'CCT', 'CDT', 'CDT', 'CEST', 'CET', 'CHADT', 'CHAST', 'CHOT', 'CHOST', 'CHST', 'CHUT', 'CIST', 'CIT', 'CKT', 'CLST', 'CLT', 'COST', 'COT', 'CST', 'CST', 'CST', 'CT', 'CVT', 'CWST', 'CXT', 'DAVT', 'DDUT', 'DFT', 'EASST', 'EAST', 'EAT', 'ECT', 'ECT', 'EDT', 'EEST', 'EET', 'EGST', 'EGT', 'EIT', 'EST', 'FET', 'FJT', 'FKST', 'FKT', 'FNT', 'GALT', 'GAMT', 'GET', 'GFT', 'GILT', 'GIT', 'GMT', 'GST', 'GST', 'GYT', 'HDT', 'HAEC', 'HST', 'HKT', 'HMT', 'HOVST', 'HOVT', 'ICT', 'IDLW', 'IDT', 'IOT', 'IRDT', 'IRKT', 'IRST', 'IST', 'IST', 'IST', 'JST', 'KALT', 'KGT', 'KOST', 'KRAT', 'KST', 'LHST', 'LHST', 'LINT', 'MAGT', 'MART', 'MAWT', 'MDT', 'MET', 'MEST', 'MHT', 'MIST', 'MIT', 'MMT', 'MSK', 'MST', 'MST', 'MUT', 'MVT', 'MYT', 'NCT', 'NDT', 'NFT', 'NOVT', 'NPT', 'NST', 'NT', 'NUT', 'NZDT', 'NZST', 'OMST', 'ORAT', 'PDT', 'PET', 'PETT', 'PGT', 'PHOT', 'PHT', 'PKT', 'PMDT', 'PMST', 'PONT', 'PST', 'PST', 'PYST', 'PYT', 'RET', 'ROTT', 'SAKT', 'SAMT', 'SAST', 'SBT', 'SCT', 'SDT', 'SGT', 'SLST', 'SRET', 'SRT', 'SST', 'SST', 'SYOT', 'TAHT', 'THA', 'TFT', 'TJT', 'TKT', 'TLT', 'TMT', 'TRT', 'TOT', 'TVT', 'ULAST', 'ULAT', 'UTC', 'UT', 'UYST', 'UYT', 'UZT', 'VET', 'VLAT', 'VOLT', 'VOST', 'VUT', 'WAKT', 'WAST', 'WAT', 'WEST', 'WET', 'WIT', 'WST', 'YAKT', 'YEKT']

def notify(msg):
    conn = http.client.HTTPSConnection("api.pushover.net:443")
    conn.request("POST", "/1/messages.json",
    urllib.parse.urlencode({
        "token": PUSHOVER_TOKEN,
        "user": PUSHOVER_USER,
        "message": msg,
    }), { "Content-type": "application/x-www-form-urlencoded" })
    conn.getresponse()
    pass

def interpret_date(input_date):
    # check if a timezone name is in the string
    tz_name = None
    for tz in ALL_TIMEZONES:
        if tz in input_date:
            tz_name = tz

    if (tz_name):
        # Remove the " EST" at the end of the string
        input_date = input_date[:-len(tz_name) - 1]
        # Example: Wed, 16 Oct 2019 12:09:00
        publish_date = datetime.strptime(input_date, "%a, %d %b %Y %H:%M:%S").astimezone()

    else:
        # Example: Wed, 16 Oct 2019 12:09:00 +0000
        publish_date = datetime.strptime(input_date, "%a, %d %b %Y %H:%M:%S %z")

    return publish_date

def add_to_pocket(url, title=None):
    """Submits a request to add the URL to Pocket.

    Returns True if the response status is 200 OK.
    """
    data = {
        "consumer_key": POCKET_CONSUMER_KEY,
        "access_token": POCKET_ACCESS_TOKEN,
        "url": url,
        "tags": TAGS
    }
    if (title):
        data['title'] = title

    response = requests.post(
        "https://getpocket.com/v3/add",
        data = data,
        timeout=1
    )

    if (response.status_code == 200):
        return True

    notify("Failed to add article to Pocket: " + response.text)
    return False

def pull_from_feeds():
    for feed in RSS_FEEDS:
        # We should expect requests to resolve rather quickly.
        print("Pulling feed {} ".format(feed))
        try:
            response = requests.get(feed, timeout=0.5)
        except requests.exceptions.Timeout as e:
            print("Timeout pulling feed: {}".format(e))
            continue

        # check status
        if (response.status_code != 200):
            notify("Failed to fetch feed for {}:\n{}.".format(feed, response.text))
            continue

        # parse XML
        try:
            root = ET.fromstring(response.text)
        except Exception as e:
            print(f"Failed to parse XML for {feed}")
            print(e.msg)
            continue

        for item in root[0].findall('item'):
            title = item.find('title').text
            url = item.find('link').text

            raw_publish_date = item.find('pubDate').text
            publish_date = interpret_date(raw_publish_date)

            one_day_ago = datetime.now(timezone.utc) - timedelta(days=1)

            is_fresh = publish_date > one_day_ago

            if (not is_fresh):
                # We'll skip old articles
                continue

            print("\tAdding '{}' to Pocket".format(title))
            add_to_pocket(url, title)

pull_from_feeds()
