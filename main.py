#!/usr/bin/env python
#
# Copyright 2007 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext import db
import twilio

# utility code for handling Twilio XML

def getData():
    return StabStatus.get_or_insert("main2")

def pleaseHold(r, limit):
    if (limit % 3 == 0):
        r.addPlay("http://stabbyphone.appspot.com/e_StabbingImportantToUs.wav")
    else:
        r.addPlay("http://stabbyphone.appspot.com/e_HoldLoop5Sec1.wav")
    r.addRedirect("http://stabbyphone.appspot.com/holdWhileStabbing?limit=" + str(limit))

# data model
    
class StabStatus(db.Model):
    lastCommand = db.IntegerProperty(required = True, default = 0)
    active = db.BooleanProperty(required = True, default = False)
    callerId = db.StringProperty(default = "")
    
# web request handlers
    
class MainHandler(webapp.RequestHandler):
    def get(self):
        self.response.out.write('<h1>Welcome to StabbyPhone!</h1>')

class SetLanguage(webapp.RequestHandler):
    def post(self):
        self.get()
    def get(self):
        self.response.headers["Content-Type"] = "text/xml"
        choice = int(self.request.get("Digits"))
        
        r = twilio.Response()
        if (choice == 1):
            r.addRedirect("http://stabbyphone.appspot.com/stab-menu.xml")
        elif (choice == 2):
            r.addSay("Mister Stabby doesn't speak Spanish!")
            r.addRedirect("http://stabbyphone.appspot.com/stab-menu.xml")
        else:
            r.addSay("That does not compute!")
            r.addRedirect("http://stabbyphone.appspot.com/intro-menu.xml")
        self.response.out.write(r)
            
class GetLastStabCommand(webapp.RequestHandler):
    def post(self):
        self.get()
    def get(self):
        d = getData()
        print >>self.response.out, "$" + d.callerId + "!" + str(d.lastCommand)
        d.lastCommand = 0
        d.put()
        
class StartStabbing(webapp.RequestHandler):
    def post(self):
        self.get()
    def get(self):
        d = getData()
        d.active = True
        d.put()
        print >>self.response.out, "start stabbing"
        
class EndStabbing(webapp.RequestHandler):
    def post(self):
        self.get()
    def get(self):
        d = getData()
        d.active = False
        d.put()
        print >>self.response.out, "end stabbing"
        
class GetStabStatus(webapp.RequestHandler):
    def post(self):
        self.get()
    def get(self):
        d = StabStatus.get_or_insert("main2")
        print >>self.response.out, d.active

class HoldWhileStabbing(webapp.RequestHandler):
    def post(self):
        self.get()
    def get(self):
        self.response.headers["Content-Type"] = "text/xml"
        d = getData()
        limit = int(self.request.get("limit"))

        r = twilio.Response()
        if (d.active and limit > 0):
            pleaseHold(r, limit - 1)
        else:
            r.addRedirect("http://stabbyphone.appspot.com/stab-complete.xml")
        self.response.out.write(r)
        
class SetStabCommand(webapp.RequestHandler):
    def post(self):
        self.get()
    def get(self):
        self.response.headers["Content-Type"] = "text/xml"
        choice = int(self.request.get("Digits"))
        caller = self.request.get("Caller")

        r = twilio.Response()
        if (choice == 5):
            r.addSay("Mister Stabby never sleeps!")
        elif (choice >= 1 and choice <= 4):
            d = getData()
            d.lastCommand = choice
            d.active = (d.lastCommand != 0)
            d.callerId = caller
            d.put()
            pleaseHold(r, 8)
        else:
            r.addSay("Mr. Stabby don't play that.")
        self.response.out.write(r)
        
class Reset(webapp.RequestHandler):
    def post(self):
        self.get()
    def get(self):
        d = getData()
        d.active = False
        d.lastCommand = 0
        d.callerId = ""
        d.put()
        print >>self.response.out, "reset"
        
def main():
    application = webapp.WSGIApplication([
            ('/', MainHandler),
            ('/reset', Reset),
            ('/setLanguage', SetLanguage),
            ('/startStabbing', StartStabbing),
            ('/endStabbing', EndStabbing),
            ('/holdWhileStabbing', HoldWhileStabbing),
            ('/getStabStatus', GetStabStatus),
            ('/getLastStabCommand', GetLastStabCommand),
            ('/setStabCommand', SetStabCommand)],
        debug=True)
    util.run_wsgi_app(application)


if __name__ == '__main__':
    main()
