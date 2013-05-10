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

logger = logging.getLogger('sogbotmod.template')

from sbbot import SogBot

class Template(object):

  def __init__(self,term,uitems=None,ritems=None,nitems=None,bitems=None,dry=False):
    global site
    dry = True

    self.term=term
    self.uitems=uitems
    self.ritems=ritems
    self.nitems=nitems
    self.bitems=bitems
    self.dry=dry
    self.bot=SogBot([],self.dry)

  def login(self):
    site = pywikibot.Site()
    site.login()

  def write(self):
    self.bot.run()

  def save(self):
    if not self.dry:
      pass
    logger.debug("Saving")

  def logoff(self):
    pywikibot.stopme()

# ----- main -----
if __name__ == '__main__':
  print "Template"