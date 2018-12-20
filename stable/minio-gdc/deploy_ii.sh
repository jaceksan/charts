#!/usr/bin/env bash

export NAMESPACE=minio

kubectl create --namespace ${NAMESPACE} -f gdc-pv-ii.yaml

export CLUSTER_NAME="minio-cluster-1"
export NODE_PORT=32080
export SERVICE_PORT=9000

# Without federation, NodePort - DEPRECATED
#helm install ../minio/ --name ${CLUSTER_NAME} --namespace ${NAMESPACE} -f gdc-values.yaml \
#  --set service.type=NodePort --set service.nodePort=${NODE_PORT}
# Upgrade example
#helm upgrade ${CLUSTER_NAME} ../minio/ --namespace ${NAMESPACE} -f gdc-values.yaml \
#  --set service.type=NodePort --set service.nodePort=${NODE_PORT}

# Without federation, ingress with default nginx
even
helm upgrade ${CLUSTER_NAME} ../minio/ --namespace ${NAMESPACE} -f gdc-values.yaml \
  --set service.type=ClusterIP --set service.port=${SERVICE_PORT} \
  --set ingress.enabled=true --set ingress.path=/
