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

import argparse
import logging
from sogbotmod import soggettario as sog
from sogbotmod import template as template

# ***** logging module objects and definition *****
import logging
from logging import config
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

# ***** START Autosend *****

# --- root logger
rootlogger = logging.getLogger()
rootlogger.setLevel(logging.DEBUG)

lvl_config_logger = logging.INFO
lvl_config_logger = logging.DEBUG

console = logging.StreamHandler()
console.setLevel(lvl_config_logger)

formatter = logging.Formatter(LOGFORMAT_STDOUT[lvl_config_logger])
console.setFormatter(formatter)

rootlogger.addHandler(console)

#config_logger = logging.getLogger(APPNAME + '.config')
#config_logger.debug("%s" %sys.argv)

#parser = argparse.ArgumentParser()
#parser.add_argument("tid", type=int, help="term id number")
#args = parser.parse_args()

logger = logging.getLogger('sogbot')
logger.debug("start")

tidlist=[]
for tid in tidlist:
  tid=args.tid

  term=sog.Term(tid)

  logger.info("== PROCESSING: %s" %term.name)
  logger.info("-> Wikipedia page: %s" %term.wikilink)

  uitems=term.used_items()
  logger.info("Sinonimi:")
  for u in uitems:
    logger.info("%s, %s" %(u.name, u.wikilink))

  ritems=term.related_items()
  logger.info("Voci correlate:")
  for r in ritems:
    logger.info("%s, %s" %(r.name, r.wikilink))

  nitems=term.narrower_items()
  logger.info("Narrower:")
  for n in nitems:
    logger.info("%s, %s" %(u.name, u.wikilink))

  bitems=term.broader_items()
  logger.info("Broader:")
  for b in bitems:
    logger.info("%s, %s" %(b.name, b.wikilink))

  LinkRetriever()

  tmpl=template.Template(term,uitems,ritems,nitems,bitems)
  tmpl.login()
  tmpl.write()
  tmpl.save()
  tmpl.logoff()

exit(0)