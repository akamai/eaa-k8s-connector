#!/bin/bash

if [ ! -z $1 ] ; then
  dkr_tag="akamai/eaa-k8s-connector:$1"
  echo "Should we build tag: $1"
  read reply
  docker build --force-rm -t $dkr_tag . && \
  docker push $dkr_tag
else
  echo "no tag given .. use $0 <tag>"
fi