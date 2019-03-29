#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# bug-report: feilengcui008@gmail.com

""" api for docker registry """

import urllib2
# import urllib
import json
import base64


class HarborException(Exception):
    """ harbor api related exception """
    pass


class HarborApi(object):
    """ harbor api """
    def __init__(self, username, password, registry_endpoint):
        self.username = username
        self.password = password
        self.basic_token = base64.encodestring("%s:%s" % (str(username), str(password)))[0:-1]
        self.registry_endpoint = registry_endpoint.rstrip('/')

    def getTagMap(self, repository):
        """ get tag list for repository """
        # scope = "repository:%s:pull" % (repository,)
        # bear_token = self.getBearerTokenForScope(scope)
        # if bear_token is None:
            # return None
        url = "%s/api/repositories/%s/tags" % (self.registry_endpoint, repository)
        req = urllib2.Request(url)
        req.add_header('Authorization', r'Basic %s' % (self.basic_token,))
        try:
            response = urllib2.urlopen(req)
            return json.loads(response.read())
        except Exception as e:
            return None