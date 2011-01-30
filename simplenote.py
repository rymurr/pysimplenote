#!/usr/bin/env python

import base64
import datetime
import logging
import urllib
import urllib2

try:
    import json
except ImportError:
    try:
        import simplejson as json
    except ImportError:
        from django.utils import simplejson as json

class SimplenoteError(Exception):
    def __init__(self, method, msg):
        self.method = method
        self.msg = msg

    def __repr__(self):
        return "%s: [%s] %r" % (self.__class__.__name__, self.method, self.msg)

class SimplenoteAuthError(SimplenoteError):
    def __init__(self, email, msg):
        self.email = email
        self.method = "auth"
        self.msg = msg

class Simplenote(object):
    api_url = "https://simple-note.appspot.com/api/"
    api2_url = "https://simple-note.appspot.com/api2/"

    def __init__(self, email, password):
        self.email = email
        self.password = password
        self._get_token()

    def _get_token(self):
        if hasattr(self, '_token'):
            return self._token

        url = self.api_url + 'login'

        form_fields = {
            'email': self.email,
            'password': self.password
        }
        data = base64.b64encode(urllib.urlencode(form_fields))

        try:
            res = urllib2.urlopen(urllib2.Request(
                url = url,
                data = data,
                ))
        except urllib2.HTTPError, exc:
            raise SimplenoteAuthError(self.email, repr(exc))

        if res.getcode() != 200:
            raise SimplenoteAuthError(email, "Request failed with response %d" % res.getcode())

        self._token = res.read().strip()
        return self._token

    def _set_token(self, token):
        self._token = token

    token = property(_get_token, _set_token)

    def _query(self, action, isjson=True, post=None, **kwargs):
        kwargs['auth'] = self.token
        kwargs['email'] = self.email
        args = urllib.urlencode(kwargs)
        url = "%s%s?%s" % (self.api2_url, action, args)

        #headers = {'User-Agent': USER_AGENT}

        if post:
            #if isinstance(post, unicode):
            #    post = post.encode('utf-8')
            data = json.dumps(post,encoding="utf-8")
            req = urllib2.Request(url=url, data=data)
        else:
            req = urllib2.Request(url=url)

        try:
            res = urllib2.urlopen(req)
        except urllib2.HTTPError, exc:
            raise SimplenoteError(action, repr(exc))

        if res.getcode() != 200:
            raise SimplenoteError(action, "Request failed with response %d" % res.getcode())

        if isjson:
            return json.load(res)

        return res

    def _parse_datetime(self, val):
        return datetime.datetime.strptime(val.split('.', 1)[0], "%Y-%m-%d %H:%M:%S")

    def index(self):
        notes = self._query("index")
        notes = notes['data']
        return notes

#    def search(self, query, max_results=10, offset=0):
#        results = self._query("search", query=query, results=max_results, offset=offset)
#        return dict(
#            total_records = results['Response']['totalRecords'],
#            results = results['Response']['Results'],
#        )

    def get_content(self):
        index = self.index()
        notes={}
        titles={}
        for i in index:
            note=self.get_note(i['key'])
            notes[note['key']] = note
            titles[note['key']] = note['content'][0:note['content'].find('\n')]
        return titles,notes

    def get_note(self, key):
        res = self._query("data/"+key)
        #res['title'] = res['content'][0:res['content'].find('\n')]
        return res

    def update_note(self, key, jdata):
        res = self._query("data/"+key, post=jdata)
        return res

    def create_note(self, jdata):
        res = self._query("data", post=jdata)
        return res

    def delete_note(self, key, jdata):
        jdata['deleted']=True
        self.update_note(key,jdata)
        return True

