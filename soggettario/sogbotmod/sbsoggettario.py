#!/usr/bin/python
# -*- coding: utf-8  -*-
#########################################################################
# Copyright (C) 2013 Cristian Consonni <cristian.consonni@gmail.com>.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program (see COPYING).
# If not, see <http://www.gnu.org/licenses/>.
#########################################################################

import tempfile
import urllib
import argparse
import lxml
from lxml.html import fromstring
import rdflib

from sogbotmod import sbdevel as devel

SKOSNS = rdflib.Namespace('http://www.w3.org/2004/02/skos/core#')
THSKOSBASEURL = "http://thes.bncf.firenze.sbn.it/SKOS.php?id=%d"
THTERMBASEURL = "http://thes.bncf.firenze.sbn.it/termine.php?id=%d"
DBPEDIAURL = "http://it.dbpedia.org"

QUERIES = {'broader': """SELECT DISTINCT ?a ?b
                         WHERE {
                                ?a skos:related ?b .
                               }""",
           'narrower':"""SELECT DISTINCT ?a ?b
                         WHERE {
                                ?a skos:related ?b .
                               }""",
           'related': """SELECT DISTINCT ?a ?b
                         WHERE {
                                ?a skos:related ?b .
                               }""",
           'used':    """SELECT DISTINCT ?a ?b
                         WHERE {
                                ?a skos:related ?b .
                               }"""
          }


class Error(Exception):
  """Base class for exceptions in this module."""
  pass

class Term(object):

  def __init__(self, graph, tid=None):
    self.tid = tid
    self.graph = graph
    self.name = None
    self._name()
    self.dblink = None
    self._dblink()

  def _name(self):
    qname = None
    pred=SKOSNS.prefLabel

    for s, p, o in self.graph:
      if p == pred:
        qname = o

    self.name = qname

  def _dblink(g,skos):
    link = None
    pred = SKOSNS.closeMatch

    for s, p, o in self.graph:
      if p == pred:
        if DBPEDIAURL in o:
          resurl="%s/resource/" %DBPEDIAURL
          link=o.replace(resurl,'')

    self.dblink = link

  def _register_plugin():
    if not self._registeredPlugin:
      plugin.register(
      'sparql', rdflib.query.Processor,
      'rdfextras.sparql.processor', 'Processor')

      plugin.register(
      'sparql', rdflib.query.Result,
      'rdfextras.sparql.query', 'SPARQLQueryResult')

      self._registeredPlugin=True

  def _skos_query(query):
    if not self._pluginRegistered:
      self._register_plugin()

    qres = self.graph.query(query,initNs=dict(SKOSNS))
    return qres

  def has_dblink():
    return self.dblink is None

  def get_wikilink(self,source):
    html = fromstring(source)
    links = html.xpath('//a/@href')
    wikilink=[l for l in links if "it.wikipedia.org" in l][0]

    wikilink=wikilink.replace(" ","_")
    return wikilink

  def used_items():
    qres = self._skos_query(QUERIES['used'])
    #for row in qres.result:

  def related_items():
    qres = self._skos_query(QUERIES['related'])
    #for row in qres.result:

  def narrower_items():
    qres = self._skos_query(QUERIES['narrower'])
    #for row in qres.result:

  def broader_items():
    qres = self._skos_query(QUERIES['broader'])
    #for row in qres.result:



class SkosGraph(rdflib.Graph):

  def __init__(self, tid):
    super(SkosGraph, self).__init__()
    self.tid = tid

    fsko = tempfile.NamedTemporaryFile()
    skosurl=THSKOSBASEURL %tid
    urllib.urlretrieve(skosurl, fsko.name)

    self.bind('skos', SKOSNS)
    self.parse(fsko.name)
    fsko.close()


# ----- main -----
if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument("tid", type=int, help="term id number")
  args = parser.parse_args()
  
  tid=args.tid

  #qname = get_name(graph)
  #wikilink=get_wikipedia_link(tid)
  print "== PROCESSING: %s" %qname
  print "-> Wikipedia page: %s" %wikilink

  print "\nVoci correlate:"  

  wikilink=get_wikipedia_link(tid)

  thesurl=THTERMBASEURL %self.tid
  fter = urllib.urlopen(thesurl)
  ster = fter.read()
  fter.close()