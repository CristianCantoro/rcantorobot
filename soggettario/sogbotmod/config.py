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

logger = logging.getLogger('sogbot.config')

configobj_loaded = None
from configobj import ConfigObj, ConfigObj, ConfigObjError, flatten_errors
from validate import Validator

import argparse
from validate import email_check, readpath_check, writepath_check, smtpserver_check, loglevel_check, hour_check

import os
import sys

from sbglobal import SOGBOT

# --- custom types ---
def pos_int(string):
  value = int(string)
  if value < 0:
    msg = "%r must be a positive integer" % string
    raise argparse.ArgumentTypeError(msg)
  return value

# --- custom actions ---
class readpath_action(argparse.Action):
  def __call__(self, parser, namespace, values, option_string=None):
    values = readpath_check(values)
    setattr(namespace, self.dest, values)

class readfile_action(argparse.Action):
  def __call__(self, parser, namespace, values, option_string=None):
    values = readfile_check(values)
    setattr(namespace, self.dest, values)

class smtpserver_action(argparse.Action):
  def __call__(self, parser, namespace, values, option_string=None):
    values = smtpserver_check(values)
    setattr(namespace, self.dest, values)

class writepath_action(argparse.Action):
  def __call__(self, parser, namespace, values, option_string=None):
    values = writepath_check(values)
    setattr(namespace, self.dest, values)

class email_action(argparse.Action):
  def __call__(self, parser, namespace, values, option_string=None):
    values = email_check(values)
    setattr(namespace, self.dest, values)

class hour_action(argparse.Action):
  def __call__(self, parser, namespace, values, option_string=None):
    values = hour_check(values)
    setattr(namespace, self.dest, values)


def parsecli(appname, desc, vers, epi):

  #logger.debug("argv: %s %s %s %s" %(appname, desc, vers, epi))

  parser = argparse.ArgumentParser(description=desc, prog=appname, epilog=epi, formatter_class=argparse.RawDescriptionHelpFormatter)

  VERSIONTEXT='***** %(prog)s VERSION: ' + ' ' + vers + ' ***** - ' + epi

  parser.add_argument('-v', '--version', action='version', version=VERSIONTEXT)

  subparsers = parser.add_subparsers(dest='command', help='-h per gli aiuti dei sottocomandi')

  # create the parser for the "start" command
  parser_start = subparsers.add_parser('start', help='sottocomando start')

  parser_start.add_argument('-c', '--config-file', type=str, help='specifica un file di configurazione diverso da quello predefinito')

  parser_start.add_argument('-d', '--directory', action=readpath_action, help='la directory in cui cercare i file', dest='lookdir')  

  recur_group = parser_start.add_mutually_exclusive_group() 
  parser_start.add_argument('-t', '--throttle-time', type=pos_int, help='il tempo di attesa (in secondi) tra due controlli', dest='delay_time')
  parser_start.add_argument('-v', '--verbose', action='store_true', help="abilita l'output verboso")
  parser_start.add_argument('--debug', action='store_true', help="abilita l'output verboso")

  log_group = parser_start.add_mutually_exclusive_group()
  loggr = log_group.add_argument_group(title='Log', description='opzioni di log.')  
  loggr.add_argument('--log-dir', action=writepath_action, help='la directory dove salvare il log', dest='logfile_dir')
  loggr.add_argument('--log-file', action='store', help='il nome del file di log', dest='logfile_name')
  loggr.add_argument('--log-level', action='store', help='il livello di dettaglio del file di log', dest='logging_level')
  loggr.add_argument('--log-interval', action='store', choices=['S', 's', 'M', 'm', 'H', 'h', 'D', 'd', 'W', 'w', 'midnight'], help="l'indirizzo mail cui spedire il log", dest='log_interval')
  loggr.add_argument('--log-period', type=pos_int, help="l'indirizzo mail cui spedire il log", dest='log_when')
  loggr.add_argument('--log-backup', type=pos_int, help="l'indirizzo mail cui spedire il log", dest='backup_count')

  loggr.add_argument('--log-send-to', action=email_action, help="l'indirizzo mail cui spedire il log", dest='sendlog_to')
  loggr.add_argument('--log-send-when', action=hour_action, help="l'indirizzo mail cui spedire il log", dest='sendlog_when')

  log_group.add_argument('--no-log', action='store_true', help='disabilita il log')

  parser_start.add_argument('--dry-send', action='store_true', help='esegue il programma senza inviare mail')
  parser_start.add_argument('--dry-action', action='store_true', help="esegue il programma senza applicare l'azione finale")
  
  args = parser.parse_args()
  #print args
  
  logger.debug("args.__dict__: %s" %args.__dict__)

  dizcli=dict([(name, args.__dict__[name]) for name in args.__dict__.keys() if args.__dict__[name] != None])
  
  if dizcli['command'] == 'start':
    if not dizcli['recursive']:
      del dizcli['recursive']
     
    if dizcli['non_recursive']:
      dizcli['recursive'] = not args.non_recursive  
    del dizcli['non_recursive']
  
    dizcli['enable_logging'] = not args.no_log
    del dizcli['no_log']
    
    dizcli['auth_required'] = not args.no_auth
    del dizcli['no_auth']
    
    if ('sendlog_to' in dizcli.keys()) or ('sendlog_when' in dizcli.keys()):
      dizcli['enable_mailing'] = True
  
    #dizcli['daemonize'] = not args.no_daemon
    #del dizcli['no_daemon']
  
  logger.debug("dizcli: %s" %dizcli)
  return dizcli

from sogbotmot import container
from sogbotmot import parse as parser

def parsestart(dizcli): 

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
