#!/usr/bin/python
# -*- coding: utf-8  -*-
#
# (C) Pywikipedia bot team, 2006-2011
#
# Distributed under the terms of the MIT license.
#
# version= '$Id: basic.py 10404 2012-06-21 18:19:05Z russblau $'
#

import pywikibot
from pywikibot import pagegenerators
from pywikibot import i18n

# This is required for the text that is shown when you run this script
# with the parameter -help.
docuReplacements = {
    '&params;': pagegenerators.parameterHelp
}

class BasicBot:
    # Edit summary message that should be used is placed on /i18n subdirectory.
    # The file containing these messages should have the same name as the caller
    # script (i.e. basic.py in this case)

    def __init__(self, generator, dry):
        """
        Constructor. Parameters:
            @param generator: The page generator that determines on which pages
                              to work.
            @type generator: generator.
            @param dry: If True, doesn't do any real changes, but only shows
                        what would have been changed.
            @type dry: boolean.
        """
        self.generator = generator
        self.dry = dry
        # Set the edit summary message
        self.summary = i18n.twtranslate(site, 'basic-changing')

    def run(self):
        for page in self.generator:
            self.treat(page)

    def treat(self, page):
        """
        Loads the given page, does some changes, and saves it.
        """
        text = self.load(page)
        if not text:
            return

        ################################################################
        # NOTE: Here you can modify the text in whatever way you want. #
        ################################################################

        print page.isDisambig()

        # Scrive un file.
        tmpoutfile = open("test.txt","w")

        DELIMITER = '|'
        ENCODING = 'utf-8'


        tmpoutfile.write(text.encode(ENCODING))
        tmpoutfile.close()

        tmpinfile = open("test.txt","r")
        lines = tmpinfile.readlines()
        tmpinfile.close()

        STRING = "{{WLM-riga|"
        lines = [l.replace(STRING,'').replace('}}','') for l in lines if l.find(STRING)==0]

        tmpfile = open("tmp.txt","a")
        tmpfile.write(''.join(lines))
        tmpfile.close()

        #print page, '\t', len(lines)

        #tmpfile = open("tmp.txt","r")
        #reader = UnicodeReader(tmpfile, delimiter=DELIMITER, encoding=ENCODING)
        #rowlist = list(reader) 

        #print rowlist
        
            #if not self.save(text, page, self.summary):
                #pywikibot.output(u'Page %s not saved.' % page.title(asLink=True))

    def load(self, page):
        """
        Loads the given page, does some changes, and saves it.
        """
        try:
            # Load the page
            text = page.get()
        except pywikibot.NoPage:
            pywikibot.output(u"Page %s does not exist; skipping."
                             % page.title(asLink=True))
        except pywikibot.IsRedirectPage:
            pywikibot.output(u"Page %s is a redirect; skipping."
                             % page.title(asLink=True))
        else:
            return text
        return None

    def save(self, text, page, comment=None, minorEdit=True,
             botflag=True):
        # only save if something was changed
        if text != page.get():
            # Show the title of the page we're working on.
            # Highlight the title in purple.
            pywikibot.output(u"\n\n>>> \03{lightpurple}%s\03{default} <<<"
                             % page.title())
            # show what was changed
            pywikibot.showDiff(page.get(), text)
            pywikibot.output(u'Comment: %s' %comment)
            if not self.dry:
                choice = pywikibot.inputChoice(
                    u'Do you want to accept these changes?',
                    ['Yes', 'No'], ['y', 'N'], 'N')
                if choice == 'y':
                    try:
                        page.text = text
                        # Save the page
                        page.save(comment=comment or self.comment,
                                  minor=minorEdit, botflag=botflag)
                    except pywikibot.LockedPage:
                        pywikibot.output(u"Page %s is locked; skipping."
                                         % page.title(asLink=True))
                    except pywikibot.EditConflict:
                        pywikibot.output(
                            u'Skipping %s because of edit conflict'
                            % (page.title()))
                    except pywikibot.SpamfilterError, error:
                        pywikibot.output(
u'Cannot change %s because of spam blacklist entry %s'
                            % (page.title(), error.url))
                    else:
                        return True
        return False

def main(filelist):
    global site
    # This factory is responsible for processing command line arguments
    # that are also used by other scripts and that determine on which pages
    # to work on.
    genFactory = pagegenerators.GeneratorFactory()
    # The generator gives the pages that should be worked upon.
    gen = None
    # This temporary array is used to read the page title if one single
    # page to work on is specified by the arguments.
    pageTitleParts = []
    # If dry is True, doesn't do any real changes, but only show
    # what would have been changed.
    dry = False

    print "RCantoroBot"
    # Parse command line arguments
    for arg in pywikibot.handleArgs():
        if arg.startswith("-dry"):
            dry = True
        else:
            # check if a standard argument like
            # -start:XYZ or -ref:Asdf was given.
            if not genFactory.handleArg(arg):
                pageTitleParts.append(arg)
    site = pywikibot.Site()
    site.login()

    if pageTitleParts == []:
      f=open(filelist,"r")
      pageTitleParts=f.readlines()

    print pageTitleParts

    if pageTitleParts != []:
        pages = [pywikibot.Page(pywikibot.Link(pageTitle, site)) for pageTitle in pageTitleParts]
        #print pages
        gen = iter([page for page in pages])
        #print gen

    if not gen:
        gen = genFactory.getCombinedGenerator()
    if gen:
        # The preloading generator is responsible for downloading multiple
        # pages from the wiki simultaneously.
        gen = pagegenerators.PreloadingGenerator(gen)
        #print gen
        bot = BasicBot(gen, dry)
        bot.run()
    else:
        pywikibot.showHelp()

def get_wikilink():
  filelist="botlist.txt"

  try:
      main(filelist)
  finally:
      pywikibot.stopme()

if __name__ == "__main__":
  filelist="botlist.txt"

  try:
      main(filelist)
  finally:
      pywikibot.stopme()
