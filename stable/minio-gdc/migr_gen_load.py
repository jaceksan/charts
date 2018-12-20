#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2007-2019, GoodData(R) Corporation. All rights reserved

from s3 import S3

region = 'us-east-1'
aws_access_key_id = 'vertica_eon_k1234567'
aws_secret_access_key = 'vertica_eon_k1234567_secret1234567890123'
s3_bucket_src = 'test_src'
s3_bucket_tgt = 'test_tgt'

# TODO - consider to implement test case for migration use case
# write/read/delete many files per second and meanwhile migrate the bucket

def main():
    try:
        s3 = S3(region, aws_access_key_id, aws_secret_access_key, s3_bucket_src)
    except Exception as e:
        print('error connect to s3 src bucket: {}'.format(str(e)))
        raise


if __name__ == "__main__":
    main()
