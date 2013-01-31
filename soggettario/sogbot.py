#!/usr/bin/python
# -*- coding: utf-8  -*-
#########################################################################
# Copyright (C) 2012 Cristian Consonni <cristian.consonni@gmail.com>.
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
from rdflib import Graph, Literal, Namespace, RDF, URIRef, plugin

def get_name(g):
  qname=""
  for s, p, o in g:
    if p == pred:
      qname = o

  return qname

def get_wikipedia_link(tid):
  thesurl="http://thes.bncf.firenze.sbn.it/termine.php?id=%d" %tid
  fter = urllib.urlopen(thesurl)
  ster = fter.read()
  fter.close()
  html = fromstring(ster)
  links = html.xpath('//a/@href')
  wikilink=[l for l in links if "it.wikipedia.org" in l][0]

  wikilink=wikilink.replace(" ","_")
  return wikilink

def dbpedia_link(g,skos):
  link=None
  for s, p, o in g:
    if p == skos.closeMatch:
      if "dbpedia" in o:
        link=o.replace("http://it.dbpedia.org/resource/","")

  #print link
  return link

parser = argparse.ArgumentParser()
parser.add_argument("tid", type=int, help="term id number")
args = parser.parse_args()

tid=args.tid

skosurl="http://thes.bncf.firenze.sbn.it/SKOS.php?id=%d" %tid

wikilink=get_wikipedia_link(tid)

fsko = tempfile.NamedTemporaryFile()
urllib.urlretrieve(skosurl, fsko.name)    

graph = Graph()
skos = Namespace('http://www.w3.org/2004/02/skos/core#')
graph.bind('skos', skos)

graph.parse(fsko.name)
fsko.close()

plugin.register(
    'sparql', rdflib.query.Processor,
    'rdfextras.sparql.processor', 'Processor')
plugin.register(
    'sparql', rdflib.query.Result,
    'rdfextras.sparql.query', 'SPARQLQueryResult')

pred=skos.prefLabel
#print pred
qname = get_name(graph)

print "== PROCESSING: %s" %qname
print "-> Wikipedia page: %s" %wikilink

print "\nVoci correlate:"
qres = graph.query(
    """SELECT DISTINCT ?a ?b
       WHERE {
          ?a skos:related ?b .
       }""",
    initNs=dict(
        skos=Namespace("http://www.w3.org/2004/02/skos/core#")))

for row in qres.result:
  g = Graph()
  relurl=row[1]
  frel = tempfile.NamedTemporaryFile()
  #print relurl
  response = urllib.urlretrieve(relurl, frel.name)
  g.parse(frel.name)
  frel.close()
  relwiki=dbpedia_link(g,skos)
  rname=get_name(g)
  reltext = "* %s is related to %s" %(qname,rname)
  if relwiki:
    relwiki="http://it.wikipedia.org/wiki/"+relwiki
    reltext = reltext + " - (%s)" %relwiki

  print reltext
