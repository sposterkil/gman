#!/usr/bin/env python
import argparse
import atexit
import os
import cPickle as pickle
import subprocess

parser = argparse.ArgumentParser(
    description="Manage multiple git repositories by tags.")
parser.add_argument(
    "-t", "--tag", help="Add the specified tag to the specified directory(s), defaulting to the current directory.", nargs='*')
parser.add_argument(
    "-l", "--list", help="Show a list of all tags and their repositories.", action='store_true')
parser.add_argument(
    "command", help="usage: TAG COMMAND\nRuns the specified git command on all repositories tagged with TAG.", nargs='*')
args = parser.parse_args()


if os.path.isfile(os.path.expanduser("~/.gman")):
    tags = pickle.load(open(os.path.expanduser("~/.gman"), "rb"))
else:
    tags = {}


def tag_path(tag, path):
    if tag in tags:
        if path not in tags[tag]:
            tags[tag] += [path]
    else:
        tags[tag] = [path]


def list_tags():
    for tag in tags:
        print "%s:" % tag
        for path in tags[tag]:
            print "\t%s" % path


def run_cmd(tag, command):
    for path in tags[tag]:
        print "For %s:" % path
        subprocess.Popen(["git"] + command, cwd=path)


def exit_cleanup():
    pickle.dump(tags, open(os.path.expanduser("~/.gman"), "wb"))
atexit.register(exit_cleanup)


if args.tag:
    if len(args.tag) == 1:
        tag_path(args.tag[0], os.path.normpath(os.getcwd()))
    else:
        for path in args.tag[1:]:
            tag_path(args.tag[0], os.path.abspath(path))
if args.list:
    list_tags()

if args.command:
    working_tag = args.command[0]
    working_command = args.command[1:]
    if working_tag in tags:
        run_cmd(working_tag, working_command)
