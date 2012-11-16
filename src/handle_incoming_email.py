#!/usr/bin/env python
# -*- coding: utf-8 -*-
#

import logging, email
from google.appengine.ext import webapp
from google.appengine.ext.webapp.mail_handlers import InboundMailHandler
from google.appengine.ext.webapp.util import run_wsgi_app

from cStringIO import StringIO
from email.generator import Generator

import datetime
from view import *
from conf import *

class LogSenderHandler(InboundMailHandler):
    def receive(self, mail_message):
        
        logging.info("==========")
        #logging.info("original : " + mail_message.original)
        logging.info("Received a message from: " + mail_message.sender)
        
        fp = StringIO()
        g = Generator(fp, mangle_from_=False, maxheaderlen=60)
        g.flatten(mail_message.original)
        text = fp.getvalue()
        #logging.info(text)
        
        msg = text.split('**msg**')
        if len(msg) > 0:
            logging.info(msg[1])
        #for s in mail_message.original.values():
        #    logging.info(s)
        #logging.info("Body: " + str(mail_message.bodies('text/plain')))
        #plaintext_bodies = mail_message.bodies('text/plain')
        
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
