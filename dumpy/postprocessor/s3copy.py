import logging
import os
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


class S3Copy(dumpy.base.PostProcessBase):
    """
    A post processor that copies the given file to S3.
    """

    def __init__(self, db):
        self.db = db

    def parse_config(self):
        super(S3Copy, self).parse_config()
        self.access_key = self._get_option_value(self.config, 'S3 options',
                                                 'access_key')
        self.secret_key = self._get_option_value(self.config, 'S3 options',
                                                 'secret_key')
        self.bucket = self._get_option_value(self.config, 'S3 options',
                                             'bucket')
        self.prefix = self._get_option_value(self.config, 'S3 options',
                                             'prefix')
        self.db_name_dir = self._get_option_value(self.config, 'S3Copy options',
                                                  'db_name_dir',
                                                  'boolean')
        # Make sure prefix ends with a single forward slash
        if not self.prefix.endswith('/'):
            self.prefix += '/'

    def process(self, file):
        if boto is None:
            raise Exception(
                "You must have boto installed before using S3 support.")

        self.parse_config()

        if dumpy.base.FILE_EXISTS_ON_S3:
            logger.info("%s - %s - Found a backup on S3. Skiping S3 Copy" %(
                self.db,
                self.__class__.__name__))
            return file

        if False in dumpy.base.FAIL_STATE:
            logger.error("%s - %s - Found a previous error. Stopping here." %
                         (self.db,
                          self.__class__.__name__))
            return file

        start = time.time()
        conn = S3Connection(self.access_key, self.secret_key)
        bucket = conn.create_bucket(self.bucket)
        k = Key(bucket)
        if self.prefix and self.db_name_dir is False:
            keyname = '%s%s' % (
                self.prefix,
                os.path.basename(file.name)
            )
        elif self.prefix and self.db_name_dir:
            keyname = '%s%s' % (
                self.prefix,
                '/'.join([self.db, os.path.basename(file.name)])
            )
        elif self.prefix is False and self.db_name_dir:
            keyname = '/'.join([self.db, os.path.basename(file.name)])
        else:
            keyname = os.path.basename(file.name)
        try:
            k.key = keyname
            k.set_contents_from_file(file)
            end = time.time() - start
            works = True
            logger.info('%s - %s - Copying to S3 with key name: %s' % (
                self.db, self.__class__.__name__, keyname))
        except BaseException:
            logger.error('%s - %s - Copying to S3 with key name: %s' % (
                self.db, self.__class__.__name__, keyname))
            end = time.time() - start
            works = False

        prom_metrics = {
            "task": self.__class__.__name__,
            "spent_time": end,
        }
        dumpy.base.FAIL_STATE.append(works)
        dumpy.base.PROMETHEUS_MONIT_STATUS[self.db].append(prom_metrics)
        return file
