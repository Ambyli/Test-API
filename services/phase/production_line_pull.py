#!/usr/bin/env python3.7


from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .production_line_config import ProductionLineConfig


class ProductionLine(ProductionLineConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        ProductionLineConfig.__init__(self, sql_config)

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    def get_production_lines(self) -> list:
        try:
            self.LOG.info("get_production_lines: START")

            production_lines = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_active_production_lines, ())
                if len(sql.table) != 0:
                    production_lines = sql.table
                else:
                    raise Exception(
                        "No results found with the get_active_production_lines query!"
                    )

        except Exception as e:
            self.LOG.error("get_production_lines: error={}".format(e))
            self.LOG.info("get_production_lines: END")
            return []  # other error

        self.LOG.info("get_production_lines: kits={}".format(production_lines))
        self.LOG.info("get_production_lines: END")
        return production_lines  # no error


# UNIT TESTING


def main():
    return


if __name__ == "__main__":
    main()
