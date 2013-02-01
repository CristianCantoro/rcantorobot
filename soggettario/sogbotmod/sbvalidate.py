#! /usr/bin/python
# -*- coding: UTF-8 -*-

import re
import os
import sys

from validate import ValidateError
from validate import Validator

import logging
logger = logging.getLogger('sogbot.validate')

logger.setLevel(logging.WARNING)

from ASregex import RegexDict
from sbglobal import SOGBOT

CONFIGSPEC_DIR = AUTOSEND['CONFIGSPEC_DIR']

regexes = RegexDict(CONFIGSPEC_DIR)

MAILREGEX = regexes.get_regex('mail')

email_re = re.compile(MAILREGEX, re.VERBOSE)

def email_check(value):
    #print "email: %s" %value
    if isinstance(value, list):
      msg = 'A list was passed when an email address was expected'
      logger.error(msg)
      raise ValidateError(msg)
      
    if email_re.match(value) is None:
      msg = '"%s" is not a valid email address' % value
      raise ValidateError(msg)
      
    return value

def email_list_check(value):
    logger.debug("value: %s" %value)
    lista = value.strip().split(",")
    lista = [e for e in lista if e]
    logger.debug("lista: %s" %lista)
    lista_corr = []
    for e in lista:
      c = email_check(e.strip())
      if c is not None:
	lista_corr.append(c)
    logger.debug("lista_corr: %s" %lista_corr)
    return lista_corr


def writepath_check(value):
    value = os.path.abspath(os.path.normpath(value))
    #print "path: %s" %value
    if isinstance(value, list):
      msg = 'A list was passed when a path with write permission was expected'
      logger.error(msg)
      raise ValidateError(msg)
      
    #print "type: ", type(value)
    #print os.path.exists(value)
    #print "qua"
    logger.debug(value)
    if not os.path.exists(value):
      msg = '"%s" is not a valid path' % value
      
      logger.error(msg)
      raise ValidateError(msg)
      
    elif not os.access(value, os.W_OK):
      msg = 'User has not the valid permissions to write: "%s"' % value
      logger.error(msg)
      
      raise ValidateError(msg)
    return value

def readpath_check(value):
    value = os.path.abspath(os.path.normpath(value))
    #print "path: %s" %value
    if isinstance(value, list):
      msg = 'A list was passed when a path with read permission was expected'
      logger.error(msg)
      raise ValidateError(msg)
      
    #print "type: ", type(value)
    #print os.path.exists(value)
    
    logger.debug(value)
    if not os.path.exists(value):
      msg = '"%s" is not a valid path' % value
      logger.error(msg)
      
      raise ValidateError(msg)
      
    elif not os.access(value, os.R_OK):
      msg = 'User has not the valid permissions to read: "%s"' % value
      logger.error(msg)
      raise ValidateError(msg)
            
    return value

def readfile_check(value):
    value = os.path.abspath(os.path.normpath(value))
    #print "path: %s" %value
    if isinstance(value, list):
      msg = 'A list was passed when a path with read permission was expected'
      logger.error(msg)
      raise ValidateError(msg)
      
    #print "type: ", type(value)
    #print os.path.exists(value)
    
    logger.debug(value)
    if not os.path.exists(value):
      msg = '"%s" is not a valid path' % value
      raise ValidateError(msg)
      
    elif not os.path.isfile(value):
      msg = '"%s" is not a regular file:' % value
      raise ValidateError(msg)
      
    elif not os.access(value, os.R_OK):
      msg = 'User has not the valid permissions to read: "%s"' % value
      raise ValidateError(msg)
      

    return value

SERVERREGEX = regexes.get_regex('server')

server_re = re.compile(SERVERREGEX, re.VERBOSE)

def smtpserver_check(value):
    #print "path: %s" %value
    if isinstance(value, list):
      msg = 'A list was passed when a server name was expected'
      raise ValidateError(msg)
      
    if server_re.match(value) is None:
      msg = '"%s" is not a valid server name' % value
      raise ValidateError(msg)
      
    return value

LOGLEVELS = {'debug': logging.DEBUG,
             'info': logging.INFO,
             'warning': logging.WARNING,
             'error': logging.ERROR,
             'critical': logging.CRITICAL
            }


def loglevel_check(value):
    #print "path: %s" %value
    if isinstance(value, list):
      msg = 'A list was passed when a log level was expected'
      logger.warning(msg)
      raise ValidateError(msg)
    level = LOGLEVELS.get(lower(value), logging.NOTSET)
    print level
    return level

HOURREGEX = regexes.get_regex('hour')

hour_re = re.compile(HOURREGEX, re.VERBOSE)

MAXHOUR = 23

def hour_check(value):
  logger.debug("hour: %s" %value)
  if isinstance(value, list):
    msg = 'A list was passed when an hour string was expected'
    logger.error(msg)
    raise ValidateError(msg)
    
    
  if hour_re.match(value) != None:
    orario = hour_re.match(value).group(0)
    lis = orario.split(":")
    ora = int(lis[0])
    logger.debug("orario: %s - ora: %s" %(orario, ora))
    value = orario
    if ora > MAXHOUR:
      raise OverflowError
      

    return orario
    
  else:
    msg = '"%s" does not contain a valid hour' % value
    logger.error(msg)
    raise ValidateError(msg)
    
  
  return value