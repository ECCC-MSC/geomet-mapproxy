# every minute, refresh geomet-mapproxy config with GeoMet-Weather via GeoMet-Weather nightly WMS
* * * * * /usr/local/bin/geomet-mapproxy config update
# every day at 0300h, clear cache
0 3 * * * /usr/local/bin/geomet-mapproxy cache clean --layers=all --force
