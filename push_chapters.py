#! /usr/bin/env python
import base64
import json
import urllib
import urllib2
import os
import glob
import getpass
from optparse import OptionParser
from urlparse import urlunparse, urlparse


class PutRequest(urllib2.Request):
  def get_method(self):
    return "PUT"


class HeadRequest(urllib2.Request):
  def get_method(self):
    return "HEAD"


def build(doc):
  """
  Build up the dictionaries that will be made into json docs from markdown
  files. Lines beginning with %%% are assumed to be metadata containing json
  which will be parsed and included in the dictionary.
  """
  f = open(doc)
  md = f.readlines()
  meta = {}
  for m in filter(lambda x: x.startswith('%%%'), md):
    try:
      meta.update(json.loads(m.strip('% ')))
    except:
      print "Could not parse metadata, invalid json?: %s" % m
  content = "".join(filter(lambda x: not x.startswith('%%%'), md))
  jdoc = {'_id': doc.strip('.md'), 'content': content}
<<<<<<< HEAD
  if meta:
    jdoc['meta'] = meta
=======
  jdoc.update(meta)
>>>>>>> 419df19... Allow for metadata in markdown documents
  f.close()
  return jdoc


def crawl(chapter):
  """
  Chapter is a path to a directory. Find all markdown files in that directory,
  build json doc and return a list of json docs to be pushed elsewhere
  """
  if os.path.isdir(chapter):
    return map(build, glob.iglob('%s/*.md' % chapter))
  else:
    chapter = '%s.md' % chapter
    chapter = chapter.replace('.md.md', '.md')
    return [build(chapter)]


def push(docs, database):
  """
  Push a list of docs to the database
  """

  parts = urlparse(database)
  if parts.port:
    netloc = '%s:%s' % (parts.hostname, parts.port)
  else:
    netloc = parts.hostname

  url_tuple = (
      parts.scheme,
      netloc,
      parts.path,
      parts.params,
      parts.query,
      parts.fragment
      )
  url = urlunparse(url_tuple)

  try:
    urllib2.urlopen(PutRequest(url))
  except:
    # The data base probably already exists
    pass

  def get_rev(doc):
    """
    Get the _rev for a doc if it has one, and add to the doc
    """
    docid = doc['_id']
    # HEAD the doc
    docurl = "%s/%s" % (url, urllib.quote_plus(docid))
    try:
      head = urllib2.urlopen(HeadRequest(docurl))
      # get its _rev, append _rev to the doc dict
      doc['_rev'] = head.info().dict['etag'].strip('"')
    except urllib2.HTTPError, e:
      if e.code != 404:
        print 'Error getting rev for %s' % urllib.quote_plus(docid)

    return doc

  docs = map(get_rev, docs)

  auth = False

  if parts.username and parts.password:
    auth_tuple = (parts.username, parts.password)
    auth = base64.encodestring('%s:%s' % auth_tuple).strip()
  elif parts.username:
    auth_tuple = (parts.username, getpass.getpass())
    auth = base64.encodestring('%s:%s' % auth_tuple).strip()

  req = urllib2.Request('%s/_bulk_docs' % url)
  req.add_header("Content-Type", "application/json")

  if auth:
    req.add_header("Authorization", "Basic %s" % auth)

  data = {'docs': docs}
  req.add_data(json.dumps(data))
  f = urllib2.urlopen(req)
  f.read()


def options():
  parser = OptionParser()
  parser.add_option("-u", "--url", default="http://localhost:5984/docs",
      help="Url of the database - don't put password in it")

  opts, args = parser.parse_args()
  return opts, args


if __name__ == '__main__':
  opts, args = options()
  docs = [item for sublist in map(crawl, args) for item in sublist]


  push(docs, opts.url)
