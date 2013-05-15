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

logger = logging.getLogger('sogbot.template')

import pywikibot
import re
from sbbot import SogBot

THESREGEX = re.compile("{{Thesaurus BNCF(.*)}}",flags=re.IGNORECASE)
LINKREGEX = re.compile("== collegamenti esterni ==",flags=re.IGNORECASE)
PORTALREGEX = re.compile("{{portale\|(.*)}}",flags=re.IGNORECASE)
CATREGEX = re.compile("\[\[Categoria:(.*)\]\]",flags=re.IGNORECASE)

class TemplateAdder(SogBot):

   def __init__(self,
                term,
                uitems=None,
                ritems=None,
                nitems=None,
                bitems=None,
                site=None,
                dry=False,
                dry_wiki=False,
                manual=False
               ):

      self.term = term
      self.uitems = uitems
      self.ritems = ritems
      self.nitems = nitems
      self.bitems = bitems
      if site is None:
         self.site = pywikibot.Site()
      else:
         self.site = site
      self.dry = dry
      self.dry_wiki = dry_wiki
      self.manual = manual
      super(TemplateAdder, self).__init__(term=self.term,
                                          site=self.site,
                                          dry=self.dry,
                                          manual=self.manual
                                         )
      

   def login(self):
      logger.debug("Login ...")
      if not self.dry:
         self.site.login()
      else:
         logger.debug("Dry run - No login")

   def run(self):
      logger.debug("Run ...")
      if not self.dry:
         for page in self.generator:
            self.page=page
            self.treat()
      else:
         logger.debug("Dry run - No run")

   def _insert_text(self,templatetext,startpos=None,endpos=None):
      
      if endpos:
         logger.debug("using endpos")
         newtext = self.text[:endpos] 
         newtext = newtext + templatetext
         newtext = newtext + self.text[endpos:]
      elif startpos:
         logger.debug("using startpos")
         newtext = self.text[:startpos]
         newtext = newtext + templatetext
         newtext = newtext + self.text[startpos:]
      else:
         newtext = self.text + templatetext

      return newtext

   def treat(self):
      logger.debug("Treat ...")
      super(TemplateAdder, self).treat(self.page)

      self.newtext = self.text
      
      match0=THESREGEX.search(self.text)
      if not match0:
         match1=LINKREGEX.search(self.text)
         match2=PORTALREGEX.search(self.text)
         match3=CATREGEX.search(self.text)
   
         if match1:
            logger.debug('Trovato "== Collegamenti esterni =="')
            templatetext = "\n* {{ThesaurusBNCF}}"
            pos = match1.end()
            logger.debug(pos)
            self.newtext = self._insert_text(templatetext,endpos=pos)
         elif match2:
            logger.debug('Trovato "{{Portale}}"')
            templatetext = "== Collegamenti esterni ==\n* {{Thesaurus BNCF}}\n\n"
            pos = match2.start()
            logger.debug(pos)
            self.newtext = self._insert_text(templatetext,startpos=pos)
         elif match3:
            logger.debug('Trovata "[Categoria]"')
            templatetext = "== Collegamenti esterni ==\n* {{Thesaurus BNCF}}\n\n"
            pos = match3.start()
            logger.debug(pos)
            self.newtext = self._insert_text(templatetext,startpos=pos)
         else:
            logger.debug('Inserisco alla fine')
            templatetext = "\n\n== Collegamenti esterni ==\n* {{Thesaurus BNCF}}\n"
            self.newtext = self._insert_text(templatetext)
         
         if self.manual:
            logger.info(self.newtext)
         else:
            logger.debug(self.newtext)
      else:
         logger.debug("{{ThesaurusBNCF}} is already there - doing nothing")

      return self.newtext

   def save(self):
      logger.debug("Save ...")
      saveres=False
      
      if not self.dry or self.dry_wiki:
         comment="Aggiungo il template {{Thesaurus BNCF}}"
         saveres=super(TemplateAdder, self).save(text=self.newtext,
                                                 page=self.page,
                                                 comment=comment)
         if saveres:
            logger.debug("Saving template to: %s" %self.term.name)
      else:
         logger.debug("Dry run - doing nothing")

      return saveres

   def logoff(self):
      logger.debug("Logoff ...")
      if not self.dry:
         pywikibot.stopme()
      else:
         logger.debug("Dry run - No logoff")

# ----- main -----
if __name__ == '__main__':
   print "Template"