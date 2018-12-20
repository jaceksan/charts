#!/usr/bin/env bash

export NAMESPACE=minio

helm del --purge minio-cluster-1

# If corrupted
helm list --namespace ${NAMESPACE}
kubectl get all --namespace ${NAMESPACE} -l release=minio-cluster-1

kubectl delete pods,services,secrets,configmaps,persistentvolumeclaims,statefulsets.apps --namespace ${NAMESPACE} -l release=minio-cluster-1
kubectl delete persistentvolumes --namespace ${NAMESPACE} -l app=minio

kubectl delete pvc export-minio-cluster-1-0 --namespace ${NAMESPACE}
kubectl delete pvc export-minio-cluster-1-1 --namespace ${NAMESPACE}
kubectl delete pvc export-minio-cluster-1-2 --namespace ${NAMESPACE}
kubectl delete pvc export-minio-cluster-1-3 --namespace ${NAMESPACE}

kubectl delete -f gdc-pv-ii.yaml --namespace ${NAMESPACE}

clusterExec.py -m ii-k8s-worker{01..02} -- 'sudo rm -rf /mnt/minio1 /mnt/minio2'
