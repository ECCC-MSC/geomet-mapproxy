#!/bin/bash
# =================================================================
#
# Author: Kevin Ngai <kevin.ngai@ec.gc.ca>
#
# Copyright (c) 2023 Kevin Ngai
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

echo "START /entrypoint.sh"

set +e

# gunicorn env settings with defaults
CONTAINER_NAME="geomet-mapproxy-nightly"
CONTAINER_HOST=${CONTAINER_HOST:=0.0.0.0}
CONTAINER_PORT=${CONTAINER_PORT:=80}
WSGI_WORKERS=${WSGI_WORKERS:=2}
WSGI_WORKER_TIMEOUT=${WSGI_WORKER_TIMEOUT:=900}

# create default cache directory
echo "Creating default cache directory for geomet-mapproxy"
geomet-mapproxy cache create

# create initial config
echo "Creating initial config for geomet-mapproxy"
geomet-mapproxy config create

# pass in GEOMET_MAPPROXY env variables to /etc/environment so they are available to cron
env | grep ^GEOMET_MAPPROXY >> /etc/environment
# startup cron jobs (builds mapfile at schedule cron settings)
service cron start

# startup geomet-mapproxy on gunicorn
echo "Starting gunicorn for name=${CONTAINER_NAME} on ${CONTAINER_HOST}:${CONTAINER_PORT} with ${WSGI_WORKERS} workers. Access logs output to ${GUNICORN_GEOMET_MAPPROXY_ACCESSLOG} and error logs to ${GUNICORN_GEOMET_MAPPROXY_ERRORLOG}"
gunicorn --workers ${WSGI_WORKERS} \
    --name=${CONTAINER_NAME} \
    --bind ${CONTAINER_HOST}:${CONTAINER_PORT} \
    --chdir $BASEDIR/geomet_mapproxy wsgi:application \
    --reload \
    --timeout ${WSGI_WORKER_TIMEOUT} \
    --access-logfile $GUNICORN_GEOMET_MAPPROXY_ACCESSLOG \
    --error-logfile $GUNICORN_GEOMET_MAPPROXY_ERRORLOG

echo "END /entrypoint.sh"
