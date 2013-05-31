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
EXTLINKREGEX =re.compile("\[http://(.*)\](.*)\n",flags=re.IGNORECASE)
THESREGEX = re.compile("{{Thesaurus BNCF(.*)}}",flags=re.IGNORECASE)
DISAMBREGEX=re.compile("{{disambigua}}",flags=re.IGNORECASE)
LINKREGEX = re.compile("==\s*collegamenti esterni\s*==",flags=re.IGNORECASE)
PORTALREGEX = re.compile("{{portale\|(.*)}}",flags=re.IGNORECASE)
CATREGEX = re.compile("\[\[Categoria:(.*)\]\]",flags=re.IGNORECASE)
SUBSEZREGEX = re.compile("===(.*)===",flags=re.IGNORECASE)
INTERPROGREGEX = re.compile("{{interprogetto(.*)}}\n",flags=re.IGNORECASE)
TEMPLATEREGEX = re.compile("\n{{(.*)}}\n",flags=re.IGNORECASE)
CORRELSEZREGEX = re.compile("\n==\s*voci correlate\s*==",flags=re.IGNORECASE)
CORRELLINKREGEX = re.compile("\*\s*\[\[(.*)\]\](.*)\n",flags=re.IGNORECASE)

class TemplateAdder(SogBot):

   def __init__(self,
                term,
                site=None,
                dry=False,
                dry_wiki=False,
                clean=False,
                manual=False
               ):

      self.term = term
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
      
      match_thes=THESREGEX.search(self.newtext)
      
      if not match_thes:
         match_dis=DISAMBREGEX.search(self.newtext)
         
         if not match_dis:
            match_link=LINKREGEX.search(self.newtext)
            match_portal=PORTALREGEX.search(self.newtext)
            match_cat=CATREGEX.search(self.newtext)       
            match_interprog=INTERPROGREGEX.search(self.newtext)
            match_correl=CORRELSEZREGEX.search(self.newtext)

            if match_link:
               logger.debug('Trovato "== Collegamenti esterni =="')
               endpos = match_link.end()
               startpos = len(self.newtext)
               match_sez=SUBSEZREGEX.search(self.newtext[endpos+1:])
               if match_sez:
                  startpos = endpos+match_sez.end() 
               elif match_portal:
                  startpos = match_portal.start()
               elif match_cat:
                  startpos = match_cat.start()
                  
               lastlinkpos=startpos-1
               restext=self.newtext[endpos+1:startpos-1]
               logger.debug(restext)
               match_extlink=EXTLINKREGEX.finditer(restext)
               if match_extlink:
                  ends=[m.end() for m in match_extlink]
                  if len(ends) > 0:
                     lastlinkpos = endpos+ends[-1]
                  else:
                     lastlinkpos=endpos

               if self.target:
                  templatetext = "\n* {{Thesaurus BNCF}}"
               else:
                  templatetext = "\n* {{Thesaurus BNCF|%d}}" %self.term.tid
               
               logger.debug(endpos)
               self.newtext = self._insert_text(templatetext,startpos=lastlinkpos)
            elif match_interprog:
               logger.debug('Trovato "{{inteprogetto}}"')
               templatetext = "\n== Collegamenti esterni ==\n"
               if self.target:
                  templatetext += "* {{Thesaurus BNCF}}\n"
               else:
                  templatetext += "* {{Thesaurus BNCF|%d}}\n" %self.term.tid
               pos = match_interprog.end()
               logger.debug(pos)
               self.newtext = self._insert_text(templatetext,endpos=pos)
            elif match_correl:
               logger.debug('Trovato "== Voci correlate =="')
               templatetext = "\n\n== Collegamenti esterni ==\n"
               endpos = match_correl.end()
               startpos = len(self.newtext)
               if match_portal:
                  startpos = match_portal.start()
               elif match_cat:
                  startpos = match_cat.start()
                  
               lastlinkpos=startpos
               restext=self.newtext[endpos+1:startpos-1]
               logger.debug(restext)
               match_correllink=CORRELLINKREGEX.finditer(self.newtext[endpos+1:])

               if match_correllink:
                  ends=[m.end() for m in match_correllink]
                  if len(ends) >0:
                     lastlinkpos = endpos+ends[-1]
                  else:
                     lastlinkpos = endpos+1

               if self.target:
                  templatetext += "* {{Thesaurus BNCF}}"
               else:
                  templatetext += "* {{Thesaurus BNCF|%d}}" %self.term.tid
               
               logger.debug(endpos)
               self.newtext = self._insert_text(templatetext,startpos=lastlinkpos)

            elif match_portal:
               logger.debug('Trovato "{{Portale}}"')
               templatetext = "== Collegamenti esterni ==\n"
               if self.target:
                  templatetext += "* {{Thesaurus BNCF}}\n\n"
               else:
                  templatetext += "* {{Thesaurus BNCF|%d}}\n\n" %self.term.tid
               pos = match_portal.start()
               logger.debug(pos)
               self.newtext = self._insert_text(templatetext,startpos=pos)
#             elif match_template:
#                logger.debug('Trovato "{{Portale}}"')
#                templatetext = "== Collegamenti esterni ==\n"
#                if self.target:
#                   templatetext += "* {{Thesaurus BNCF}}\n\n"
#                else:
#                   templatetext += "* {{Thesaurus BNCF|%d}}\n\n" %self.term.tid
#                pos = match_portal.start()
#                logger.debug(pos)
#                self.newtext = self._insert_text(templatetext,startpos=pos)            
            elif match_cat:
               logger.debug('Trovata "[Categoria]"')
               templatetext = "== Collegamenti esterni ==\n"              
               if self.target:
                  templatetext += "* {{Thesaurus BNCF}}\n\n"
               else:
                  templatetext += "* {{Thesaurus BNCF|%d}}\n\n" %self.term.tid
               pos = match_cat.start()
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
         comment="inserimento di {{Thesaurus BNCF}}, "
         comment+="[[Discussioni progetto:Coordinamento/Bibliografia e fonti#Collaborazione come Biblioteca Nazionale di Firenze|discussione]]"
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
      match_clean=CLEANREGEX.search(self.text)
      
      if match_clean:
         logger.debug("Trovato {{ThesaurusBNCF}}")
         startpos = match_clean.start()
         endpos = match_clean.end()
         restext=self.text[endpos+1:]
         match_extlink=EXTLINKREGEX.search(restext)
         
         if match_extlink:
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