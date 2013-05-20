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

# ***** logging module objects and definition *****
import logging
from logging import handlers

LOGFORMAT_STDOUT = { logging.DEBUG: '%(module)s:%(funcName)s:%(lineno)s - %(levelname)-8s: %(message)s',
             logging.INFO: '%(levelname)-8s: %(message)s',
             logging.WARNING: '%(levelname)-8s: %(message)s',
             logging.ERROR: '%(levelname)-8s: %(message)s',
             logging.CRITICAL: '%(levelname)-8s: %(message)s'
           }

LOGFORMAT_FILE = { logging.DEBUG: "%(module)s:%(funcName)s:%(lineno)s - ***%(levelname)s***: %(message)s",
           logging.INFO: "%(asctime)s ***%(levelname)s***: %(message)s",
           logging.WARNING: "%(asctime)s ***%(levelname)s***: [%(module)s:%(funcName)s] %(message)s",
           logging.ERROR: "%(asctime)s *****%(levelname)s*****: ***[%(module)s:%(funcName)s:%(lineno)s]*** ***%(message)s***",
           logging.CRITICAL: "%(asctime)s *****%(levelname)s*****: ***[%(module)s:%(funcName)s:%(lineno)s]*** ***%(message)s***"
         }

LOGDATEFMT = '%Y-%m-%d %H:%M:%S'

class NullHandler(logging.Handler):
   def emit(self, record):
      pass

class Formattatore(logging.Formatter):
   def format(self, record):
      self._fmt=LOGFORMAT_FILE[record.levelno]
      s = logging.Formatter.format(self,record)
      return s

# ***** END logging module *****

# ***** system imports *****
import os
import time
import pywikibot

# ***** START sogbot *****
from sogbotmod import sbsoggettario as sog
from sogbotmod import sbconfig as config
from sogbotmod.sbglobal import SOGBOT
from sogbotmod.sblinkretriever import LinkRetriever
from sogbotmod.sbtemplate import TemplateAdder

# --- root logger
rootlogger = logging.getLogger('sogbot')
rootlogger.setLevel(logging.DEBUG)

lvl_config_logger = logging.INFO
#lvl_config_logger = logging.DEBUG

console = logging.StreamHandler()
console.setLevel(lvl_config_logger)

formatter = logging.Formatter(LOGFORMAT_STDOUT[lvl_config_logger])
console.setFormatter(formatter)

rootlogger.addHandler(console)

logger = logging.getLogger('sogbot.main')

cfgcli = config.parse()
  
BASE_DIR = SOGBOT['BASE_DIR']
CURR_DIR = os.path.abspath(os.path.normpath(os.getcwd()))
verbose = cfgcli['verbose']
debug = cfgcli['debug']

manual = cfgcli['manual']
if manual:
   verbose=True
   logger.info("--manual set - activating verbose")

if verbose or debug:
   if debug: 
      lvl = logging.DEBUG
   else: 
      lvl = logging.INFO
   formatter = logging.Formatter(LOGFORMAT_STDOUT[lvl])
   console.setFormatter(formatter)
   console.setLevel(lvl)
else:
   h = NullHandler()
   console.setLevel(logging.WARNING)
   rootlogger.addHandler(h)

logger.info("BASE_DIR: %s" %BASE_DIR)
logger.info("CURR_DIR: %s" %CURR_DIR)

logger.debug("verbose: %s" %verbose)
logger.debug("debug: %s" %debug)

cfg = config.parseall(dizcli=cfgcli)
enable_logging= cfg['enable_logging']
logger.debug("enable_logging: %s" %enable_logging)

logfile_dir = cfg['logfile_dir']
logfile_name = cfg['logfile_name']
logfile = os.path.normpath(os.path.join(logfile_dir, logfile_name))

log_when = cfg['log_when']
log_interval = cfg['log_interval']
log_backup = cfg['backup_count']

# --- Abilita il log su file ---
if enable_logging:
   logger.debug("logfile: %s" %logfile)
   ch = handlers.TimedRotatingFileHandler(filename=logfile, when=log_when, interval=log_interval, backupCount=log_backup)

   if debug: lvl = logging.DEBUG
   else: lvl = logging.INFO

   ch.setLevel(lvl)
   formatter = Formattatore(LOGFORMAT_FILE, datefmt=LOGDATEFMT)
   ch.setFormatter(formatter)
   rootlogger.addHandler(ch)

logger.debug("cfg: %s" %cfg)

idlist = cfg['idlist']
dry = cfg['dry']
dry_wiki = cfg['dry_wiki']
clean = cfg['clean']
manual = cfg['manual']

tidfile = open(idlist)
tidlist = tidfile.readlines()

tidlist = [int(n.strip('\n')) for n in tidlist]
logger.debug("tidlist: %s" %tidlist)

