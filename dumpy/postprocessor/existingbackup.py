import logging
from datetime import datetime

import dumpy

try:
    import boto
except ImportError:
    boto = None
else:
    from boto.s3.key import Key
    from boto.s3.connection import S3Connection

logger = logging.getLogger("dumper")


class CheckS3ExistingBackup(dumpy.base.PostProcessBase):
    """
    This class checks on S3 if a file pattern exists.
    If exists, a flag is set and the backup is stopped
    """

    def __init__(self, db):
        self.db = db

    def parse_config(self):
        super(CheckS3ExistingBackup, self).parse_config()

        self.pattern = self._get_option_value(self.config,
                                              'S3CheckExistingFile',
                                              'pattern')
        self.access_key = self._get_option_value(self.config, 'S3 options',
                                                 'access_key')
        self.secret_key = self._get_option_value(self.config, 'S3 options',
                                                 'secret_key')
        self.bucket = self._get_option_value(self.config, 'S3 options',
                                             'bucket')
        self.prefix = self._get_option_value(self.config, 'S3 options',
                                             'prefix')
        if not self.prefix.endswith('/'):
            self.prefix += '/'

    def process(self, file):
        self.parse_config()
        p = datetime.now().strftime(self.pattern)

        conn = S3Connection(self.access_key, self.secret_key)
        bucket = conn.get_bucket(self.bucket)
        bucket_data = bucket.get_all_keys()
        bucket_data.sort(reverse=False, key=lambda i: i.last_modified)

        for file in bucket_data:
            if p in file.name:
                dumpy.base.FILE_EXISTS_ON_S3 = True
                logger.info("%s - %s - Found a backup file %s on S3 with "
                            "pattern %s" % (self.db,
                                            self.__class__.__name__,
                                            file.name,
                                            p))
                break

        return file
