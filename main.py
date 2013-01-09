#!/usr/bin/env python

'''
Created on Jan 8, 2013

@author: matt
'''

import json
import urllib2
import icalendar
import re
import datetime
import HTMLParser
import webapp2

TITLE_RE = re.compile('\[(\S+)\] (.+) \@ (.+)')

def parse_event_title(title):
    """
    Breaks up [date] title @ location into components
    """
    match = TITLE_RE.search(title)
    if match:
        title_date = match.group(1)
        title_title = match.group(2)
        title_loc = match.group(3)
        title_date = datetime.datetime.strptime(title_date, '%d/%m/%y').date()
        return (title_date, title_title, title_loc)
    

def main():
    opener = urllib2.build_opener()
    opener.addheaders = [('User-agent', 'London Social Club Calendar v0.1 by /u/dalore')]
    data = opener.open('http://api.reddit.com/r/londonsocialclub/new/?sort=new')

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

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/calendar'
        cal = main()
        self.response.out.write(cal)

app = webapp2.WSGIApplication([('/', MainPage)])

if __name__ == '__main__':
    main()