skiplist=[]
if cfg['skiplist'] is not None:
   skipfile = open(cfg['skiplist'])
   skiplist = skipfile.readlines() 
   skiplist = [int(s.strip()) for s in skiplist]
logger.debug('skiplist: %s' %skiplist)

throttle_time = cfg['throttle_time']
logger.debug("throttle_time: %s", throttle_time)

# ***** utility functions *****

def write_term(filename,term,msg):
   if filename is not None:
      logger.debug(msg)
      logger.debug("filename: %s" %filename)
      outfile = open(filename,'a+')
      outfile.write("%d\n" %term.tid)
      outfile.close()
   
      filename=filename+'.term'
      logger.debug("Writing terms")
      logger.debug("term filename: %s" %filename)
      outfile = open(filename,'a+')
      outfile.write("%s: %d\n" %(term.name,term.tid))
      outfile.close()

#if cfg['disamblist'] is not None:
#    disamblistname=cfg['disamblist']
#    logger.debug("Writing disamb tids in disamblist")
#    logger.debug("disamblist: %s" %disamblistname)
#    disambfile = open(disamblistname,'w+')
#    for term in disambterm:
#       disambfile.write("%d\n" %term.tid)
#  
#    disamblistname=disamblistname+'.term'
#    logger.debug("Writing disamb terms in disamblist")
#    logger.debug("disamblist: %s" %disamblistname)
#    disambfile = open(disamblistname,'w+')
#    for term in disambterm:
#       disambfile.write("%s: %d\n" %(term.name,term.tid))


# errorlistname=cfg['errorlist']
# logger.debug("Writing errors (tids)")
# logger.debug("errorlist file: %s" %errorlistname)
# errorfile = open(errorlistname,'w+')
# for term in errorterm:
#    errorfile.write("%d\n" %term.tid)
# 
# errorlistname=errorlistname+'.term'
# logger.debug("Writing errors (terms)")
# logger.debug("errorlist file: %s" %errorlistname)
# errorfile = open(errorlistname,'w+')
# for term in errorterm:
#    errorfile.write("%s: %d\n" %(term.name,term.tid))

doneterm=[]
errorterm=[]
disambterm=[]
logger.info("==========\n\n")

logger.debug("==========\n")
site = pywikibot.Site()

logger.debug("Login ...")
if not dry:
   site.login()
else:
   logger.debug("Dry run - No login")
logger.debug("==========\n\n")

for tid in tidlist:

   if tid in skiplist:
      logger.debug("Tid %d in skiplist. Skipping ..." %tid)
      logger.info("==========\n")
      continue

   term=sog.Term(tid)

   logger.info("== PROCESSING: %s ==" %term.name)
   wikiname=None
   if term.wikiname:
      wikiname=term.wikiname.replace('_',' ')
   logger.info("-> Wikipedia page: %s - url: %s - (tid:%d)" %(wikiname,
               term.wikilink,term.tid))

   uitems=term.used_items()
   logger.info("Sinonimi:")
   for u in uitems:
      logger.info("* %s, %s, %s" %(u.name, u.wikilink, u.tid))

   ritems=term.related_items()
   logger.info("Voci correlate:")
   for r in ritems:
      logger.info("* %s, %s, %s" %(r.name, r.wikilink, r.tid))

   nitems=term.narrower_items()
   logger.info("Narrower:")
   for n in nitems:
      logger.info("* %s, %s, %s" %(n.name, n.wikilink, n.tid))

   bitems=term.broader_items()
   logger.info("Broader:")
   for b in bitems:
      logger.info("* %s, %s, %s" %(b.name, b.wikilink, b.tid))

   LinkRetriever()

   tmpl=TemplateAdder(term=term,
                      uitems=uitems,
                      ritems=ritems,
                      nitems=nitems,
                      bitems=bitems,
                      site=site,
                      dry=dry,
                      dry_wiki=dry_wiki,
                      clean=clean,
                      manual=manual
                     )
   try:
      tmpl.run()
      saveres=tmpl.save()
      if saveres:
         write_term(cfg['donelist'],term,'Writing processed terms to donelist')
      if tmpl.is_disamb():
         write_term(cfg['disamblist'],term,'Writing disambig terms to disamblist')
      if tmpl.has_nodata():
         write_term(cfg['nodatalist'],term,'Writing processed terms to nodatalist')
   except Exception as e:
      logger.error("Term %s raised exception: %s" %(term.name,e))
      errorterm.append(term)

   logger.debug("donetid: %s" %doneterm)
   logger.info("==========\n")
   time.sleep(throttle_time)

logger.debug("\n==========\n")
if not dry:
   logger.debug("Logoff ...")
   pywikibot.stopme()
logger.debug("==========\n\n")
      
logger.info("Everything done! Great job! Exiting")
exit(0)