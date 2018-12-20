#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2007-2016, GoodData(R) Corporation. All rights reserved

import boto
import boto.s3.connection


class S3BucketDoesNotExistException(Exception):
    """
    Bucket with the specified name does not exist

    """

    def __init__(self, error_message):
        super(S3BucketDoesNotExistException, self).__init__()
        self.error_message = error_message

    def __str__(self):
        return "Error: message={0}".format(self.error_message)


class S3ConnectionException(Exception):
    """
    Connection to S3 could not be established

    """
    def __init__(self, error_message):
        super(S3ConnectionException, self).__init__()
        self.error_message = error_message

    def __str__(self):
        return "Error: message={0}".format(self.error_message)


class S3KeyException(Exception):
    """
    A key in the S3 bucket could not be created

    """
    def __init__(self, error_message):
        super(S3KeyException, self).__init__()
        self.error_message = error_message

    def __str__(self):
        return "Error: message={0}".format(self.error_message)


class S3Exception(Exception):
    """
    File could not be uploaded to S3

    """
    def __init__(self, action, error_code, error_message):
        super(S3Exception, self).__init__()
        self.action = action
        self.error_code = error_code
        self.error_message = error_message

    def __str__(self):
        return 'Error: action="{0}" code="{1}" message="{2}"'.format(self.action, self.error_code, self.error_message)


