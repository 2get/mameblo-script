#!/usr/bin/env python
# -*- coding: utf-8 -*-

import cookielib
import json
import os
import re
import urllib
import urllib2
from codecs import open


class Opener(object):
    def __init__(self):
        self.COOKIE_FILE = os.path.join(
            os.path.dirname(__file__), 'cookie.dat')
        self.cj = self.getCookieJar()
        self.opener = urllib2.build_opener(
            urllib2.HTTPCookieProcessor(self.cj))

    def hasCookie(self):
        return os.access(self.COOKIE_FILE, os.F_OK)

    def getCookieJar(self):
        cj = cookielib.LWPCookieJar(self.COOKIE_FILE)

        if self.hasCookie():
            cj.load(self.COOKIE_FILE, ignore_discard=True)

        return cj

    def saveCookieJar(self):
        self.cj.save(self.COOKIE_FILE, ignore_discard=True)

    def get(self, url):
        response = self.opener.open(url)
        self.saveCookieJar()
        return response

    def post(self, url, query):
        params = urllib.urlencode(query)
        response = self.opener.open(url, params)
        self.saveCookieJar()
        return response


class Mameblo(object):
    def __init__(self, name, password):
        self.opener = Opener()
        self.re_authenticity_token = re.compile('name="authenticity_token".+?value="(.+?)"')

        if not self.isLogin():
            self.login(name, password)

    def getToken(self, url):
        response = self.opener.get(url)
        content = unicode(response.read(), 'utf-8', 'ignore')
        m = self.re_authenticity_token.search(content)
        if m:
            return m.group(1)

    def isLogin(self):
        url = 'http://www.mameblo.com'
        response = self.opener.get(url)
        if response.code == 200:
            body = unicode(response.read(), 'utf-8', 'ignore')
            if '/signin' in body:
                return False
            else:
                return True
        return False

    def login(self, name, password):
        url = 'http://www.mameblo.com/signin'
        authenticity_token = self.getToken(url)
        query = {
            'authenticity_token': authenticity_token,
            'session[name]': name,
            'session[password]': password
        }
        response = self.opener.post('http://www.mameblo.com/sessions', query)
        body = unicode(response.read(), 'utf-8', 'ignore')
        if 'error' in body:
            print 'Login failed'
            quit()
        else:
            print 'Login success'
        return response

    def post(self, title, content):
        url = 'http://www.mameblo.com'
        authenticity_token = self.getToken(url)
        query = {
            'authenticity_token': authenticity_token,
            'entry[title]': title.encode('utf-8'),
            'entry[content]': content.encode('utf-8')
        }
        return self.opener.post('http://www.mameblo.com/entries', query)

def main():
    import sys

    name = ''  # mameblo account name
    password = ''  # mameblo account password

    mame = Mameblo(name, password)

    argv = sys.argv
    argc = len(argv)

    if argc != 3:
        print 'Usage: # python %s title content' % argv[0]
        quit()

    title = unicode(argv[1], 'utf-8')
    content = unicode(argv[2], 'utf-8')

    mame.post(title, content)

if __name__ == '__main__':
    main()
