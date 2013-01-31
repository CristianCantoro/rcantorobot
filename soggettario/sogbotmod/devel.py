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

def setup_rootlogger():
  rootlogger = logging.getLogger()
  rootlogger.setLevel(logging.DEBUG)

  console = logging.StreamHandler()
  console.setLevel(logging.DEBUG)

  formatter = logging.Formatter('%(module)s:%(funcName)s:%(lineno)s - %(levelname)-8s: %(message)s')
  console.setFormatter(formatter)

  rootlogger.addHandler(console)

  return rootlogger

def info(object, spacing=10, collapse=1):
  """Print methods and doc strings.
  Takes module, class, list, dictionary, or string."""

  methodList = [method for method in dir(object)]

  processFunc = collapse and (lambda s: " ".join(s.split())) or (lambda s: s)

  print "\n".join(["%s %s" %
  (method.ljust(spacing),
  processFunc(str(getattr(object, method).__doc__)))
  for method in methodList])