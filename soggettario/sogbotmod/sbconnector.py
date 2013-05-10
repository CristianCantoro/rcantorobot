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

import urllib

class Error(Exception):
  """Base class for exceptions in this module."""
  pass

class PageGetter(object):

  def __init__(self, url, fname=None, dry=False, local=None):
    self._url = url

    if fname is None:
      self._fname = something
    else:
      self._fname = fname

    urllib.urlretrieve(url, self.fname)
    self._hasPage = True

  def get_fname():
    return self._fname
  
  def get_url():
    return self.url

  def has_page():
    return self._hasPage

# ----- main -----
if __name__ == '__main__':
  pass