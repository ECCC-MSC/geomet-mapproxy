# =================================================================
#
# Author: Tom Kralidis <tom.kralidis@ec.gc.ca>
#
# Copyright (c) 2023 Tom Kralidis
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation
# files (the "Software"), to deal in the Software without
# restriction, including without limitation the rights to use,
# copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following
# conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR
# OTHER DEALINGS IN THE SOFTWARE.
#
# =================================================================

import logging
import os


LOGGER = logging.getLogger(__name__)

LOGGER.info('Fetching environment variables')

GEOMET_MAPPROXY_LOGGING_LOGLEVEL = os.getenv(
    'GEOMET_MAPPROXY_LOGGING_LOGLEVEL', 'ERROR')

GEOMET_MAPPROXY_LOGGING_LOGFILE = os.getenv(
    'GEOMET_MAPPROXY_LOGGING_LOGFILE', None)

GEOMET_MAPPROXY_CACHE_DATA = os.getenv('GEOMET_MAPPROXY_CACHE_DATA', None)
GEOMET_MAPPROXY_CACHE_WMS = os.getenv('GEOMET_MAPPROXY_CACHE_WMS', None)
GEOMET_MAPPROXY_CACHE_MAPFILE = os.getenv('GEOMET_MAPPROXY_CACHE_MAPFILE',
                                          None)
GEOMET_MAPPROXY_CACHE_XML = os.getenv('GEOMET_MAPPROXY_CACHE_XML', None)
GEOMET_MAPPROXY_CACHE_CONFIG = os.getenv('GEOMET_MAPPROXY_CACHE_CONFIG', None)
GEOMET_MAPPROXY_CONFIG = os.getenv('GEOMET_MAPPROXY_CONFIG', None)
GEOMET_MAPPROXY_URL = os.getenv('GEOMET_MAPPROXY_URL', None)
GEOMET_MAPPROXY_TMP = os.getenv('GEOMET_MAPPROXY_TMP', '/tmp')

if None in (GEOMET_MAPPROXY_CACHE_DATA, GEOMET_MAPPROXY_CONFIG,
            GEOMET_MAPPROXY_CACHE_CONFIG, GEOMET_MAPPROXY_URL,
            GEOMET_MAPPROXY_TMP):
    msg = 'Environment variables not set'
    LOGGER.error(msg)
    raise EnvironmentError(msg)
