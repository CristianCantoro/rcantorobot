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
##########################################################################

import tempfile
import urllib
from lxml import etree

SEARCH="https://it.wikipedia.org/w/api.php?action=query&list=search&srsearch=%s\
&srprop=score&redirects=true&format=xml"

def wikipedia_search(searchterm, locfile=None):
    
  searchurl = SEARCH %searchterm
  #print searchurl

  filename=locfile
  if locfile is None:
    fser = tempfile.NamedTemporaryFile()
    urllib.urlretrieve(searchurl, fser.name)
    filename=fser.name

  ts = etree.parse(filename)

  if locfile is None:
    fser.close()

  sroot = ts.getroot()

  reslist=[e.attrib for e in sroot.findall("./query/search/p")]

  return reslist

if __name__ == "__main__":
  searchterm="Pippo"

  results=wikipedia_search(searchterm,locfile="risp5")

  print results