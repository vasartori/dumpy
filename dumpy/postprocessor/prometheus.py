import logging

from prometheus_client import Gauge, push_to_gateway, CollectorRegistry

import dumpy

logger = logging.getLogger("dumper")



class Monitoring(dumpy.base.PostProcessBase):
    """
    This class allow push metrics to PrometheusPushGateway service.
    """

    def __init__(self, db):
        self.db = db

    def parse_config(self):
        super(Monitoring, self).parse_config()

        self.host = self._get_option_value(self.config, 'prometheus', 'host')
        self.job_name = self._get_option_value(self.config, 'prometheus',
                                               'job_name')


    def process(self, file):
        self.parse_config()
        status = list()
        prom_labels = ["database", "task"]
        r = CollectorRegistry()
        db_backup_ok = Gauge("backup_ok", "Full Backup of mysql or pgsql "
                                          "databases.",
                             ["database"],
                             registry=r)
        db_backup_time_spent = Gauge("backup_time_spent",
                                     "Time spent with a task on backup.",
                                     prom_labels,
                                     registry=r)

        last_success = Gauge("backup_last_success_unixtime",
                             "Last time a backup job successfully finished",
                             ["database"],
                             registry=r)

        for i in dumpy.base.PROMETHEUS_MONIT_STATUS[self.db]:
            db_backup_time_spent.labels(self.db, i['task']).set(i['spent_time'])

        if False in dumpy.base.FAIL_STATE:
            db_backup_ok.labels(self.db).set(0)
        else:
            db_backup_ok.labels(self.db).set(1)
            last_success.labels(self.db).set_to_current_time()

        try:
            push_to_gateway(self.host, self.job_name, registry=r)
        except BaseException as e:
            logger.error("%s - %s - %s" % (self.db, self.__class__.__name__, e))

        return file