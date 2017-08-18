import xml.etree.ElementTree as ET
import http.client
import json
import base64
import time
import os
from urllib.parse import urlencode
from html.parser import HTMLParser


import firebase_admin
import firebase_admin.db
from firebase_admin import credentials

# Firebase data
FIREBASE_KEY_DATA = json.loads(base64.b64decode(os.environ['FIREBASE_KEY']))
FIREBASE_URL="https://case-calendar-4b522.firebaseio.com"
TNT_USERNAME = os.environ['TNT_USERNAME']
TNT_PASSWORD = os.environ['TNT_PASSWORD']

class MyParser(HTMLParser):
    def __init__(self, dictobj):
        HTMLParser.__init__(self)
        self.form_opened = False
        self.dictobj = dictobj

    def handle_starttag(self, tag, attrs):
        if tag.lower() == 'input' and self.form_opened:
            D = dict(attrs)
            if 'name' in D:
                self.dictobj[D['name']] = D.get('value', '')
        elif tag.lower() == 'form':
            self.form_opened = True
            print(dict(attrs))

    def handle_endtag(self, tag):
        if tag.lower() == 'form':
            self.form_opened = True

def login(conn):
    conn = http.client.HTTPConnection('www.smartrax.com.sg')
    r = conn.request('GET', '/LoginSG.aspx')
    r = conn.getresponse()

    html = r.read()

    dictobj = dict()
    MyParser(dictobj).feed(html.decode('utf-8'))
    dictobj

    dictobj['txtUserId'] = TNT_USERNAME
    dictobj['txtPwd'] = TNT_PASSWORD

    body = urlencode(dictobj)
    conn.request('POST', '/LoginSG.aspx', body=body,
                 headers={
                    'Content-Length': len(body),
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'User-Agent': 'WhatEver/1.0'
                          })
    resp = conn.getresponse()

    h = dict([(k.lower(), v) for k, v in resp.getheaders()])
    r = resp.read()

    print(h)

    c = h['set-cookie'].split(';')[0]
    req_headers={
        'Cookie': c
    }

    return req_headers

req_headers = None

def try_headers(conn):
    """
    This function first yields the saved headers,
    then it yields a header obtained after login.

    So while the cookie is valid, it programs should only yield once.
    If it's invalid, programs will continue and it will yield a second
    time by logging in.
    """
    global req_headers
    if req_headers != None:
        yield req_headers
    req_headers = login(conn)
    yield req_headers

def get_data():
    conn = http.client.HTTPConnection('www.smartrax.com.sg', timeout=10)
    for h in try_headers(conn):
        try:
            conn.request('GET', '/GetSnapShotData.aspx?DataType=SnapShots', headers=h)
            resp = conn.getresponse()

            if resp.status != 200: # try to log in
                print(resp.read())
                continue
        except httplib.ResponseNotReady:
            print("Response not ready?")
            continue

        r = resp.read()

        def parse_child(e):
            rv = dict()
            for f in e.getchildren():
                rv[f.tag.lower()] = f.text
            return rv

        tree = ET.fromstring(r)
        data = [parse_child(e) for e in tree.getchildren()]

        return data

def put_data(d):
    firebase_admin.db.reference('/locations/ambulance-medical-service').set({e['registrationno']: e for e in d})

def keep_polling():
    from datetime import datetime

    while True:
        try:
            d = get_data()
            if d is not None:
                print ('Fetched location on %s' % datetime.now())
                put_data(d)
        finally:
            time.sleep(5)

if __name__ == '__main__
    cred = credentials.Certificate(
        FIREBASE_KEY_DATA
    )
    firebase_admin.initialize_app(
        credential=cred,
        options={
            'databaseURL': FIREBASE_URL,
        }
    )

    keep_polling()
