import logging
import os
import time

import dumpy

logger = logging.getLogger("dumper")

class Bzip(dumpy.base.PostProcessBase):
    """
    A post processor that bzips the given file and returns it.
    """
    def __init__(self, db):
        self.db = db

    def parse_config(self):
        super(Bzip, self).parse_config()
        self.path = self._get_option_value(self.config, 'Bzip options', 'path')

    def process(self, file):

        self.parse_config()

        if False in dumpy.base.FAIL_STATE:
            logger.error("%s - %s - Found a previous error. Stopping here." %
                         (self.db,
                          self.__class__.__name__))
            return file

        cmd = "%(path)s -f '%(file)s'" % ({'path': self.path, 'file': file.name})
        logger.info('%s - %s - Command: %s' % (self.db, self.__class__.__name__, cmd))
        start = time.time()
        retval = os.system(cmd)
        end = time.time() - start

        new_file = open('%s.bz2' % (file.name))
        file.close()

        if retval == 0:
            prom_metrics = {
                "task": self.__class__.__name__,
                "spent_time": end,
            }
            works = True
        else:
            prom_metrics = {
                "task": self.__class__.__name__,
                "spent_time": end,
            }
            works = False
            logger.warning("The return value of command: %s is not zero. The "
                           "returned value is: %s" % (cmd, str(retval)))
        dumpy.base.FAIL_STATE.append(works)
        dumpy.base.PROMETHEUS_MONIT_STATUS[self.db].append(prom_metrics)
        return new_file
