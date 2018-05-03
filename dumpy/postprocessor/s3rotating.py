import logging
import time

try:
    import boto
except ImportError:
    boto = None
else:
    from boto.s3.key import Key
    from boto.s3.connection import S3Connection

import dumpy

logger = logging.getLogger("dumper")


class S3Rotating(dumpy.base.PostProcessBase):
    """
    A post processor that purge old dumps on S3
    This only works when S3Copy have db_name_dir turned on
    """

    def __init__(self, db):
        self.db = db

    def parse_config(self):
        super(S3Rotating, self).parse_config()
        self.access_key = self._get_option_value(self.config, 'S3Rotating '
                                                              'options',
                                                 'access_key')
        self.secret_key = self._get_option_value(self.config, 'S3Rotating '
                                                              'options',
                                                 'secret_key')
        self.bucket = self._get_option_value(self.config, 'S3Rotating options',
                                             'bucket')
        self.prefix = self._get_option_value(self.config, 'S3Rotating options',
                                             'prefix')
        self.number = int(self._get_option_value(self.config, 'S3Rotating '
                                                              'options',
                                                 'number'))
        if not self.prefix.endswith('/'):
            self.prefix += '/'

    def process(self, file):
        if boto is None:
            raise Exception(
                "You must have boto installed before using S3 support.")

        self.parse_config()
        start = time.time()
        conn = S3Connection(self.access_key, self.secret_key)
        bucket = conn.get_bucket(self.bucket)
        bucket_data = bucket.get_all_keys()

        if len(bucket_data) <= self.number:
            logger.info("The amount of backups for db %s was not reached to "
                        "be deleted." % (self.db))
            works = True
        else:
            bucket_data.sort(reverse=False, key=lambda i: i.last_modified)
            for i in range(0, self.number):
                bucket_data.pop()
            for file in bucket_data:
                try:
                    logger.info('Deleting file %s' % file.name)
                    bucket.delete_key(key_name=file.name)
                    logger.info('Key %s deleted.' % file.name)
                    works = True
                except BaseException:
                    logger.error('Error deleting key %s' % file.name)
                    works = False
        end = time.time() - start
        prom_metrics = {
            "task": self.__class__.__name__,
            "spent_time": end,
            "works": works
        }
        dumpy.base.PROMETHEUS_MONIT_STATUS[self.db].append(prom_metrics)
        return file
