#!/bin/bash
dkr_tag="akamai/eaa-k8s-connector:testing"

kubectl delete -f examples/StatefulSet.yml
docker build --force-rm -t $dkr_tag . && \
docker push $dkr_tag
kubectl apply -f examples/StatefulSet.yml
sleep 2
kubectl get pod eaa-k8s-connector-0 -o wide