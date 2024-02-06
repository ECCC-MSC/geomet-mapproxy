# build Docker image
```bash
docker image build -t eccc-msc/geomet-mapproxy:nightly .
```

# (recommended) build Docker image via Docker Compose
```bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml build --no-cache
```

# startup container
```bash
docker compose -f docker/docker-compose.yml -f docker/docker-compose.override.yml up -d
```

# test OGC WMS endpoint
```bash
curl "http://geomet-dev-22.cmc.ec.gc.ca:5091/service?request=GetCapabilities"
# or
curl "https://geomet-dev-22-nightly.cmc.ec.gc.ca/geomet-mapproxy/service?request=GetCapabilities"
```
