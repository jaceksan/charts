#!/usr/bin/env bash

wget https://dl.minio.io/client/mc/release/linux-amd64/mc
chmod 775 mc

export NAMESPACE=minio

helm list --namespace ${NAMESPACE}
kubectl get all --namespace ${NAMESPACE} -l release=minio-4node-200g-c01

kubectl describe svc minio-4node-200g-c01 --namespace minio | grep Endpoints:

export POD_IP=172.16.0.49
export PORT=9000

./mc config host add minio-4node-200g-c01 http://${POD_IP}:${PORT} \
  vertica_eon_k1234567 vertica_eon_k1234567_secret1234567890123 S3v4

./mc config host add minio-4node-200g-c02 http://${POD_IP}:${PORT} \
  vertica_eon_k1234567 vertica_eon_k1234567_secret1234567890123 S3v4

./mc admin info minio-4node-200g-c01
./mc ls minio-4node-200g-c01

./mc mb minio-4node-200g-c02/test2
./mc mirror minio-4node-200g-c01/test minio-4node-200g-c02/test2

# Heal certain pod
./mc config host add minio-4node-200g-c01 http://perf-k8s-worker01.int.na.prodgdc.com:32080 \
  vertica_eon_k1234567 vertica_eon_k1234567_secret1234567890123 S3v4
./mc admin heal --recursive --dry-run minio-4node-200g-c01/vertica
./mc admin heal --recursive minio-4node-200g-c01/vertica

# Check for latest version of Minio
curl -s https://api.github.com/repos/minio/minio/releases/latest | jq '.tag_name'


#################################################################
# Explore / modify ETCD records
export ETCDCTL_API=3
etcdctl --endpoints perf-k8s-master01.int.na.prodgdc.com:2379 get --prefix /skydns

# Delete key
etcdctl --endpoints perf-k8s-master01.int.na.prodgdc.com:2379 \
  del /skydns/com/gdc/k8s/minio/test/172.19.32.4
etcdctl --endpoints perf-k8s-master01.int.na.prodgdc.com:2379 \
  del /skydns/com/gdc/k8s/minio/test2/172.17.48.8


# TODO - think about to modify IP to redirect bucket to different Minio cluster
# would have to be done in sync with "mc -w mirror" operation
etcdctl --endpoints perf-k8s-master01.int.na.prodgdc.com:2379 \
  put /skydns/com/gdc/k8s/minio/test/172.19.32.4 \
  "{\"host\":\"172.17.48.8\",\"port\":9000,\"ttl\":30,\"creationDate\":\"2019-01-10T11:21:08.03322357Z\"}"


