#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# bug-report: makssych@gmail.com

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
        b_string = base64.encodebytes(
            ("%s:%s" % (str(username), str(password))).encode()
            )
        self.basic_token = b_string.decode()[0:-1]
        self.registry_endpoint = registry_endpoint.rstrip('/')
        self.registry_dict = {}

    def retentionPolicy(self, repolist, count):
        """ apply retention policy from file config.json to the repo """
        for i in repolist:
            self.registry_dict[i] = self.getTagMap(i)
        self.sortTagByDate(count)
        self.checkLabel()

        for repo, tags in self.registry_dict.items():
            for tag in tags:
                self.deleteTag(repo, tag)
        # self.printTagDate()

    def getTagMap(self, repository):
        """ get tag list for repository """

        url = "https://%s/api/repositories/%s/tags" % (
            self.registry_endpoint, repository
            )
        req = urllib.request.Request(url)
        req.add_header('Authorization', r'Basic %s' % (self.basic_token,))
        try:
            response = urllib.request.urlopen(req)
            return json.loads(response.read())
        except urllib.error.URLError as error:
            print("Error: " + error.read().decode('utf8'))

    def sortTagByDate(self, count):
        """ 
        sort tags in self.registry_dict by created date and remove 'count'
        of tags from delete task
        """
        for repo, value in self.registry_dict.items():
            # print("{} == > {}".format(repo, value))
            if value == []:
                continue
            self.registry_dict[repo] = sorted(
                value, key=lambda tag: tag['created']
                )[:-int(count)]

    def printTagDate(self):
        """ print self.registry_dict """
        for repo, value in self.registry_dict.items():
            print("################# {} ###############".format(repo))
            for i in value:
                print("deleted: {} tag: {}".format(i['created'], i['name']))

    def checkLabel(self):
        """ remove tag from delete task if it has a Label """
        for repo, value in self.registry_dict.items():
            self.registry_dict[repo] = [x for x in value if x['labels'] == []]
            # for tag in self.registry_dict[repo]:
            #     if tag['labels'] != []:
            #         print(tag)        

    def deleteTag(self, repository, tag):
        """ delete tag list for repository """

        url = "https://%s/api/repositories/%s/tags/%s" % (
            self.registry_endpoint, repository, tag['name']
            )
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Authorization': r'Basic %s' % (self.basic_token,)
        }
        req = urllib.request.Request(
            url,
            headers=headers,
            method='DELETE'
        )

        try:
            response = urllib.request.urlopen(req)
            print("Success: {:17}code: {}".format(
                tag['name'], response.getcode()
                ))
        except urllib.error.URLError as error:
            print("Error: " + error.read().decode('utf8'))