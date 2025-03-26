#!/usr/bin/env python3.7
import os
import pyodbc
from .sql_config import SQLConfig
from dotenv import load_dotenv

load_dotenv()


class SQL_Pull:
    # NEW OBJECT WITH RETURN OF DYNAMIC BASE
    def __call__(self, base=SQLConfig):
        # define instance class to be returned
        class SQL_Instance(base):
            # CONSTRUCTOR
            def __init__(self):
                super().__init__()

                # holds the table from the query
                self.table = []
                self.types = {}

            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc_value, traceback):
                # clear linked values
                return

            # execute query
            def execute(self, query: str, data: tuple = ()):
                # reset table
                self.table = []
                self.types = {}

                # make connection
                conn = pyodbc.connect(self.con_str)

                # conn.commit() will automatically be called when Python leaves the outer `with` statement
                # Neither crs.close() nor conn.close() will be called upon leaving the the `with` statement!!
                with conn:
                    # create cursor
                    crsr = conn.cursor()

                    # replace database
                    if "{database}" in query:
                        # replace database value in string with the provided database selected
                        query = query.format(database=self.database)

                    # execute query
                    crsr.execute(query, data)

                    # write output to table
                    try:
                        # get results
                        rows = crsr.fetchall()

                        # get column types
                        for item in crsr.description:
                            self.types[item[0]] = item[1].__name__

                        # get rows and zip them to columns
                        for row in rows:
                            instance = {}
                            for i, value in enumerate(row):
                                instance[str(crsr.description[i][0])] = value
                            self.table.append(instance)

                        crsr.commit()

                    except pyodbc.ProgrammingError:
                        crsr.rollback()
                        pass

                # return table
                return self.table, self.types

        return SQL_Instance


def main():
    other = SQLConfig

    # other.update_con_string(SQLConfig(), username="Test")
    def new(self):
        # globals
        self.server = os.getenv("SQL_SERVER")
        self.database = os.getenv("SQL_DATABASE")
        self.password = os.getenv("SQL_PASSWORD")
        self.username = "Test"
        self.driver = os.getenv("SQL_DRIVER")
        self.def_str = "Server={server};Database={database};UID={username};PWD={password};Driver={driver}"

        # SQL Connection Profile
        self.con_str = self.def_str.format(
            server=self.server,
            database=self.database,
            username=self.username,
            password=self.password,
            driver=self.driver,
        )

    other.__init__ = new

    with SQL_Pull()(other)() as derp:
        print(derp.con_str)
        derp.execute(
            query="""
            SELECT USER_NAME()
            """,
        )
        print(derp.table)


if __name__ == "__main__":
    main()
