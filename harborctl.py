#!/usr/bin/env python3
# -*- coding:utf-8 -*-
# bug-report: makssych@gmail.com

"""Simple cli tool to work with harbor api.

cli tool
which work with harbor api and make some admin task.
Firs of all it's made for cleaning from old and useless
tags in my private registry
"""
import logging
import logging.handlers
import os
import argparse
import sys
import json
from registry import RegistryApi
from harbor import HarborApi


logger = logging.getLogger(os.path.splitext(os.path.basename(sys.argv[0]))[0])


class ApiProxy(object):
    """ user RegistryApi """
    def __init__(self, registry, args):
        self.registry = registry
        self.args = args
        self.callbacks = dict()
        self.register_callback("repo", "list", self.list_repo)
        self.register_callback("tag", "list", self.list_tag)
        self.register_callback("tag", "delete", self.delete_tag)
        self.register_callback("manifest", "list", self.list_manifest)
        self.register_callback("manifest", "delete", self.delete_manifest)
        self.register_callback("manifest", "get", self.get_manifest)

    def register_callback(self, target, action, func):
        """ register real actions """
        if not target in self.callbacks.keys():
            self.callbacks[target] = {action: func}
            return
        self.callbacks[target][action] = func

    def execute(self, target, action):
        """ execute """
        print(json.dumps(self.callbacks[target][action](), indent=4, sort_keys=True))

    def list_repo(self):
        """ list repo """
        return self.registry.getRepositoryList(self.args['num'])

    def list_tag(self):
        """ list tag """
        return self.registry.getTagList(self.args['repo'])

    def delete_tag(self):
        """ delete tag """
        (_, ref) = self.registry.existManifest(self.args['repo'], self.args['tag'])
        if ref is not None:
            return self.registry.deleteManifest(self.args['repo'], ref)
        return False

    def list_manifest(self):
        """ list manifest """
        tags = self.registry.getTagList(self.args['repo'])["tags"]
        manifests = list()
        if tags is None:
            return None
        for i in tags:
            content = self.registry.getManifestWithConf(self.args['repo'], i)
            manifests.append({i: content})
        return manifests

    def delete_manifest(self):
        """ delete manifest """
        return self.registry.deleteManifest(self.args['repo'], self.args['ref'])

    def get_manifest(self):
        """ get manifest """
        return self.registry.getManifestWithConf(self.args['repo'], self.args['tag'])


class ApiProxy2(object):
    """ user RegistryApi """
    def __init__(self, registry, args):
        self.registry = registry
        self.args = args
        self.callbacks = dict()
        self.register_callback("tag", "clean", self.tag_clean)

    def register_callback(self, target, action, func):
        """ register real actions """
        if not target in self.callbacks.keys():
            self.callbacks[target] = {action: func}
            return
        self.callbacks[target][action] = func

    def execute(self, target, action):
        """ execute """
        print(json.dumps(self.callbacks[target][action](), indent=4, sort_keys=True))

    def tag_clean(self):
        """ tag clean"""
        return self.registry.retentionPolicy(self.args['repo'], self.args['count'])


class CustomFormatter(argparse.RawDescriptionHelpFormatter,
                      argparse.ArgumentDefaultsHelpFormatter):
    pass


