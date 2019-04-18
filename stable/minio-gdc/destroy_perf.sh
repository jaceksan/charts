#!/usr/bin/env bash

export NAMESPACE=minio

helm del --purge minio-4node-200g-c01
helm del --purge minio-4node-200g-c02
kubectl delete -f custom_ingress_nginx.yaml -n ${NAMESPACE}

###################################
# If corrupted
helm list --namespace ${NAMESPACE}
kubectl get all --namespace ${NAMESPACE} -l release=minio-4node-200g-c01

kubectl delete pods,services,secrets,configmaps,persistentvolumeclaims,statefulsets.apps --namespace ${NAMESPACE} -l release=minio-4node-200g-c01
kubectl delete persistentvolumes --namespace ${NAMESPACE} -l app=minio
# If corrupted
###################################

kubectl delete pvc export-minio-4node-200g-c01-0 --namespace ${NAMESPACE}
kubectl delete pvc export-minio-4node-200g-c01-1 --namespace ${NAMESPACE}
kubectl delete pvc export-minio-4node-200g-c01-2 --namespace ${NAMESPACE}
kubectl delete pvc export-minio-4node-200g-c01-3 --namespace ${NAMESPACE}
kubectl delete pvc export-minio-4node-200g-c02-0 --namespace ${NAMESPACE}
kubectl delete pvc export-minio-4node-200g-c02-1 --namespace ${NAMESPACE}
kubectl delete pvc export-minio-4node-200g-c02-2 --namespace ${NAMESPACE}
kubectl delete pvc export-minio-4node-200g-c02-3 --namespace ${NAMESPACE}

kubectl delete -f gdc-pv-perf.yaml --namespace ${NAMESPACE}

clusterExec.py -m perf-k8s-worker{01..08} -- 'sudo time rm -rf /mnt/minio1'
