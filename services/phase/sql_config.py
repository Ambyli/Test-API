#!/usr/bin/env python3.10
import os
from dotenv import load_dotenv

load_dotenv()


# sql config
class SQLConfig:
    # CONSTRUCTOR
    # A OVERLOAD EXISTS WITHIN TOKEN_PULL.PY
    def __init__(self) -> None:
        # globals
        self.server = os.getenv("SQL_SERVER")
        self.database = os.getenv("SQL_DATABASE")
        self.password = os.getenv("SQL_PASSWORD")
        self.username = os.getenv("SQL_USERNAME")
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

    def update_con_string(
        self, server=None, database=None, username=None, password=None, driver=None
    ) -> None:
        if server is None:
            server = self.server
        else:
            self.server = server
        if database is None:
            database = self.database
        else:
            self.database = database
        if username is None:
            username = self.username
        else:
            self.username = username
        if password is None:
            password = self.password
        else:
            self.password = password
        if driver is None:
            driver = self.driver
        else:
            self.driver = driver

        self.con_str = self.def_str.format(
            server=server,
            database=database,
            username=username,
            password=password,
            driver=driver,
        )
