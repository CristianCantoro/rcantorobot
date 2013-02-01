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


import os
import sys
import argparse
import logging
from configobj import ConfigObj, ConfigObj, ConfigObjError, flatten_errors

from sbglobal import SOGBOT
from sogbotmot import parse as parser
from sogbotmot import container
from sbvalidate import email_check, writepath_check, loglevel_check
from validate import Validator

logger = logging.getLogger('sogbot.config')

# --- custom types ---
def pos_int(string):
  value = int(string)
  if value < 0:
    msg = "%r must be a positive integer" % string
    raise argparse.ArgumentTypeError(msg)
  return value

# --- custom actions ---
class readfile_action(argparse.Action):
  def __call__(self, parser, namespace, values, option_string=None):
    values = readfile_check(values)
    setattr(namespace, self.dest, values)

class writepath_action(argparse.Action):
  def __call__(self, parser, namespace, values, option_string=None):
    values = writepath_check(values)
    setattr(namespace, self.dest, values)

def parsecli(appname, desc, vers, epi):

  #logger.debug("argv: %s %s %s %s" %(appname, desc, vers, epi))

  parser = argparse.ArgumentParser(description=desc, prog=appname, epilog=epi, formatter_class=argparse.RawDescriptionHelpFormatter)

  VERSIONTEXT='***** %(prog)s VERSION: ' + ' ' + vers + ' ***** - ' + epi

  parser.add_argument('-v', '--version', action='version', version=VERSIONTEXT)

  parser.add_argument('-c', '--config-file', type=readfile_action, help='specifica un file di configurazione diverso da quello predefinito')

  parser.add_argument('-i', '--id-file', type=readfile_action, help='specifica un file di input', dest='tidfile')  

  parser.add_argument('-t', '--throttle-time', type=pos_int, help='il tempo di attesa (in secondi) tra due controlli', dest='delay_time')
  parser.add_argument('-v', '--verbose', action='store_true', help="abilita l'output verboso")
  parser.add_argument('--debug', action='store_true', help="abilita l'output verboso (con messaggi di debug)")

  log_group = parser.add_mutually_exclusive_group()
  loggr = log_group.add_argument_group(title='Log', description='opzioni di log.')  
  loggr.add_argument('--log-dir', action=writepath_action, help='la directory dove salvare il log', dest='logfile_dir')
  loggr.add_argument('--log-file', action='store', help='il nome del file di log', dest='logfile_name')
  loggr.add_argument('--log-level', action='store', help='il livello di dettaglio del file di log', dest='logging_level')
  loggr.add_argument('--log-interval', action='store', choices=['S', 's', 'M', 'm', 'H', 'h', 'D', 'd', 'W', 'w', 'midnight'], help="l'indirizzo mail cui spedire il log", dest='log_interval')
  loggr.add_argument('--log-period', type=pos_int, help="l'indirizzo mail cui spedire il log", dest='log_when')
  loggr.add_argument('--log-backup', type=pos_int, help="l'indirizzo mail cui spedire il log", dest='backup_count')
  log_group.add_argument('--no-log', action='store_true', help='disabilita il log')

  parser.add_argument('--dry', action='store_true', help='esegue il programma senza compiere azioni e senza collegarsi alla rete')
  parser.add_argument('--dry-wiki', action='store_true', help="esegue il programma senza scrivere su Wikipedia")
  
  args = parser.parse_args()
  #print args

  logger.debug("args.__dict__: %s" %args.__dict__)

  dizcli=dict([(name, args.__dict__[name]) for name in args.__dict__.keys() if args.__dict__[name] != None])

  dizcli['enable_logging'] = not args.no_log
  del dizcli['no_log']

  logger.debug("dizcli: %s" %dizcli)
  return dizcli

def parseall(dizcli): 

  cont = container.ConfigContainer(dizcli)

  spec = SOGBOT['CONFIGSPECPATH']

  config = dizcli.pop('config_file')

  #print parserconfig.__name__
  dizconfig = parser.parse(config, spec)

  cont.add_requested('throttle_time')

  cont.add_optional('verbose', default=False)

  cont.add_optional('debug', default=False)

  cont.add_optional('enable_logging', default=True)

  cont.add_optional('logfile_dir', default="")

  cont.add_depending('logfile_name', depends='enable_logging', value=True)

  cont.add_depending('logging_level', depends='enable_logging', value=True)

  cont.add_depending('log_when', depends='enable_logging', value=True)

  cont.add_depending('log_interval', depends='enable_logging', value=True)

  cont.add_depending('backup_count', depends='enable_logging', value=True)

  cont.add_depending('enable_mailing', depends='enable_logging', value=True)

  cont.add_depending('sendlog_to', depends='enable_mailing', value=True)

  cont.add_depending('sendlog_when', depends='enable_mailing', value=True)

  cont.add_optional('dry_run', default=False)

  cont.add_optional('dry_send', default=False)

  cont.add_optional('dry_action', default=False)

  cont.merge(dizconfig, priority=False)

  diz = cont.get_container('dict')
  
  logger.debug("Parsing results: %s" %diz)

  return diz
 
def parse():

  appname = SOGBOT['APPNAME']
  desc = SOGBOT['DESCRIPTION']
  vers = SOGBOT['VERSION']
  epi = SOGBOT['EPILOG']

  CONFIGNAME = SOGBOT['CONFIGNAME']

  dizcli = parsecli(appname, desc, vers, epi)

  if not ('config_file' in dizcli.keys()):
    base_dir = SOGBOT['BASE_DIR']
    config = os.path.join(SOGBOT['CONFIG_DIR'], SOGBOT['CONFIGNAME'])
    dizcli['config_file'] = config

  logger.debug("dizcli: %s" %dizcli)

  return dizcli


# ----- main -----
if __name__ == '__main__':
  import os
  import tuct

  APPNAME = "sogbot"
  VERSION = "alpha"

  CONFIGNAME = 'sogbot.cfg'

  CONFIGSPECNAME = 'sogbot.spec.cfg'

  CFGDIR = os.path.normpath(os.path.dirname(os.path.realpath(__file__)) + '/../config')

  print "CFGDIR =", CFGDIR

  CFGFILE = CFGDIR + '/' + CONFIGNAME

  print "CFGFILE = ", CFGFILE

  CFGSPECFILE = CFGDIR + '/' + CONFIGSPECNAME

  print "CFGSPECFILE = ", CFGSPECFILE

  DESCRIPTION = "Descrizione di prova"

  EPILOG = "Epilogo di prova"

  app = tuct.Tuct(
                  APPNAME = APPNAME,

                  VERSION = VERSION,

                  CONFIGNAME = CONFIGNAME,

                  CONFIGSPECNAME = CONFIGSPECNAME,

                  CONFIGPATH = CFGFILE,

                  CONFIGSPECPATH = CFGSPECFILE,

                  DESCRIPTION = DESCRIPTION,

                  EPILOG = EPILOG 
                 )

  dizcli = parsecli(appname, desc, vers, epi)
