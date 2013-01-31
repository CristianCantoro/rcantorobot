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
import re
import os
import sys
import logging

from sogbotmod import tuct

logger = logging.getLogger('sogbot.sbglobal')

# ***** application (meta)data *****
APPNAME = 'sogbot'

VERSION = '0.1'

BASE_DIR = os.path.dirname(os.path.normpath(os.path.realpath(sys.argv[0])))

CURR_DIR = os.path.abspath(os.path.normpath(os.getcwd()))

logger.debug("BASE_DIR: %s" %BASE_DIR)
logger.debug("CURR_DIR: %s" %CURR_DIR)

DESCRIPTION="""sogbot description"""

EPILOG = """Copyright 2013 - Cristian Consonni.
This program is free software; you may redistribute it under the terms of
the GNU General Public License version 3 or (at your option) any later version. 
This program has absolutely no warranty."""

SOGBOT = tuct.Tuct(
        APPNAME = APPNAME,

        VERSION = VERSION,
        
        BASE_DIR = BASE_DIR,
        
        DESCRIPTION = DESCRIPTION,

        EPILOG = EPILOG 
       )
# ***** END application (meta)data *****
