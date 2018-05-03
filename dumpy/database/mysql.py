import logging
import os
import tempfile
import time

import dumpy

logger = logging.getLogger("dumper")


class MySQLDumpError(Exception):
    pass


class MysqlBackup(dumpy.base.BackupBase):

    def parse_config(self):
        super(MysqlBackup, self).parse_config()

        section = 'database %s' % (self.db)
        self.name = self._get_option_value(self.config, section, 'name')
        self.user = self._get_option_value(self.config, section, 'user')
        self.password = self._get_option_value(self.config, section, 'password')
        self.host = self._get_option_value(self.config, section, 'host')
        self.port = self._get_option_value(self.config, section, 'port', 'int')

        self.binary = self._get_option_value(self.config, 'mysqldump options',
                                             'path')
        self.flags = self._get_option_value(self.config, 'mysqldump options',
                                            'flags')

    def get_flags(self):
        flags = '%s' % (self.flags)
        if self.user:
            flags += ' -u %s' % (self.user)
        if self.password:
            flags += ' -p%s' % (self.password)
        if self.host:
            flags += ' -h %s' % (self.host)
        if self.port:
            flags += ' -P %d' % (self.port)
        return flags

    def backup(self):
        self.parse_config()
        tmp_file = tempfile.NamedTemporaryFile()

        cmd = '%(binary)s %(flags)s %(database)s > %(file)s' % ({
            'binary': self.binary,
            'flags': self.get_flags(),
            'database': self.name,
            'file': tmp_file.name,
        })
        logger.info('%s - Command: %s' % (self.db, cmd))
        start = time.time()
        retval = os.system(cmd)
        end = time.time() - start

        if retval == 0:
            prom_metrics = {
                "task": self.__class__.__name__,
                "spent_time": end,
                "works": True
            }
        else:
            prom_metrics = {
                "task": self.__class__.__name__,
                "spent_time": end,
                "works": False
            }
            logger.warning("The return value of command: %s is not zero. The "
                           "returned value is: %s" % (cmd, str(retval)))
        dumpy.base.PROMETHEUS_MONIT_STATUS[self.db].append(prom_metrics)
        return tmp_file
