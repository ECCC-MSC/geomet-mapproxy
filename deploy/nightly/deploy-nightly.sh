#!/bin/bash
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

BASEDIR=/data/web/geomet-mapproxy-nightly
MAPPROXY_GITREPO=https://github.com/ECCC-MSC/mapproxy.git
GEOMET_MAPPROXY_GITREPO=https://github.com/ECCC-MSC/geomet-mapproxy.git
DAYSTOKEEP=7
GEOMET_MAPPROXY_URL=https://geomet-dev-03-nightly.cmc.ec.gc.ca/geomet-mapproxy-nightly/latest/service

cat >$BASEDIR/geomet-mapproxy-nightly.env <<EOL
export GEOMET_MAPPROXY_LOGGING_LOGLEVEL=DEBUG
export GEOMET_MAPPROXY_LOGGING_LOGFILE=stdout
export GEOMET_MAPPROXY_CACHE_DATA=$BASEDIR/cache_data
export GEOMET_MAPPROXY_CACHE_WMS=https://geo.wxod-dev.cmc.ec.gc.ca/geomet
export GEOMET_MAPPROXY_CACHE_MAPFILE=/opt/geomet/conf/geomet-en.map
export GEOMET_MAPPROXY_CACHE_XML=/opt/geomet/conf/geomet-wms-1.3.0-capabilities-en.xml
export GEOMET_MAPPROXY_URL=$GEOMET_MAPPROXY_URL
export GEOMET_MAPPROXY_CONFIG=$BASEDIR/geomet-mapproxy-config.yml
export GEOMET_MAPPROXY_CACHE_CONFIG=$BASEDIR/latest/geomet-mapproxy/deploy/default/geomet-mapproxy-cache-config.yml
export GEOMET_MAPPROXY_TMP=/tmp
EOL

# you should be okay from here

. $BASEDIR/geomet-mapproxy-nightly.env

DATETIME=`date +%Y%m%d`
TIMESTAMP=`date +%Y%m%d.%H%M`
NIGHTLYDIR=geomet-mapproxy-$TIMESTAMP

echo "Deleting nightly builds > $DAYSTOKEEP days old"

cd $BASEDIR

for f in `find . -type d -name "geomet-mapproxy-20*"`
do
    DATETIME2=`echo $f | awk -F- '{print $3}' | awk -F. '{print $1}'`
    let DIFF=(`date +%s -d $DATETIME`-`date +%s -d $DATETIME2`)/86400
    if [ $DIFF -gt $DAYSTOKEEP ]; then
        rm -fr $f
    fi
done

rm -fr latest
echo "Generating nightly build for $TIMESTAMP"
python3.6 -m venv --system-site-packages $NIGHTLYDIR && cd $NIGHTLYDIR
source bin/activate
git clone $MAPPROXY_GITREPO
cd mapproxy
python3 setup.py install
cd ..
git clone $GEOMET_MAPPROXY_GITREPO
cd geomet-mapproxy
pip3 install -r requirements.txt
python3 setup.py install
cd ..

cd ..

ln -s $NIGHTLYDIR latest

geomet-mapproxy cache create
geomet-mapproxy config create
