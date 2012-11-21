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

    def make_list_html(self, admin):
        
        rs = self.get_data()
        rs.order("-name")

        ans = AnswerMails()

        objects = []
        i = 0
        color = "#FFFFFF"

        #admin = self.is_admin()
        
        for obj in rs:
            i += 1
            cnt = ans.count_by_event(str(obj.key()))
            objects.append({
                "name": obj.name,
                "display": self.display_name(obj.name.encode('utf-8')),
                "message": obj.message,
                "ans_num": cnt,
                "send_num": obj.send_num,
                "color": color
            })
            if color == "#FFFFFF":
                color = "#EEEEEE"
            else:
                color = "#FFFFFF"
            
        exists = False
        if i > 0:
            exists = True
            
        values = {
            "admin": admin,
            "objects": objects,
            "exists": exists
        }
        html = self.render("event_list.html", values).encode('utf-8')
        
        return html

    def make_detail_html(self, name):

        usr = Users()
        ans = AnswerMails()

        user_name = self.user_name()
        
        rs = self.get_data()
        rs.filter('name =', name)
        key = ""
        msg = ""
        for obj in rs:
            key = str(obj.key())
            msg = obj.message.encode('utf-8')

        data = ans.get_data_by_event(key)
        d = datetime.datetime.today() + datetime.timedelta(hours=9)
        
        html =""

        html += "<h1>%s</h1>" % self.display_name(name.encode('utf-8'))
        html += "<p>%s</p>" % msg

        html_ans = ""
        html_not = ""

        html += "<table class='list' style='margin: 20px;'>"
        html += "<tr><th>返信日時</th><th>名前</th></tr>"
        
        for s in data:
            user_data = usr.get_data_by_key(s["user"])
            if user_data["user_id"] == user_name:
                if s["date"] == None:
                    ans.update(
                        key, s["user"],
                        datetime.datetime(d.year,d.month,d.day,d.hour,d.minute,d.second)
                    )
                    s["date"] = d.strftime("%Y-%m-%d %H:%M:%S")
            if s["date"] == None:
                html_not += "<tr><td><!-- %s --></td><td>%s</td></tr>" % (s["date"], user_data["name"])
            else:
                html_ans += "<tr><td>%s</td><td>%s</td></tr>" % (s["date"], user_data["name"])
            #html += "<div style='margin:10px;'>[%s] %s</div>" % (s["date"], user_data["name"])

        html += html_not + html_ans

        html += "</table>"
        
        return html
    
    def inc(self, name, mail):
        return ""

    def display_name(self, name):
        return "%s年%s月%s日 %s時%s分" % (
            name[0:4],
            name[4:6],
            name[6:8],
            name[8:10],
            name[10:]
        )
    
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
            html += self.make_list_html(self.is_admin())
        
        return html

    def make_post_contents(self):
        
        if self.is_admin():
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

class EventsDelete(Events):
    def make_get_contents(self):
        
        if self.is_admin():
            ans = AnswerMails()
            name = self.request.get("name")
            
            rs = self.get_data()
            rs.filter('name =', str(name))
            
            key = ""
            for obj in rs:
                key = str(obj.key())
                ans.delete(key)
                obj.delete()
                break
            
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
        rs.order('-received')
        users = []
        for obj in rs:
            users.append({
                'user':obj.user_key,
                'date':obj.received
            })
        return users
    
    def delete(self, event):
        rs = self.get_data()
        rs.filter('event_key =', event)
        flg = False
    	for obj in rs:
    		obj.delete()
    		flg = True
    		
    	return flg
    	
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

