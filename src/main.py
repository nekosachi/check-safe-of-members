#!/usr/bin/env python
# -*- coding: utf-8 -*-

import webapp2

login = False

from view import *
from conf import *
from handle_incoming_email import *

class MainHandler(View):

    def __init__(self, *arg):
        View.__init__(self, *arg)

    def menu(self):

        html = View.menu(self)
        return html
        
    def make_get_contents(self):

        evt = Events()
        
        html = ""
        if self.is_admin():
            html = evt.make_edit_form()
        html += evt.make_list_html()

        return html

    def post(self):

        user_id = self.request.get("user_id").encode('utf-8')
        passwd = self.request.get("passwd").encode('utf-8')
        
        usr = Users()
        login = usr.login(user_id, passwd)
        
        if user_id == "":
            self.reset_cookie('user')
        elif login:
            self.set_cookie('user', user_id)
        
        self.redirect('/')
        
app = webapp2.WSGIApplication([('/', MainHandler),
                               LogSenderHandler.mapping(),
                               ('/events', Events),
                               ('/delete', EventsDelete),
                               ('/user', Users)],
                              debug=True)
