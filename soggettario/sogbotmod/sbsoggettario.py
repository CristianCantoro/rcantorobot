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

import logging

logger = logging.getLogger('sogbotmod.sbsoggettario')

import time
import tempfile
import urllib
import lxml
from lxml.html import fromstring
import rdflib
from rdflib import Graph, Literal, Namespace, RDF, URIRef, plugin

import sbdevel as devel


import inspect


SKOSNS = Namespace('http://www.w3.org/2004/02/skos/core#')
THSKOSBASEURL = "http://thes.bncf.firenze.sbn.it/SKOS.php?id=%d"
THTERMBASEURL = "http://thes.bncf.firenze.sbn.it/termine.php?id=%d"
PURLBASEURL="http://purl.org/bncf/tid/%d"
DBPEDIAURL = "http://it.dbpedia.org"

QUERIES = {'broader': """SELECT DISTINCT ?a ?b
                         WHERE {
                                ?a skos:broader ?b .
                               }""",
           'narrower':"""SELECT DISTINCT ?a ?b
                         WHERE {
                                ?a skos:narrower ?b .
                               }""",
           'related': """SELECT DISTINCT ?a ?b
                         WHERE {
                                ?a skos:related ?b .
                               }""",
           'used':    """SELECT DISTINCT ?a ?b
                         WHERE {
                                ?a skos:used ?b .
                               }"""
          }


class Error(Exception):
  """Base class for exceptions in this module."""
  pass

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

class Term(object):

  def __init__(self, term):

    if isinstance(term,int):
      self.tid = term
      self.purl = PURLBASEURL %self.tid
    elif isinstance(term,rdflib.term.URIRef):
      self.purl = str(term)
      self.tid=int(self.purl.split('/')[-1])

    self.graph = SkosGraph(self.tid)
    self.termpage = self.get_termpage()
    self.name = self.get_name()
    self.dblink = self.get_dblink()
    self.wikilink = self.get_wikilink()
    self._registeredPlugin=False

  def get_name(self):
    qname = None
    pred=SKOSNS.prefLabel

    for s, p, o in self.graph:
      if p==pred:
        qname=o

    self.name=qname
    return qname

  def get_dblink(self):
    link = None
    pred = SKOSNS.closeMatch

    for s, p, o in self.graph:
      if p == pred:
        if DBPEDIAURL in o:
          resurl="%s/resource/" %DBPEDIAURL
          link=o.replace(resurl,'')

    self.dblink=link
    return link

  def get_termpage(self):
    thesurl=THTERMBASEURL %self.tid
    fter = urllib.urlopen(thesurl)
    ster = fter.read()
    fter.close()
    self.termpage=ster
    return ster

  def get_wikilink(self):

    if self.termpage is None:
      self.get_termpage()

    html = fromstring(self.termpage)
    links = html.xpath('//a/@href')
    wikilinklist=[l for l in links if "it.wikipedia.org" in l]
    wikilink=None
    if len(wikilinklist) > 0:
      wikilink=wikilinklist[0].replace(" ","_")

    return wikilink

  def _register_plugin(self):
    rdflib.plugin.register(
    'sparql', rdflib.query.Processor,
    'rdfextras.sparql.processor', 'Processor')

    rdflib.plugin.register(
    'sparql', rdflib.query.Result,
    'rdfextras.sparql.query', 'SPARQLQueryResult')

    self._registeredPlugin=True

  def _skos_query(self,query):
    if not self._registeredPlugin:
      self._register_plugin()

    qres = self.graph.query(query,initNs=dict(skos=SKOSNS))
    return qres

  def has_dblink(self):
    return self.dblink is None

  def has_wikilink(self):
    return self.wikilink is None

  def used_items(self):
    logger.debug('USED')
    qres = self._skos_query(QUERIES['used'])
    logger.debug('query results list: %s' %qres.result)
    items=list()
    for row in qres.result:
      items.append(Term(row[1]))
    return items

  def related_items(self):
    logger.debug('RELATED')
    qres = self._skos_query(QUERIES['related'])
    logger.debug('query results list: %s' %qres.result)
    items=list()
    for row in qres.result:
      items.append(Term(row[1]))
    return items

  def narrower_items(self):
    logger.debug('NARROWER')
    qres = self._skos_query(QUERIES['narrower'])
    logger.debug('query results list: %s' %qres.result)
    items=list()
    for row in qres.result:
      items.append(Term(row[1]))
    return items

  def broader_items(self):
    logger.debug('BROADER')
    qres = self._skos_query(QUERIES['broader'])
    logger.debug('query results list: %s' %qres.result)
    items=list()
    for row in qres.result:
      items.append(Term(row[1]))
    return items

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