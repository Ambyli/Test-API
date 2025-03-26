#!/usr/bin/env python3.7

from typing import List, Dict

from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .iot_config import IOTConfig


class IOT(IOTConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        IOTConfig.__init__(self, sql_config)

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    def log_sensor(
        self, sensor: str, temp_avg: float, humidity_avg: float, battery_avg: float
    ) -> int:
        try:
            self.LOG.info(
                "log_sensor: sensor={} temp_avg={} humidity_avg={} battery_avg={}".format(
                    sensor, temp_avg, humidity_avg, battery_avg
                )
            )

            iD = -1

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.insert_iot, (sensor, temp_avg, humidity_avg, battery_avg)
                )

                if len(sql.table) != 0:
                    iD = int(sql.table[0]["ID"])
                else:
                    raise Exception("No results found with the insert_iot query!")

            self.LOG.info("log_sensor: SUCCESS")
            return iD
        except Exception as e:
            self.LOG.error("log_sensor: error={}".format(e))
        self.LOG.info("log_sensor: FAILURE")
        return -1

    def get_iot_data(
        self, startdate: str, enddate: str, rows: int, offset: int
    ) -> list:
        try:
            self.LOG.info(
                "get_iot_data: startdate={} enddate={} rows={} offset={}".format(
                    startdate, enddate, rows, offset
                )
            )

            sensors = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_iot, (startdate, enddate, offset, rows))
                if len(sql.table) != 0:
                    sensors = sql.table
                else:
                    raise Exception("No results found with the get_iot query!")

            self.LOG.info("get_iot_data: SUCCESS")
            return sensors
        except Exception as e:
            self.LOG.error("get_iot_data: error={}".format(e))
        self.LOG.info("get_iot_data: FAILURE")
        return []


# UNIT TESTING


def main():
    return


if __name__ == "__main__":
    main()
