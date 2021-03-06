#!/usr/bin/python

from IPython.Shell import IPShellEmbed

import stackexchange
import shelve
import pygtk
pygtk.require('2.0')
import pynotify
import datetime
import os

HOMEDIR="/home/pfarmer"
APPDIR="%s/.so-notify/" % HOMEDIR
USERID=66020

if not os.path.exists(APPDIR):
    os.mkdir(APPDIR)

data = shelve.open("%s/data.shelf" % APPDIR)

site = stackexchange.Site(
    "api.stackoverflow.com",
    app_key="TXgPj5rLtE2Ky-9nCuUVRQ"
)

tags = [ "git", "python", "bash" ]

the_questions = {}
creation_date = []
notify_tags = []

for tag in tags:
    questions = site.questions(tagged=tag, sort="creation", pagesize=5)
    key = "last_id_%s" % (tag)
    last_id = 0
    for q in questions:
        the_questions[q.id] = (q.title, q, tag)
        creation_date.append((q.json["creation_date"], q.id))
        if q.id > last_id:
            last_id = q.id


    if data.has_key(key):
        if last_id > data[key]:
            notify_tags.append(tag)
            data[key] = last_id
    else:
        notify_tags.append(tag)
        data[key] = last_id

user = site.user(USERID)
rep = user.reputation

user_key = "%i-rep" % USERID
notify_rep = 0

if data.has_key(user_key):
    if rep > data[user_key]:
        notify_rep = rep
        data[user_key] = rep
else:
    notify_rep = rep
    data[user_key] = rep

data.close()

output = open("/home/pfarmer/.conky/stackoverflow.txt", "w")

output.write("%s %s\n" % (
    str("Tag").ljust(6),
    str("Title").ljust(67)
))

output.write("%s %s\n" % (
    str("-").ljust(6, "-"),
    str("-").ljust(67, "-")
))

for q in sorted(creation_date, key=lambda date:(-date[0])):
    tag = the_questions[q[1]][2]
    title = the_questions[q[1]][0]
    title = title.encode('utf-8')
    title = title.decode('ascii','ignore')
    if len(title) > 67:
        title = str(title[:63]).ljust(67, ".")
    output.write("%s %s\n" % (tag.ljust(6), title))

dt = datetime.datetime.now()
now = dt.strftime("Last updated: %X")
output.write("\n%s - %s\n" % (now, site.rate_limit))

if len(notify_tags):
    pynotify.init("SO-Notify")
    message = "New questions in:\n"
    for tag in notify_tags:
        message = message + "\t%s\n" % tag

    if notify_rep > 0:
        message = message + "\nRep: %i\n" % notify_rep
    # message = message + "\n%s\n" % str(site.rate_limit)

    n = pynotify.Notification("StackOverflow", message)
    n.set_timeout(10000)
    n.show()
elif notify_rep > 0:
    message = "Rep: %i" % notify_rep

    n = pynotify.Notification("StackOverflow", message)
    n.set_timeout(10000)
    n.show()

# IPShellEmbed([])()
