#!/usr/bin/env python
# -*- coding: utf-8 -*-

import datetime
from google.appengine.ext import db
from google.appengine.api import mail

from view import *

class Event(db.Model):
    name = db.StringProperty()
    message = db.StringProperty()
    send_num = db.IntegerProperty()
    recieved_num = db.IntegerProperty()

class AnswerMail(db.Model):
    event_key = db.StringProperty()
    user_key = db.StringProperty()
    received = db.DateTimeProperty()

class Events(View):

    def __init__(self, *arg):
        View.__init__(self, *arg)
        self.table = "Event"
        self.DB = Event

    def make_edit_form(self):

        d = datetime.datetime.today() + datetime.timedelta(hours=9)
        
        values = {
            'name': d.strftime("%Y%m%d%H%M"),
            'message': ""
        }
        
        html = self.render('event_edit_form.html', values).encode('utf-8')
        return html

    def make_list_html(self):
        
        rs = self.get_data()
        rs.order("-name")

        html = ""
        ans = AnswerMails()
        
        for obj in rs:
            cnt = ans.count_by_event(str(obj.key()))
            html += "<div style='padding: 10px;'><a href='/events?name=%s'>%s</a> : %s [%s / %s]</div>" % (obj.name.encode('utf-8'), obj.name.encode('utf-8'), obj.message.encode('utf-8'), str(cnt), str(obj.send_num))
        return html

    def make_detail_html(self, name):

        usr = Users()
        ans = AnswerMails()
        
        rs = self.get_data()
        rs.filter('name =', name)
        key = ""
        msg = ""
        for obj in rs:
            key = str(obj.key())
            msg = obj.message.encode('utf-8')

        data = ans.get_data_by_event(key)

        html = "<h1>%s</h1>" % name.encode('utf-8')
        html += "<p>%s</p>" % msg
        
        for s in data:
            html += "<div style='margin:10px;'>[%s] %s</div>" % (s["date"], usr.get_name_by_key(s["user"]))

        return html
    
    def inc(self, name, mail):
        return ""
        
    def get_key_by_name(self, name):
        rs = self.get_data()
        rs.filter('name =', str(name))
        key = ""
        for obj in rs:
            key = str(obj.key())
            break
        return key
        
    def make_get_contents(self):
        name = self.request.get("name")
        if name != u"":
            html = self.make_detail_html(name)
        else:
            html = self.make_edit_form()
            html += self.make_list_html()
        
        return html

    def make_post_contents(self):

        usr = Users()
        ans = AnswerMails()
        
        d = datetime.datetime.today() + datetime.timedelta(hours=9)
        
        cnt = usr.count_active()

        evt_name = d.strftime("%Y%m%d%H%M")

        obj = self.DB(
            name = evt_name,
            message = self.request.get("message"),
            send_num = cnt,
            recieved_num = 0
        )

        obj.put()
        
        evt_key = str(obj.key())
        users = usr.get_active_keys()
        ans.add(evt_key, users)
        
        sender_addr = "%s@%s.appspotmail.com" % (evt_name, app_id)
        to_addr = usr.make_mail_addresses()
        message = mail.EmailMessage(sender=sender_addr,
                                    subject=mail_subject)
        message.bcc = to_addr
        message.body = u"""
%s
%s
""" % (self.request.get("message"), mail_body)
        
        message.send()
        
        self.redirect('/')

class AnswerMails(View):

    def __init__(self, *arg):
        View.__init__(self, *arg)
        self.table = "AnswerMail"
        self.DB = AnswerMail

    def count_by_event(self, event_key):
        rs = self.get_data()
        rs.filter('event_key =', event_key)
        cnt = 0
        for obj in rs:
            if obj.received != None:
                cnt += 1

        #return rs.count()
        return cnt
        
    def get_data_by_event(self, event_key):
        rs = self.get_data()
        rs.filter('event_key =', event_key)
        users = []
        for obj in rs:
            users.append({
                'user':obj.user_key,
                'date':obj.received
            })
        return users
    
    def add(self, event, users):
        flg = False
        for u in users:
            obj = self.DB(
                event_key = event,
                user_key = u,
                received = None
            )
            obj.put()
            flg = True
            
        return flg

    def update(self, event, user, date):
        rs = self.get_data()
        rs.filter('event_key =', event)
        rs.filter('user_key =', user)

        flg = False
        
        for obj in rs:
            if obj.received == None:
                obj.received = date
                obj.put()
                flg = True
            
        return flg

class LogSenderHandlerTest:
    def receive(self):
        
        user = "guest@test.ne.jp"
        event = "201211121509@sample.com".split('@')
        received = datetime.datetime.now()

        evt = Events()
        event_key = evt.get_key_by_name(event[0])

        usr = Users()
        user_key = usr.get_key_by_mail(user)

        if event_key != "" and user_key != "":
            ans = AnswerMails()
            ans.add(event_key, user_key, received)


        
            
    
