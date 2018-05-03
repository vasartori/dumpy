import datetime
import logging
import os
import shutil

import dumpy

logger = logging.getLogger("dumper")

class PrependDatabaseName(dumpy.base.PostProcessBase):
    """
    A post procesor that renames the file by prepending the database name to
    the existing file name.
    """
    def __init__(self, db):
        self.db = db

    def parse_config(self):
        super(PrependDatabaseName, self).parse_config()

    def process(self, file):

        self.parse_config()

        if dumpy.base.FILE_EXISTS_ON_S3:
            logger.info("%s - %s - Found a backup on S3. Skiping Prepend "
                        "Database Name" %(
                self.db,
                self.__class__.__name__))
            return file

        if False in dumpy.base.FAIL_STATE:
            logger.error("%s - %s - Found a previous error. Stopping here." %
                         (self.db,
                          self.__class__.__name__))
            return file

        dir = os.path.dirname(file.name)
        base, ext = os.path.splitext(os.path.basename(file.name))

        new_file_name = '%s/%s-%s%s' % (dir, self.db, base, ext)

        shutil.copy(file.name, new_file_name)
        logger.info('%s - %s - Copying %s to %s' % (self.db, self.__class__.__name__, file.name, new_file_name))
        new_file = open(new_file_name)
        file.close()

        return new_file

