#!/usr/bin/env python

from time import sleep
import HTMLParser
import datetime
import icalendar
import json
import parsedatetime as pdt
import re
import urllib2

ptc = pdt.Constants('en_GB', usePyICU=False)
cal = pdt.Calendar(ptc)

LOCATION_RE = re.compile('@(.+)$')
DATE_RE = re.compile('\D?(\d+\D\d+\D\d+)[^\d ]?')

def parse_event_title(title):
    """
    Breaks up [date] title @ location into components
    """
    match = DATE_RE.search(title)
    date_tuple = cal.parseDate(match.group(1))
    event_date = datetime.date(date_tuple[0], date_tuple[1], date_tuple[2])
    event_title = title[len(match.group(0)):].strip()
    location = None
    match = LOCATION_RE.search(title)
    if match:
        location = match.group(1).strip()
    return (event_date, event_title, location)

def main():
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'London Social Club Calendar v0.1 by /u/dalore')]
    opened = False
    while not opened:
        try:
            data = opener.open('http://api.reddit.com/r/londonsocialclub/hot/?sort=new&limit=100')
            opened = True
        except:
            sleep(31)


    jsondata = json.load(data)
    try:
        links = jsondata['data']['children']
    except:
        return jsondata

    cal = icalendar.Calendar()
    cal.add('prodid', '-//London Social Club Calendar//reddit.com//')
    cal.add('version', '0.1')

    h = HTMLParser.HTMLParser()

    # now create an event for each link
    for link in links:
        try:
            linkdata = link['data']
            (event_date, event_title, event_location) = parse_event_title(linkdata['title'])
            event = icalendar.Event()
            event['uid'] = "%s@lsc" % linkdata['id']
            event.add('description', "%s\n\n%s" % (linkdata['url'],
                h.unescape(linkdata['selftext_html'])))
            if event_location:
                event.add('location', event_location)
            event.add('summary', event_title)
            event.add('dtstart', event_date)
            event.add('dtend', event_date + datetime.timedelta(1))
            event.add('organizer', linkdata['author'])
            event.add('url', linkdata['url'])
            cal.add_component(event)
        except:
            pass

    return cal.to_ical() # content_type="text/calendar")

try:
    import webapp2

    class MainPage(webapp2.RequestHandler):
        def get(self):
            self.response.headers['Content-Type'] = 'text/calendar'
            cal = main()
            self.response.out.write(cal)

    app = webapp2.WSGIApplication([('/', MainPage)])
except:
    pass

if __name__ == '__main__':
    print main()