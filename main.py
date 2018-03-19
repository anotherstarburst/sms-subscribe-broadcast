# Copyright 2016 Google Inc.
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
import os
import json
import webapp2
import logging
from google.appengine.ext.webapp import template
from google.appengine.ext import ndb, deferred
from google.appengine.api import users

from twilio.rest import Client

from env_variables import ACCOUNT_SID, AUTH_TOKEN, SERVICE_NUMBER


class RegisteredUsers(ndb.Model):
    name = ndb.StringProperty(default="")
    number = ndb.StringProperty(default="")
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)


class Messages(ndb.Model):
    user_key = ndb.KeyProperty()
    content = ndb.TextProperty(default="")
    direction = ndb.StringProperty(default="")  # outbound / inbound
    sid = ndb.StringProperty(default="")
    created_at = ndb.DateTimeProperty(auto_now_add=True)
    updated_at = ndb.DateTimeProperty(auto_now=True)


def render_template(template_name, values={}):
    path = os.path.join(os.path.dirname(__file__), 'templates/', template_name)
    template_values = {}
    response = template.render(path, values)
    return response

def ajax_respond(self):
    data_to_send = json.dumps(self.response_dict)
    data_wrapper = self.request.get('callback')
    if data_wrapper:  # for jquery requests
        data_to_send = data_wrapper + "(" + data_to_send + ")"
    return self.response.write(data_to_send)

def send_message(to_number, message, user_key):
    client = Client(ACCOUNT_SID, AUTH_TOKEN)
    resp = client.messages.create(
        to=to_number,
        from_=SERVICE_NUMBER,
        body=message)
    new_message = Messages()
    new_message.user_key = user_key
    new_message.content = message
    new_message.sid = resp.sid
    new_message.direction = "outbound"
    new_message.put()

class MainPage(webapp2.RequestHandler):
    def get(self):
        template = render_template(template_name="index.html")
        return self.response.out.write(template)

class InboundMessageHandler(webapp2.RequestHandler):
    def post(self):
        self.sid = self.request.get('MessageSid')
        self.number = self.request.get('From')
        self.body = self.request.get('Body')

        check = RegisteredUsers.query()
        check = check.filter(RegisteredUsers.number == self.number)
        if check.count():
            self.user_key = check.get().key
            return self._already_registered()

        return self._register()

    def _record_message(self):
        new_message = Messages()
        new_message.user = self.user_key
        new_message.content = self.body
        new_message.direction = "inbound"
        new_message.sid = self.sid
        new_message.put()

    def _already_registered(self):
        self._record_message()
        message = "Thank you for responding. This is just part of the presentation. \
        The live version will be pushed in a little while. <3 from Small Wins."
        deferred.defer(send_message, self.number, message, self.user_key)
        return self.response.write('Ok')

    def _register(self):
        new_user = RegisteredUsers()
        new_user.number = self.number
        name = str(self.body).strip().split(" ")[0]
        new_user.name = name
        self.user_key = new_user.put()
        self._record_message()

        message = "Thank you for registering for Small Wins %s! We'll be in touch soon." % name
        deferred.defer(send_message, self.number, message, self.user_key)

        return self.response.write('Ok')

class BroadcastMessageHandler(webapp2.RequestHandler):
    def get(self):
        users = RegisteredUsers.query()
        messages = [
            "Hi %s, thanks for signing up! Let's learn a little more about you.",
            "On a scale of 1-10 how much time do you spend engaging with the Barking and Dagenham community?",
            "Where 1 is never and 10 is every day.",
        ]
        values = {
            "users": users,
            "messages": messages
        }
        template = render_template(template_name="broadcast.html", values=values)
        return self.response.out.write(template)

    def post(self):
        message = self.request.get("message")
        users = RegisteredUsers.query()
        for user in users:
            to_number = user.number
            deferred.defer(send_message, to_number, message, user.key)

        self.response_dict = {
            "message": "Message sent! (%s)" % message
        }
        return ajax_respond(self)


app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/inbound', InboundMessageHandler),
    ('/broadcast', BroadcastMessageHandler),
], debug=True)
