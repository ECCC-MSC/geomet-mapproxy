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

# test geomet-mapproxy endpoint
```bash
curl "http://geomet-dev-21.cmc.ec.gc.ca:5091/service?request=GetCapabilities"
# or
curl "https://geomet-dev-21-nightly.cmc.ec.gc.ca/geomet-mapproxy/service?request=GetCapabilities"
```