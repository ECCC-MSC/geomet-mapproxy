[![Build Status](https://github.com/ECCC-MSC/geomet-mapproxy/workflows/flake8%20%E2%9A%99%EF%B8%8F/badge.svg)](https://github.com/ECCC-MSC/geomet-mapproxy/actions)

# geomet-mapproxy

## Overview

MSC GeoMet MapProxy configuration management and orchestration

## Installation

### Requirements
- Python 3
- [virtualenv](https://virtualenv.pypa.io/)

### Dependencies
Dependencies are listed in [requirements.txt](requirements.txt). Dependencies
are automatically installed during geomet-mapproxy installation.

### Installing geomet-mapproxy
```bash
# setup virtualenv
python3 -m venv --system-site-packages geomet-mapproxy
cd geomet-mapproxy
source bin/activate

# clone codebase and install
git clone https://github.com/ECCC-MSC/geomet-mapproxy.git
cd geomet-mapproxy
python3 setup.py build
python3 setup.py install

# configure environment
cp geomet-mapproxy.env dev.env
vi dev.env # edit paths accordingly
. dev.env
```

## Running

```bash
# create default cache directory
geomet-mapproxy cache create

# initialize default MapProxy configuration
geomet-mapproxy config create

# start MapProxy
mapproxy-util serve-develop $GEOMET_MAPPROXY_CONFIG -b 0.0.0.0:8000

# manage configuration and cache

# update specific layers from WMS endpoint (default)
geomet-mapproxy config update --layers=GDPS.ETA_TT,RADAR_1KM_RRAI

# update all layers from WMS endpoint (default)
geomet-mapproxy config update

# update specific layers from mapfile on disk
geomet-mapproxy config update --layers=GDPS.ETA_TT,RADAR_1KM_RRAI --mode=mapfile

# update all layers from mapfile on disk
geomet-mapproxy config update

# update specific layers from Capabilities XML file on disk
geomet-mapproxy config update --layers=GDPS.ETA_TT,RADAR_1KM_RRAI --mode=xml

# update all layers from Capabilities XML file on disk
geomet-mapproxy config update --mode=xml

# delete cache for specific layers
geomet-mapproxy cache clean --layers=GDPS.ETA_TT,RADAR_1KM_RRAI

# delete cache for specific layers, bypassing confirmation
geomet-mapproxy cache clean --layers=GDPS.ETA_TT,RADAR_1KM_RRAI --force
```

## Development

### Running Tests

```bash
# install dev requirements
pip3 install -r requirements-dev.txt

# run tests like this:
python3 geomet_mapproxy/tests/run_tests.py

# or this:
python3 setup.py test
```

## Releasing

```bash
python3 setup.py sdist bdist_wheel --universal
twine upload dist/*
```

### Code Conventions

* [PEP8](https://www.python.org/dev/peps/pep-0008)

### Bugs and Issues

All bugs, enhancements and issues are managed on [GitHub](https://github.com/ECCC-MSC/geomet-mapproxy/issues).

## Contact

* [Tom Kralidis](https://github.com/tomkralidis)