class S3(object):
    def __init__(self, region_name, aws_access_key_id, aws_secret_access_key, bucket=None, path=None, validate=True):
        self._connection = self._connect(region_name, aws_access_key_id, aws_secret_access_key)
        self._validate = validate
        self._bucket = self._get_bucket(bucket) if bucket else None
        self._bucket_name = bucket
        self._path = ''
        if path is not None:
            self.set_path(path)

    @staticmethod
    def _connect(region_name, aws_access_key_id, aws_secret_access_key, host=None):
        """
        Establish a connection to S3

        :param region_name: name of the region to connect to
        :param aws_access_key_id: the access key to S3
        :param aws_secret_access_key: the secret access key to S3
        :return: S3 connection object
        """
        try:
            return boto.s3.connect_to_region(
                host=host,
                region_name=region_name,
                aws_access_key_id=aws_access_key_id,
                aws_secret_access_key=aws_secret_access_key,
                is_secure=True,
                calling_format=boto.s3.connection.OrdinaryCallingFormat()
            )

        except Exception as e:
            raise S3ConnectionException(e)

    def _get_bucket(self, bucket):
        """
        Checks if the bucket exists and returns its object instance

        :param bucket: name of the bucket
        :return: bucket object
        """
        if self._validate:
            if self.check_bucket_existence(bucket):
                return self._connection.get_bucket(bucket)
            else:
                raise S3BucketDoesNotExistException('Bucket {0} does not exist'.format(bucket))
        else:
            return self._connection.get_bucket(bucket, validate=self._validate)

    def check_bucket_existence(self, bucket):
        """
        Checks if the given bucket exists

        :param bucket: name of the bucket
        :return: True if the bucket exist, False otherwise
        """
        return self._connection.lookup(bucket) is not None

    def set_bucket(self, bucket):
        """
        Sets the S3 bucket

        :param bucket: name of the bucket
        :return:
        """
        self._bucket = self._get_bucket(bucket)

    def set_path(self, *directories):
        """
        Sets the S3 path

        :param directories: complete path or separate directories (in the right order)
        :return:
        """
        path = '/'.join(directory for directory in directories)

        self._path = '{0}/'.format(path.rstrip('/')) if path.rstrip() != '' else path

    def list_contents(self):
        """
        Lists information about keys (files) in the given bucket path

        :return:
        """
        return dict([(self._get_file_name(key.name), {'timestamp': key.last_modified,
                                                      'md5': key.etag[1:-1],
                                                      'size': key.size,
                                                      'name': key.name})
                     for key in self._bucket.list(self._path)])

    def check_file_existence(self, file_name):
        """
        Checks if the given file exists

        :param file_name: name of the key (file) to be checked for
        :return: True if the file exist, False otherwise
        """
        key = '{0}{1}'.format(self._path, file_name)

        return self._bucket.get_key(key) is not None

    def _create_key(self, file_name, overwrite=False):
        """
        Creates a new key (file) in the given bucket path

        :param file_name: name of the key (file) to be created
        :param overwrite: indication if an existing key (file) may be overwritten
        :return: key object
        """
        key = '{0}{1}'.format(self._path, file_name)

        if not overwrite and self.check_file_existence(file_name):
            raise S3KeyException('File {0} already exists'.format(key))
        else:
            try:
                return self._bucket.new_key(key)
            except boto.exception.S3CreateError as e:
                raise S3Exception('create key', e.status, '{0}/{1}'.format(e.reason, e.message))

    @staticmethod
    def _get_file_name(file_name_with_path):
        """
        Parses the file name from the file name with path

        :param file_name_with_path: name of the file with path
        :return: file name
        """
        return file_name_with_path.split('/')[-1]

    def upload_file(self, file_name_with_path, file_name=None, encrypt_key=False, overwrite=False):
        """
        Uploads a file from the given path to S3

        :param file_name_with_path: name of the file with path
        :param file_name: name of the file (optional)
        :param encrypt_key: if True, the file will be encrypted on the server-side by S3
                            and will be stored in an encrypted form while at rest in S3
        :param overwrite: indication if an existing key (file) may be overwritten
        :return:
        """
        key = self._create_key(file_name if file_name else self._get_file_name(file_name_with_path),
                               overwrite=overwrite)

        try:
            key.set_contents_from_filename(file_name_with_path, encrypt_key=encrypt_key)
        except boto.exception.S3ResponseError as e:
            raise S3Exception('upload file', e.status, '{0}/{1}'.format(e.reason, e.message))

    def create_file(self, file_name, contents, encrypt_key=False, overwrite=False):
        """
        Creates a new file with the supplied contents in the given S3 path

        :param file_name: name of the file
        :param contents: content of the file
        :param encrypt_key: if True, the file will be encrypted on the server-side by S3
                            and will be stored in an encrypted form while at rest in S3
        :param overwrite: indication if an existing key (file) may be overwritten
        :return:
        """
        key = self._create_key(file_name, overwrite=overwrite)

        try:
            key.set_contents_from_string(contents, encrypt_key=encrypt_key)
        except boto.exception.S3ResponseError as e:
            raise S3Exception('create file', e.status, '{0}/{1}'.format(e.reason, e.message))

    def _delete_key(self, key):
        """
        Deletes a file from S3 bucket path.
        (By default the bucket method deletes the directory with the last deleted file as well)

        :param key: name of the key with path
        :return:
        """
        try:
            self._bucket.delete_key(key)
        except boto.exception.S3ResponseError as e:
            raise S3Exception('delete file', e.status, '{0}/{1}'.format(e.reason, e.message))

    def delete_file(self, file_name):
        """
        Deletes a file from S3 bucket path.
        (By default the bucket method deletes the directory with the last deleted file as well)

        :param file_name: name of the key (file) to be created
        :return:
        """
        key = '{0}{1}'.format(self._path, file_name)
        self._delete_key(key)

    @staticmethod
    def _get_file(key, target_file_name):
        """
        Download file from S3

        :param key: pointer to a key object
        :param target_file_name: file name with path
        :return:
        """
        try:
            key.get_contents_to_filename(target_file_name)
        except boto.exception.S3ResponseError as e:
            raise S3Exception('get file', e.status, '{0}/{1}'.format(e.reason, e.message))

    def get_file(self, target_path, file_name):
        """
        Download file form S3 bucket

        :param target_path: path the file will be written to
        :param file_name: name of the key (file) to be downloaded
        :return:
        """
        key = '{0}{1}'.format(self._path, file_name)
        target_file_name = '{0}/{1}'.format(target_path.rstrip('/'), file_name)
        self._get_file(self._bucket.get_key(key), target_file_name)

    def get_files(self, target_path):
        """
        Download multiple files form S3 bucket

        :param target_path: path the files will be written to
        :return:
        """
        for key in self._bucket.list(self._path):
            target_file_name = '{0}/{1}'.format(target_path.rstrip('/'), key.name)
            self._get_file(key, target_file_name)

    def _copy_file(self, key, target_bucket, target_file_name, encrypt_key=False):
        """
        Copy file between buckets/keys

        :param key: pointer to a key object
        :param target_bucket:
        :param target_file_name: file name with path
        :param encrypt_key: if True, the file will be encrypted on the server-side by S3
                            and will be stored in an encrypted form while at rest in S3
        :return:
        """
        try:
            key.copy(target_bucket, target_file_name, validate_dst_bucket=self._validate, encrypt_key=encrypt_key)
        except boto.exception.S3ResponseError as e:
            raise S3Exception('copy file', e.status, '{0}/{1}'.format(e.reason, e.message))

    def move_file(self, target_path, file_name, encrypt_key=False):
        """
        Move file inside a bucket

        :param target_path: path the files will be written to
        :param file_name: name of the key (file) to be moved
        :param encrypt_key: if True, the file will be encrypted on the server-side by S3
                            and will be stored in an encrypted form while at rest in S3
        :return:
        """
        key = '{0}{1}'.format(self._path, file_name)
        target_file_name = '{0}/{1}'.format(target_path.rstrip('/'), file_name)
        self._copy_file(self._bucket.get_key(key), self._bucket_name, target_file_name, encrypt_key=encrypt_key)
        self._delete_key(key)

    def move_files(self, target_path, encrypt_key=False):
        """
        Move multiple files inside a bucket

        :param target_path: path the files will be written to
        :param encrypt_key: if True, the file will be encrypted on the server-side by S3
                            and will be stored in an encrypted form while at rest in S3
        :return:
        """
        for key in self._bucket.list(self._path):
            target_file_name = '{0}/{1}'.format(target_path.rstrip('/'), key.name)
            self._copy_file(key, self._bucket_name, target_file_name, encrypt_key=encrypt_key)
            self._delete_key(key.name)
