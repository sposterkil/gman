#!/usr/bin/env python
import argparse
import atexit
import os
import cPickle as pickle
import subprocess

parser = argparse.ArgumentParser(
    description="Manage multiple git repositories by tags.")
parser.add_argument(
    "-t", "--tag", help="add the specified tag to the specified directory(s), defaulting to the current directory.", nargs='*')
parser.add_argument("-r", "--untag", "--remove",
                    help="remove specified tags from specified directory(s), defaulting to the current directory", nargs='*')
parser.add_argument(
    "-l", "--list", help="show a list of all tags and their repositories.", action='store_true')
parser.add_argument(
    "working_tag", help="specifies the tag to operate on", metavar="TAG", nargs="?")
parser.add_argument(
    "COMMAND", help="runs this command on all repositories tagged with tag", nargs=argparse.REMAINDER)
args = parser.parse_args()


if os.path.isfile(os.path.expanduser("~/.gman")):
    tags = pickle.load(open(os.path.expanduser("~/.gman"), "rb"))
else:
    tags = {}


def tag_path(tag, path):
    print "Adding tag %s to %s" % (tag, path)
    if tag in tags:
        if path not in tags[tag]:
            tags[tag] += [path]
    else:
        tags[tag] = [path]


def untag_path(remove_tag, path):
    if remove_tag == None:
        for tag in tags:
            if path in tag:
                del tag[path]
    else:
        if path in tags[remove_tag]:
            del tags[remove_tag][tags[remove_tag].index(path)]


def list_tags():
    for tag in tags:
        print "%s:" % tag
        for path in tags[tag]:
            print "\t%s" % path


def run_cmd(tag, command):
    for path in tags[tag]:
        print "For %s:" % path
        subprocess.Popen(["git"] + command, cwd=path).wait()


def exit_cleanup():
    to_delete = []
    for tag in tags:
        if len(tags[tag]) < 1:
            to_delete.append(tag)
    for tag in to_delete:
        del tags[tag]
    pickle.dump(tags, open(os.path.expanduser("~/.gman"), "wb"))
atexit.register(exit_cleanup)


if args.tag:
    if len(args.tag) == 1:
        tag_path(args.tag[0], os.path.normpath(os.getcwd()))
    else:
        for path in args.tag[1:]:
            tag_path(args.tag[0], os.path.abspath(path))

if args.untag:
    if args.untag[0] not in tags:
        print """"%s" isn't a tag you're using.""" % args.untag[0]
    if len(args.untag) == 1:
        untag_path(args.untag[0], os.path.normpath(os.getcwd()))
    else:
        for path in args.untag[1:]:
            untag_path(args.untag[0], os.path.abspath(path))

if args.list:
    list_tags()

if args.working_tag:
    if args.COMMAND:
        if args.working_tag in tags:
            run_cmd(args.working_tag, args.COMMAND)
        else:
            print """"%s" isn't a tag you're using.""" % args.working_tag
    else:
        print "Please supply a command to run."
