# -*- coding: utf-8  -*-
#########################################################################
# Adapted from basic.py
# found in pywikipedia-rewrite (scripts dir)
# at https://toolserver.org/~pywikipedia/
#
# (C) Pywikipedia bot team, 2006-2011
#
# Distributed under the terms of the MIT license.
#
# version= '$Id: basic.py 10404 2012-06-21 18:19:05Z russblau $'
#
# Adapted by Cristian Consonni
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

import logging

logger=logging.getLogger('sogbot.sbbot')

import pywikibot
from pywikibot import pagegenerators

class SogBot:

   def __init__(self, site, term, dry,manual):
      """
      Constructor. Parameters:
         @param generator: The page generator that determines on which pages
                              to work.
         @type generator: generator.
         @param dry: If True, doesn't do any real changes, but only shows
                        what would have been changed.
         @type dry: boolean.
      """
      self.site = site
      self.dry = dry
      self.manual = manual
      self.term = term
      self.generator = self._get_generator()

   def _get_generator(self):

      pages = [pywikibot.Page(pywikibot.Link(self.term.name, self.site))]
      gen = iter([page for page in pages])
      gen = pagegenerators.PreloadingGenerator(gen)

      return gen

   def run(self):
      for page in self.generator:
         self.treat(page)

   def treat(self, page):
      """
         Loads the given page, does some changes, and saves it.
      """
      self.text = self.load(page)
      #print self.text


   def load(self, page):
      """
         Loads the given page, does some changes, and saves it.
      """
      try:
         # Load the page
         text = page.get()
      except pywikibot.NoPage:
         logger.debug(u"Page %s does not exist; skipping."
                             % page.title(asLink=True))
      except pywikibot.IsRedirectPage:
         targetpage = page.getRedirectTarget()
         logger.debug("Page %s is a redirect; following to %s"
                             % (page.title(asLink=True),
                               targetpage.title(asLink=True))
                     )
         text = self.load(targetpage)
         return text
      else:
         return text
      return None

   def _save(self,page,text,comment,minorEdit,botflag):
      if self.text != text:
         try:
            page.text = text
            # Save the page
            page.save(comment=comment or self.comment,
                         minor=minorEdit, botflag=botflag)
         except pywikibot.LockedPage:
               logger.error(u"Page %s is locked; skipping."
                                % page.title(asLink=True))
         except pywikibot.EditConflict:
               logger.error(
                   u'Skipping %s because of edit conflict'
                   % (page.title()))
         except pywikibot.SpamfilterError, error:
               logger.error(
                   u'Cannot change %s because of spam blacklist entry %s'
                   % (page.title(), error.url))
         else:
            return True

      return False

   def save(self, text, page, comment=None, minorEdit=True,
             botflag=True):
      # only save if something was changed
      saveres=False
      if text != page.get():
         if not self.dry:
            if self.manual:
               # Show the title of the page we're working on.
               # Highlight the title in purple.
               pywikibot.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                                % page.title())
               # show what was changed
               pywikibot.showDiff(page.get(), text)
               logger.info(u'Comment: %s' %comment)

               choice = pywikibot.inputChoice(
                       u'Do you want to accept these changes?',
                       ['Yes', 'No'], ['y', 'N'], 'N')

            if not self.manual or (self.manual and choice == 'y'):
               saveres=self._save(page,text,comment,minorEdit,botflag)
               
      return saveres