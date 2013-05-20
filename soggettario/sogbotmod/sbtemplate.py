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

CLEANREGEX = re.compile("\n==\s*collegamenti esterni\s*==\s*\n\*\s*{{Thesaurus\s*BNCF(.*)}}",flags=re.IGNORECASE)
EXTLINKREGEX =re.compile("http://",flags=re.IGNORECASE)
THESREGEX = re.compile("{{Thesaurus BNCF(.*)}}",flags=re.IGNORECASE)
DISAMBREGEX=re.compile("{{disambigua}}",flags=re.IGNORECASE)
LINKREGEX = re.compile("==\s*collegamenti esterni\s*==",flags=re.IGNORECASE)
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
                clean=False,
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
      self.clean = clean
      self.manual = manual
      super(TemplateAdder, self).__init__(term=self.term,
                                          site=self.site,
                                          dry=self.dry,
                                          manual=self.manual
                                         )
      self._disamb = False
      self._nodata = False

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
            if self.clean:
               self._clean()
            self._treat()
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

   def _treat(self):
      logger.debug("Treat ...")
      super(TemplateAdder, self).treat(self.page)

      self.newtext = self.text
      
      itemdict=self.item.get()
      target=None
      try:
         claim=itemdict['claims']['p508'][0]
         target=claim.getTarget()
      except KeyError:
         target=None
         logger.debug("Wikidata: property 'Thesaurus BNCF' (p508) not found")
      except IndexError:
         target=None
         logger.debug("Wikidata property has no claims")

      self.target = target
      if target is None:
         self._nodata = True
         logger.debug("No data from Wikidata")
      
      match0=THESREGEX.search(self.newtext)
      
      if not match0:
         match_dis=DISAMBREGEX.search(self.newtext)
         
         if not match_dis:
            match1=LINKREGEX.search(self.newtext)
            match2=PORTALREGEX.search(self.newtext)
            match3=CATREGEX.search(self.newtext)            
            if match1:
               logger.debug('Trovato "== Collegamenti esterni =="')
               if self.target:
                  templatetext = "\n* {{Thesaurus BNCF}}\n"
               else:
                  templatetext = "\n* {{Thesaurus BNCF|%d}}\n" %self.term.tid
               pos = match1.end()
               logger.debug(pos)
               self.newtext = self._insert_text(templatetext,endpos=pos)
            elif match2:
               logger.debug('Trovato "{{Portale}}"')
               templatetext = "== Collegamenti esterni ==\n"
               if self.target:
                  templatetext += "* {{Thesaurus BNCF}}\n"
               else:
                  templatetext += "* {{Thesaurus BNCF|%d}}\n" %self.term.tid
               pos = match2.start()
               logger.debug(pos)
               self.newtext = self._insert_text(templatetext,startpos=pos)
            elif match3:
               logger.debug('Trovata "[Categoria]"')
               templatetext = "== Collegamenti esterni ==\n"              
               if self.target:
                  templatetext += "* {{Thesaurus BNCF}}\n"
               else:
                  templatetext += "* {{Thesaurus BNCF|%d}}\n" %self.term.tid
               pos = match3.start()
               logger.debug(pos)
               self.newtext = self._insert_text(templatetext,startpos=pos)
            else:
               logger.debug('Inserisco alla fine')
               templatetext = "\n\n== Collegamenti esterni ==\n"
               templatetext += "* {{Thesaurus BNCF|%d}}\n\n" %self.term.tid
               self.newtext = self._insert_text(templatetext)
             
            if self.manual:
               logger.info(self.newtext)
            else:
               logger.debug(self.newtext)

         else:
            logger.debug("disambiguation page - doing nothing")
            self._disamb = True
 
      else:
         logger.debug("{{Thesaurus BNCF}} is already there - doing nothing")
      
      return self.newtext

   def save(self):
      logger.debug("Save ...")
      saveres=False
      
      if not self.dry or self.dry_wiki:
         #comment="Aggiungo il template {{Thesaurus BNCF}}"
         comment="Tolgo il parametro di {{Thesaurus BNCF}} per usarlo con Wikidata"
         logger.info("Wikidata target: %s" %str(self.target))
         saveres=super(TemplateAdder, self).save(text=self.newtext,
                                                 page=self.page,
                                                 comment=comment)
         if saveres:
            logger.debug("Saving template to: %s" %self.term.name)
      else:
         logger.debug("Dry run - doing nothing")

      return saveres

   def _clean(self):
      logger.debug("Clean...")
      super(TemplateAdder, self).treat(self.page)
      self.newtext = self.text
      match0=CLEANREGEX.search(self.text)
      
      if match0:
         logger.debug("Trovato {{ThesaurusBNCF}}")
         startpos = match0.start()
         endpos = match0.end()
         restext=self.text[endpos+1:]
         match1=EXTLINKREGEX.search(restext)
         
         if match1:
            templatetext = "== Collegamenti esterni =="
            newtext = self.text[:startpos]
            newtext = newtext + templatetext
            newtext = newtext + self.text[endpos+1:]
            self.newtext = newtext
         else:
            newtext = self.text[:startpos]
            newtext = newtext + self.text[endpos+1:]
            self.newtext = newtext
         
         if self.manual:
            logger.info(self.newtext)
         else:
            logger.debug(self.newtext)
         
      return self.newtext

   def is_disamb(self):
      return self._disamb

   def has_nodata(self):
      return self._nodata

   def logoff(self):
      logger.debug("Logoff ...")
      if not self.dry:
         pywikibot.stopme()
      else:
         logger.debug("Dry run - No logoff")

# ----- main -----
if __name__ == '__main__':
   print "Template"