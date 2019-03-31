#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# bug-report: feilengcui008@gmail.com

""" api for docker registry """

import json
import base64
import urllib.request


class HarborException(Exception):
    """ harbor api related exception """
    pass


class HarborApi(object):
    """ harbor api """
    def __init__(self, username, password, registry_endpoint):
        self.username = username
        self.password = password
        b_string = base64.encodebytes(("%s:%s" % (str(username), str(password))).encode())
        self.basic_token = b_string.decode()[0:-1]
        self.registry_endpoint = registry_endpoint.rstrip('/')

    def getTagMap(self, repository):
        """ get tag list for repository """

        url = "%s/api/repositories/%s/tags" % (self.registry_endpoint, repository)
        req = urllib.request.Request(url)
        req.add_header('Authorization', r'Basic %s' % (self.basic_token,))
        try:
            response = urllib.request.urlopen(req)
            return json.loads(response.read())
        except Exception as e:
            return None