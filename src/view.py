#!/usr/bin/env python
# -*- coding: utf-8 -*-
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

import os
import datetime
from xml.sax.saxutils import *
from google.appengine.ext import db
from google.appengine.ext.webapp import template

import webapp2

admin_name = "root"
app_title = u"安否確認"
app_id = "confsafe"
mail_subject = u"安否確認メール"
mail_body = u"""
安否確認のため、そのまま返信して下さい。
https://%s.appspot.com/
""" % app_id

class UserData(db.Model):

    user_id = db.StringProperty()
    passwd = db.StringProperty()
    name = db.StringProperty()
    phone = db.StringProperty()
    mail1 = db.StringProperty()
    mail2 = db.StringProperty()

class View(webapp2.RequestHandler):

    def __init__(self, *arg):
        webapp2.RequestHandler.__init__(self, *arg)
        self.title = app_title

    def get_data(self):
        return self.DB.all()

    def make_select_form(self, name, values, default):
        html = u"<select name='%s'>" % name
        for value in values:
            if value == default:
                option = u"selected"
            else:
                option = u""
            html += "<option value='%s' %s>%s</option>" % (value, option, value)
        html += "</select>"
        return html
        
    def render(self, filename, values):
        
        path = os.path.join(os.path.dirname(__file__), "tpl/%s" % filename)
        html = template.render(path, values)

        return html
        
    def menu(self):

        html = self.render('menu.html', {})
        
        if self.user_name() == admin_name:
            html += self.render('menu_admin.html', {})
        else:
            html += self.render('menu_user.html', {})

        return html

    def get(self):
        if self.is_login():
            values = {
                "title": self.title,
                'menu': self.menu(),
                'contents': self.make_get_contents()
            }
            html = self.render('main_page.html', values)
            self.response.out.write(html)
        else:
            values = {
                "title": self.title
            }
            html = self.render('login_page.html', values)
            self.response.out.write(html)
            
    def post(self):
        if self.is_login():
            self.make_post_contents()
        else:
            values = {
                "title": self.title
            }
            html = self.render('login_page.html', values)
            self.response.out.write(html)
            
    def get_cookie(self,name):

        return self.request.cookies.get(name,'')

    def set_cookie(self, name, value):

        self.response.headers.add_header(
            'Set-Cookie',
            '%s=%s; epires=Fri, 31-Dec-1975 23:59:59 GMT; path=/' % (name, value)
        )

    def reset_cookie(self, name):

        self.response.headers.add_header(
            'Set-Cookie',
            '%s=; epires=Fri, 31-Dec-1975 23:59:59 GMT; path=/' % name
        )

    def is_login(self):

        user_id = str(self.get_cookie('user').encode('utf-8'))
        usr = Users()
        return usr.is_user(user_id)
        
    def is_admin(self):
        
        flg = False
        if str(self.get_cookie('user').encode('utf-8')) == admin_name:
            flg = True
        return flg
        
    def user_name(self):
        return self.get_cookie('user').encode('utf-8')
    
class Users(View):

    def __init__(self, *arg):
        View.__init__(self, *arg)
        self.admin = admin_name
        self.DB = UserData
    
    def login(self, user_id, passwd):
        
        flg = False
        rs = self.get_data()
        for obj in rs:
            if obj.user_id == user_id and obj.passwd == passwd:
                flg = True
        if user_id == self.admin:
            flg = True
        
        return flg

    def is_user(self, user_id):

        flg = False
        rs = self.get_data()
        for obj in rs:
            if obj.user_id == user_id:
                flg = True
        if user_id == self.admin:
            flg = True
        
        return flg
        
    def count(self):
        return self.get_data().count()
    
    def make_list_html(self):
        
        rs = self.DB.all().order("user_id")
        objects = []
        i = 0
        
        for obj in rs:
            i += 1
            objects.append({
                "key": obj.key(),
                "user_id": obj.user_id,
                "passwd": obj.passwd,
                "name": obj.name,
                "mail1": obj.mail1,
                "mail2": obj.mail2
            })
            
        if i > 0:
            exists = True
        else:
            exists = False
            
        values = {
            "objects": objects,
            "exists": exists
        }

        html = self.render("user_list.html", values)
        
        return html

    def get_new(self):
        obj = UserData(
            user_id = u"",
            passwd = u"",
            name = u"",
            phone = u"",
            mail1 = u"",
            mail2 = u""
        )
        return obj
        
    def make_get_contents(self):

        if self.request.get("key") == u"":
            obj = self.get_new()
            key = ""
        else:
            obj = UserData.get(self.request.get("key"))
            key = str(obj.key())

        value = {
            'key': key,
            'user_id': obj.user_id,
            'passwd': obj.passwd,
            'name': obj.name,
            'phone': obj.phone,
            'mail1': obj.mail1,
            'mail2': obj.mail2
        }
        
        html = ""
        if self.is_admin():
            html += self.render('user_edit_form.html', value).encode('utf-8')
            html += self.make_list_html().encode('utf-8')
            html += "<p style='padding: 10px 0px;'><a href='/user'>追加</a></p>"
        
        return html

    def make_post_contents(self):

        if self.request.get("key") == u"":
            obj = self.get_new()
        else:
            obj = UserData.get(self.request.get("key"))
        
        obj.user_id = self.request.get("user_id")
        obj.passwd = self.request.get("passwd")
        obj.name = self.request.get("name")
        obj.phone = self.request.get("phone")
        obj.mail1 = self.request.get("mail1")
        obj.mail2 = self.request.get("mail2")
        obj.put()

        self.redirect('/user')
    
    def make_mail_addresses(self):

        rs = self.get_data()
        addr = u""

        for obj in rs:
            if obj.mail1 != u"":
                if addr != u"":
                    addr += u", "
                addr += obj.mail1
            if obj.mail2 != u"":
                if addr != u"":
                    addr += u", "
                addr += obj.mail2

        return addr.encode('utf-8')

    def count_active(self):

        rs = self.get_data()
        cnt = 0

        for obj in rs:
            if obj.mail1 != u"":
                cnt += 1
            elif obj.mail2 != u"":
                cnt += 1

        return cnt

    def get_array(self, answered):
        rs = self.get_data()
        users = []
        for obj in rs:
            ans = ""
            for x in answered:
                if str(obj.key()) == x['user']:
                    ans = x['date'].strftime("%Y-%m-%d %H:%M:%S")
            users.append({
                "name": obj.name.encode('utf-8'),
                "ans": ans
            })
        return users
    
    def get_active_keys(self):
        rs = self.get_data()
        users = []
        for obj in rs:
            flg = False
            if obj.mail1 != u"":
                flg = True
            elif obj.mail2 != u"":
                flg = True
            if flg:
                users.append(str(obj.key()))
        return users
    
    def get_name_by_key(self, key):
        
        rs = self.get_data()
        #rs.filter('__key__ =', key)
        name = ""
        for obj in rs:
            if str(obj.key()) == key:
                name = obj.name.encode('utf-8')

        return name
        
    def get_key_by_mail(self, mail):

        rs = self.get_data()
        key = ""
        for obj in rs:
            if mail == obj.mail1:
                key = str(obj.key())
                break
            elif mail == obj.mail2:
                key = str(obj.key())
                break

        return key

