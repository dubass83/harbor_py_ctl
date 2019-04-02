#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# bug-report: feilengcui008@gmail.com

""" api for docker registry """

import urllib.request
import urllib.parse
import json
import base64


class RegistryException(Exception):
    """ registry api related exception """
    pass


class RegistryApi(object):
    """ interact with docker registry and harbor """
    def __init__(self, username, password, registry_endpoint):
        self.username = username
        self.password = password
        b_string = base64.encodebytes((
            "%s:%s" % (str(username), str(password))
            ).encode())
        self.basic_token = b_string.decode()[0:-1]
        self.registry_endpoint = registry_endpoint.rstrip('/')
        auth = self.pingRegistry(
            "https://%s/v2/_catalog" % (self.registry_endpoint,)
            )
        if auth is None:
            raise RegistryException("get token realm and service failed")
        self.token_endpoint = auth[0]
        self.service = auth[1]

    def pingRegistry(self, registry_endpoint):
        """ ping v2 registry and get realm and service """
        headers = dict()
        try:
            res = urllib.request.urlopen(registry_endpoint)
        except urllib.request.HTTPError as e:
            headers = dict(e.hdrs)
            # print(headers['Www-Authenticate'])
        try:
            (realm, service, _) = headers['Www-Authenticate'].split(',')
            return (realm[14:-1:], service[9:-1])
        except Exception as e:
            return None

    def getBearerTokenForScope(self, scope):
        """ get bearer token from harbor """
        payload = urllib.parse.urlencode(
            {'service': self.service, 'scope': scope}
            )
        url = "%s?%s" % (self.token_endpoint, payload)
        req = urllib.request.Request(url)
        req.add_header('Authorization', 'Basic %s' % (self.basic_token,))
        try:
            response = urllib.request.urlopen(req)
            return json.loads(response.read())["token"]
        except Exception as e:
            return None

    def getRepositoryList(self, n=None):
        """ get repository list """
        scope = "registry:catalog:*"
        bear_token = self.getBearerTokenForScope(scope)
        if bear_token is None:
            return None
        url = "https://%s/v2/_catalog" % (self.registry_endpoint,)
        if n is not None:
            url = "https://%s?n=%s" % (url, str(n))
        req = urllib.request.Request(url)
        req.add_header('Authorization', r'Bearer %s' % (bear_token,))
        try:
            response = urllib.request.urlopen(req)
            return json.loads(response.read())
        except Exception as e:
            return None

    def getTagList(self, repository):
        """ get tag list for repository """
        scope = "repository:%s:pull" % (repository,)
        bear_token = self.getBearerTokenForScope(scope)
        if bear_token is None:
            return None
        url = "https://%s/v2/%s/tags/list" % (
            self.registry_endpoint, repository
            )
        req = urllib.request.Request(url)
        req.add_header('Authorization', r'Bearer %s' % (bear_token,))
        try:
            response = urllib.request.urlopen(req)
            return json.loads(response.read())
        except Exception as e:
            return None

    def getManifest(self, repository, reference="latest", v1=False):
        """ get manifest for tag or digest """
        scope = "repository:%s:pull" % (repository,)
        bear_token = self.getBearerTokenForScope(scope)
        if bear_token is None:
            return None
        url = "https://%s/v2/%s/manifests/%s" % (
            self.registry_endpoint, repository, reference
            )
        req = urllib.request.Request(url)
        req.get_method = lambda: 'GET'
        req.add_header('Authorization', r'Bearer %s' % (bear_token,))
        req.add_header('Accept', 'application/vnd.docker.distribution.manifest.v2+json')
        if v1:
            req.add_header('Accept', 'application/vnd.docker.distribution.manifest.v1+json')
        try:
            response = urllib.request.urlopen(req)
            return json.loads(response.read())
        except Exception as e:
            return None

    def existManifest(self, repository, reference, v1=False):
        """ check to see it manifest exist """
        scope = "repository:%s:pull" % (repository,)
        bear_token = self.getBearerTokenForScope(scope)
        if bear_token is None:
            raise RegistryException("manifestExist failed due to token error")
        url = "https://%s/v2/%s/manifests/%s" % (
            self.registry_endpoint, repository, reference
            )
        req = urllib.request.Request(url)
        req.get_method = lambda: 'HEAD'
        req.add_header('Authorization', r'Bearer %s' % (bear_token,))
        req.add_header('Accept', 'application/vnd.docker.distribution.manifest.v2+json')
        if v1:
            req.add_header('Accept', 'application/vnd.docker.distribution.manifest.v1+json')
        try:
            response = urllib.request.urlopen(req)
            return (True, response.headers.dict["docker-content-digest"])
        except Exception as e:
            return (False, None)

    def deleteManifest(self, repository, reference):
        """ delete manifest by tag """
        (is_exist, digest) = self.existManifest(repository, reference)
        if not is_exist:
            raise RegistryException("manifest not exist")
        scope = "repository:%s:pull,push" % (repository,)
        bear_token = self.getBearerTokenForScope(scope)
        if bear_token is None:
            raise RegistryException("delete manifest failed due to token error")
        url = "https://%s/v2/%s/manifests/%s" % (
            self.registry_endpoint, repository, digest
            )
        req = urllib.request.Request(url)
        req.get_method = lambda: 'DELETE'
        req.add_header('Authorization', r'Bearer %s' % (bear_token,))
        try:
            urllib.request.urlopen(req)
        except Exception as e:
            return False
        return True

    def getManifestWithConf(self, repository, reference="latest"):
        """ get manifest for tag or digest """
        manifest = self.getManifest(repository, reference)
        if manifest is None:
            raise RegistryException("manifest for %s %s not exist" % (repository, reference))
        config_digest = manifest["config"]["digest"]
        scope = "repository:%s:pull" % (repository,)
        bear_token = self.getBearerTokenForScope(scope)
        if bear_token is None:
            return None
        url = "https://%s/v2/%s/blobs/%s" % (self.registry_endpoint, repository, config_digest)
        req = urllib.request.Request(url)
        req.get_method = lambda: 'GET'
        req.add_header('Authorization', r'Bearer %s' % (bear_token,))
        req.add_header('Accept', 'application/vnd.docker.distribution.manifest.v2+json')
        try:
            response = urllib.request.urlopen(req)
            manifest["configContent"] = json.loads(response.read())
            return manifest
        except Exception as e:
            return None
