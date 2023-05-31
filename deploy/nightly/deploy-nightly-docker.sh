#!/bin/bash
# =================================================================
#
# Copyright (c) 2023 Government of Canada
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
