#!/bin/bash

unset KUBECONFIG

cd .. && docker build -f docker/Dockerfile.latest \
             -t DISABLED/maliang .

docker tag DISABLED/maliang DISABLED/maliang:$(date +%y%m%d)