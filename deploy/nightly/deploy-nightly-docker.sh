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

BASEDIR=/data/web/geomet-mapproxy-nightly
GEOMET_MAPPROXY_GITREPO=https://github.com/ECCC-MSC/geomet-mapproxy.git
DAYSTOKEEP=7
GEOMET_MAPPROXY_URL=https://geomet-dev-21-nightly.cmc.ec.gc.ca/geomet-mapproxy

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
mkdir $NIGHTLYDIR && cd $NIGHTLYDIR

echo "Cloning geomet-mapproxy repository"
git clone $GEOMET_MAPPROXY_GITREPO . -b main --depth=1

echo "Stopping/building/starting Docker setup"
docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml build --no-cache
docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml down
docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml up -d

cat > geomet-mapproxy-nightly.conf <<EOF
<Location /geomet-mapproxy>
  ProxyPass  http://localhost:5091
  ProxyPassReverse http://localhost:5091
  Header set Access-Control-Allow-Origin "*"
  Header set Access-Control-Allow-Headers "Origin, X-Requested-With, Content-Type, Accept, Authorization"
  Require all granted
</Location>
EOF

cd ..

ln -s $NIGHTLYDIR latest
