#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import logging, email
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app

import datetime
from view import *
from conf import *

class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        
        logging.info("Received a message from: " + mail_message.sender)

        wk = mail_message.sender
        if wk.find("<") < 0:
            user = wk
        else:
            x = wk.split("<")
            y = x[1].split(">")
            user = y[0]
        
        wk = mail_message.to.split('@')
        event = wk[0].replace('"','').replace('<','')
        logging.info("Event: " + event)
        
        evt = Events()
        event_key = evt.get_key_by_name(event)

        usr = Users()
        user_key = usr.get_key_by_mail(user)
        
        wk = str(mail_message.date).replace(" +0900","").replace(" (JST)","")
        logging.info("date: " + wk)
        received = datetime.datetime.strptime(wk,'%a, %d %b %Y %H:%M:%S')

        logging.info("Event: " + event_key)
        logging.info("User : " + user_key)
        
        if event_key != "" and user_key != "":
            ans = AnswerMails()
            ans.update(event_key, user_key, received)
            logging.info("Received!")
