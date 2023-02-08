## Building on a M1
```bash
docker build --platform linux/amd64 --tag akamai/eaa-k8s-connector:testing . && \
docker push akamai/eaa-k8s-connector:testing
```