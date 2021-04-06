#!/bin/bash
# =================================================================
#
# Copyright (c) 2021 Government of Canada
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# =================================================================

BASEDIR=/data/web/geomet-mapproxy-nightly
MAPPROXY_GITREPO="https://github.com/piensa/mapproxy.git -b dimensions"
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