# since just a script tool, we do not construct whole target->action->args 
# structure with oo abstractions which has more flexibility, just register 
# parser directly
def get_parser():
    """ return a parser """
    parser = argparse.ArgumentParser("harborctl.py", 
        description=sys.modules[__name__].__doc__, 
        formatter_class=CustomFormatter)

    parser.add_argument('--username', action='store', required=True, help='username')
    parser.add_argument('--password', action='store', required=True, help='password')
    parser.add_argument('--registry_endpoint', action='store', required=True,
            help='registry endpoint')

    subparsers = parser.add_subparsers(dest='target', help='target to operate on')

    # repo target
    repo_target_parser = subparsers.add_parser('repo', help='target repository')
    repo_target_subparsers = repo_target_parser.add_subparsers(dest='action',
            help='repository subcommand')
    repo_cmd_parser = repo_target_subparsers.add_parser('list', help='list repositories')
    repo_cmd_parser.add_argument('--num', action='store', required=False, default=None,
            help='the number of data to return')

    # tag target
    tag_target_parser = subparsers.add_parser('tag', help='target tag')
    tag_target_subparsers = tag_target_parser.add_subparsers(dest='action',
            help='tag subcommand')
    tag_list_parser = tag_target_subparsers.add_parser('list', help='list tags')
    tag_list_parser.add_argument('--repo', action='store', required=True, help='list tags')
    tag_delete_parser = tag_target_subparsers.add_parser('delete', help='delete tag')
    tag_delete_parser.add_argument('--repo', action='store', required=True, help='delete tags')
    tag_delete_parser.add_argument('--tag', action='store', required=True, help='tag reference')
    tag_dict_parser = tag_target_subparsers.add_parser('dict', help='dict tag')
    tag_dict_parser.add_argument('--repo', action='store', required=True, help='dict tag')


    # manifest target
    manifest_target_parser = subparsers.add_parser('manifest', help='target manifest')
    manifest_target_subparsers = manifest_target_parser.add_subparsers(dest='action',
            help='manifest subcommand')
    manifest_list_parser = manifest_target_subparsers.add_parser('list', help='list manifests')
    manifest_list_parser.add_argument('--repo', action='store', required=True, 
            help='list manifests')
    manifest_delete_parser = manifest_target_subparsers.add_parser('delete', help='delete manifest')
    manifest_delete_parser.add_argument('--repo', action='store', required=True,
            help='delete manifest')
    manifest_delete_parser.add_argument('--ref', action='store', required=True,
            help='manifest reference')
    manifest_get_parser = manifest_target_subparsers.add_parser('get', help='get manifest content')
    manifest_get_parser.add_argument('--repo', action='store', required=True, help='delete tags')
    manifest_get_parser.add_argument('--tag', action='store', required=True,
            help='manifest reference')

    g = parser.add_mutually_exclusive_group()
    g.add_argument("--debug", "-d", action="store_true",
                   default=False,
                   help="enable debugging")
    g.add_argument("--silent", "-s", action="store_true",
                   default=False,
                   help="don't log to console")

    return parser


def setup_logging(options):
    """Configure logging."""
    root = logging.getLogger("")
    root.setLevel(logging.WARNING)
    logger.setLevel(options["debug"] and logging.DEBUG or logging.INFO)
    if not options["silent"]:
        ch = logging.StreamHandler()
        ch.setFormatter(logging.Formatter(
            "%(levelname)s[%(name)s] %(message)s"))
        root.addHandler(ch)


def main():
    """ main entrance """

    # try read config from file
    try:
        with open('config/config.json') as json_data_file:
            options = json.load(json_data_file)
    except FileNotFoundError:
        print("No such file or directory: 'config/config.json'")
        print("Try get options from comand line")
        parser = get_parser()
        options = parser.parse_args(sys.argv[1:])
        options = vars(options)
    print(options)
    setup_logging(options)

    try:
        logger.debug("Start {} for {} in {}".format(options["action"],
                                                    options["target"],
                                                    options["registry_endpoint"]))

        registry = RegistryApi(options["username"], options["password"],
                                options["registry_endpoint"])
        harbor = HarborApi(options["username"], options["password"],
                            options["registry_endpoint"])

        if 'from_file' in options:
            proxy2 = ApiProxy2(harbor, options)
            proxy2.execute(options['target'], options['action'])
            return 'Done!'

        proxy = ApiProxy(registry, options)
        proxy.execute(options['target'], options['action'])
    except Exception as e:
        logger.exception("%s", e)
        sys.exit(1)
    sys.exit(0)

if __name__ == '__main__':
    main()
