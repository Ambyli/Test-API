#!/usr/bin/env python3.7

from os import link
from typing import List, Dict
from datetime import date

from .sql_config import SQLConfig
from .shade_regex import gen_steps
from .stock_config import StockConfig
from .gauge_pull import Gauge
from .location_pull import Location
from .verification_pull import Verification
from .sql_pull import SQL_Pull


class Stock(StockConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        StockConfig.__init__(self, sql_config)

        # initialize gauge
        self.gauge = Gauge()

        # initialize location
        self.locations = Location()

        # Current working values
        result = []
        with SQL_Pull()(self.sql_config)() as sql:
            result, _ = sql.execute(self.get_status)
            for stat in result:
                self.statuses[stat["ID"]] = stat["StatusType"]
            result, _ = sql.execute(self.get_log_types)
            for log_type in result:
                self.log_types[log_type["ID"]] = log_type["LogType"]

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # Gets all stock types
    # input: N/A
    # output: Stock types on success, [] on error
    def get_stocks_detail(self) -> list:
        try:
            self.LOG.info("get_stocks: BEGIN")

            # define stock_types info
            stocks = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stocks_details)
                if len(sql.table) != 0:
                    stocks = sql.table
                else:
                    raise Exception("No results found with the get_stocks query!")

        except Exception as e:
            self.LOG.error("get_stocks: error={}".format(e))
            self.LOG.info("get_stocks: END")
            return []

        self.LOG.info("get_stocks: stock_type_info={}".format(str(stocks)))
        self.LOG.info("get_stocks: END")
        return stocks  # no error

    # Gets all stock types. Including inactive stocks
    # input: N/A
    # output: Stock types on success, [] on error
    def get_stock_types(self) -> list:
        try:
            self.LOG.info("get_stocks: BEGIN")

            # define stock_types info
            stock_types = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stocks)
                if len(sql.table) != 0:
                    stock_types = sql.table
                else:
                    raise Exception("No results found with the get_stocks query!")

        except Exception as e:
            self.LOG.error("get_stock_types: error={}".format(e))
            self.LOG.info("get_stock_types: END")
            return []

        self.LOG.info("get_stock_types: stock_type_info={}".format(str(stock_types)))
        self.LOG.info("get_stock_types: END")
        return stock_types  # no error

    # Gets all active stock types
    # input: Optional Status (default value = 11)
    # output: Stock types on success, [] on error
    def get_active_stock_types(self, status: int = 11) -> list:
        try:
            self.LOG.info(f"get_active_stocks: status={status}")

            # define stock_types info
            stock_types = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_active_stocks, (status))
                if len(sql.table) != 0:
                    stock_types = sql.table
                else:
                    raise Exception(
                        "No results found with the get_active_stocks query!"
                    )

        except Exception as e:
            self.LOG.error("get_active_stocks_types: error={}".format(e))
            self.LOG.info("get_active_stocks_types: END")
            return []

        self.LOG.info(
            "get_active_stocks_types: stock_type_info={}".format(str(stock_types))
        )
        self.LOG.info("get_active_stocks_types: END")
        return stock_types  # no error

    # Gets stock type by stockID
    # input: stock ID
    # output: Stock type on success, [] on error
    def get_stock_types_by_ID(self, ID: int) -> list:
        try:
            self.LOG.info(f"get_stock_types_by_name: ID={ID}")

            # define stock_type info
            stock_type = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stocks_by_ID, (ID))
                if len(sql.table) != 0:
                    stock_type = sql.table
                else:
                    raise Exception("No results found with the get_stocks_by_ID query!")

        except Exception as e:
            self.LOG.error("get_stock_types_by_ID: error={}".format(e))
            self.LOG.info("get_stock_types_by_ID: END")
            return []

        self.LOG.info("get_stock_types_by_ID: stock_type={}".format(str(stock_type)))
        self.LOG.info("get_stock_types_by_ID: END")
        return stock_type  # no error

    # Gets stocks by locationIDs and status
    # input: locationIDs (optional), status (optional)
    # output: list of Stocks
    def get_stock_storage_by_locations_and_status(
        self, locationIDs: str, status: int
    ) -> list:
        try:
            self.LOG.info(
                "get_stock_by_locations_and_status: locationIDs={} status={}".format(
                    locationIDs, status
                )
            )

            # define stocks info
            stocks = []

            with SQL_Pull()(self.sql_config)() as sql:
                locationIDs = (
                    None if locationIDs == [None] else ",".join(map(str, locationIDs))
                )
                sql.execute(
                    self.get_stocks_by_locations_and_status, (locationIDs, status)
                )
                if len(sql.table) != 0:
                    stocks = sql.table
                else:
                    raise Exception(
                        "No results found with the get_stock_by_locations_and_status query!"
                    )

        except Exception as e:
            self.LOG.error("get_stock_by_locations_and_status: error={}".format(e))
            self.LOG.info("get_stock_by_locations_and_status: END")
            return []

        self.LOG.info(
            "get_stock_by_locations_and_status: stock_type={}".format(str(stocks))
        )
        self.LOG.info("get_stock_by_locations_and_status: END")
        return stocks  # no error

    # get stock type logs
    # input: stockID
    def get_stock_type_logs_by_stock_id(self, stockID: int) -> list:
        try:
            self.LOG.info("get_stock_type_logs_by_stock_id: stockID={}".format(stockID))
            logs = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stock_logs_by_stock, (stockID,))
                if len(sql.table) != 0:
                    logs = sql.table
                else:
                    raise Exception(
                        "No results found with the get_stock_type_logs_by_stock_id query!"
                    )

        except Exception as e:
            self.LOG.error("get_stock_type_logs_by_stock_id: error={}".format(e))
            return []

        self.LOG.info("get_stock_type_logs_by_stock_id: END")
        return logs

    # get stock type logs
    # input: logTypeIDs (optional), stockIDs (optional), customerIDs(optional), from, to
    def get_stock_type_logs(
        self,
        logTypeIDs: list,
        stockIDs: list,
        customerIDs: list,
        loggedFrom: str,
        loggedTo: str,
    ) -> list:
        try:
            self.LOG.info(
                "get_stock_type_logs: logTypeIDs={}, stockIDs={}, customerIDs={}, loggedFrom={}, loggedTo={}, ".format(
                    logTypeIDs, stockIDs, customerIDs, loggedFrom, loggedTo
                )
            )
            logs = []

            with SQL_Pull()(self.sql_config)() as sql:
                logTypeIDs_string = (
                    ",".join(logTypeIDs) if logTypeIDs is not None else None
                )
                stockIDs_string = ",".join(stockIDs) if stockIDs is not None else None
                customerIDs_string = (
                    ",".join(customerIDs) if customerIDs is not None else None
                )
                sql.execute(
                    self.get_stock_logs,
                    (
                        logTypeIDs_string,
                        stockIDs_string,
                        customerIDs_string,
                        loggedFrom,
                        loggedTo,
                    ),
                )
                if len(sql.table) != 0:
                    logs = sql.table
                else:
                    raise Exception(
                        "An error occurred with the get_stock_type_logs query!"
                    )

        except Exception as e:
            self.LOG.error("get_stock_type_logs: error={}".format(e))
            return []

        self.LOG.info("get_stock_type_logs: END")
        return logs

    # log a change for a stock type
    # input: verification, stockID, description
    # output: 0 on success, -1 on error
    def log_stock_type(
        self,
        stockID: int,
        change: str,
        verification: Verification,
        logNote: str,
        logTypeID: int,
    ) -> int:
        try:
            self.LOG.info(
                'log_stock_type: logtypeID={} stockID={} change="{}" dateIn="{}" logNote="{}"'.format(
                    logTypeID, stockID, change, verification, logNote
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_stock_log,
                        (
                            int(logTypeID),
                            str(change),
                            str(logNote),
                            verification.get_verification(),
                            int(stockID),
                            int(stockID),
                            int(stockID),
                            int(stockID),
                            int(stockID),
                            int(stockID),
                            int(stockID),
                            int(stockID),
                            int(stockID),
                        ),
                    )
                    if len(sql.table) != 0:
                        self.LOG.info("log_stock_type: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the insert_stock_log query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_stock_type: error={}".format(e))

        self.LOG.info("log_stock_type: END")
        return -1

    # Creates a stock type
    # input: name, customerID, createDate, createBy, verification, status, alertLimit, priority, barcode, category
    # output: Stock types on success, -1 on error
    def create_stock_type(
        self,
        name: str,
        customerID: str,
        description: str,
        verification: Verification,
        priority: int,
        barcode: str,
        leadTime: int,
        reorderPoint: int,
        dailyUse: int | None = None,
        vendorID: int | None = None,
        responsible: Verification = None,
    ) -> int:
        try:
            self.LOG.info(
                f'insert_stock: Stockname="{name}" customerID="{customerID}" "description="{description} priority={priority} barcode={barcode} leadTime={leadTime} reorderPoint={reorderPoint} dailyUse={dailyUse} vendorID={vendorID} responsible={responsible}'
            )

            # define stock
            stockID = -1

            responsibleID = None
            if responsible is not None:
                responsibleID = responsible.get_verification()

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
                and (responsibleID != -1 or responsibleID is None)
            ):
                # continue on
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.insert_stock,
                        (
                            name,
                            customerID,
                            description,
                            verification.get_verification(),
                            priority,
                            barcode,
                            leadTime,
                            reorderPoint,
                            dailyUse,
                            vendorID,
                            responsibleID,
                        ),
                    )
                    if len(sql.table) != 0:
                        stockID = int(sql.table[0]["ID"])
                        self.log_stock_type(
                            stockID, "stock_created", verification, "Stock Created", 44
                        )
                    else:
                        raise Exception("No results found with the insert_stock query!")
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_stock_type: error={}".format(e))
            self.LOG.info("create_stock_type: END")
            return -1  # other error

        self.LOG.info("create_stock_type: stockID={}".format(stockID))
        self.LOG.info("create_stock_type: END")
        return stockID  # no error

    # updates stock type
    # input: stockTypeID, verification, name, customerID, priority, barcode, description
    # output: Stock ID on success, -1 on error
    def update_stock_type_info(
        self,
        stockTypeID: int,
        verification: Verification,
        name: str,
        customerID: str,
        priority: int,
        barcode: str,
        leadTime: int,
        reorderPoint: int,
        dailyUse: int,
        vendorID: int,
        responsible: Verification,
        description: str = "",
    ) -> int:
        # define stock
        try:
            self.LOG.info(
                "update_stock_type_info: stockTypeID={} name={} customerID={} description={} verification={} priority={} barcode={} leadTime={} reorderPoint={} dailyUse={} vendorID={} responsible={}".format(
                    stockTypeID,
                    name,
                    customerID,
                    description,
                    verification,
                    priority,
                    barcode,
                    leadTime,
                    reorderPoint,
                    dailyUse,
                    vendorID,
                    responsible,
                )
            )

            stockID = -1

            responsibleID = None
            if responsible is not None:
                responsibleID = responsible.get_verification()

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                    and (responsibleID != -1 or responsibleID is None)
                ):
                    sql.execute(
                        self.update_stock_type,
                        (
                            name,
                            description,
                            customerID,
                            priority,
                            barcode,
                            leadTime,
                            reorderPoint,
                            vendorID,
                            responsibleID,
                            dailyUse,
                            stockTypeID,
                            verification.get_verification(),
                        ),
                    )
                    if len(sql.table) != 0:
                        stockID = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "No results found with the update_stock_status query!"
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("update_stock_type_info: error={}".format(e))
            return -1

        self.LOG.info("update_stock_type_info: END")
        return stockID

    # updates the status of a stock type
    # input: verification, stockID, status
    # output: 0 on success, -1 on error
    def update_status_of_stock_type(
        self, verification: Verification, stockID: int, status: int
    ) -> int:
        try:
            self.LOG.info(
                "update_stock_status: verification={} stockID={} status={}".format(
                    verification, stockID, status
                )
            )
            # Get label of status ID given
            label = self.statuses[status]
            if len(label) == 0:
                raise Exception(
                    f"Unable to find a matching status with a given status id {status}!"
                )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_stock_status, (status, stockID))
                    if len(sql.table) != 0:
                        self.LOG.info("update_stock_status: END")

                        # Log change of stock type status
                        self.log_stock_type(
                            stockID,
                            "Status: {0}".format(label),
                            verification,
                            "Status Updated",
                            34,
                        )
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_stock_status query!"
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("update_status_of_stock_type: error={}".format(e))

        self.LOG.info("update_status_of_stock_type: END")
        return -1

    # updates the customerID of a stock type
    # input: verification, stockID, customerID
    # output: 0 on success, -1 on error
    def update_customer_of_stock_type(
        self, verification: Verification, stockID: str, customerID: str
    ) -> int:
        try:
            self.LOG.info(
                "update_customer_of_stock_type: verification={} stockID={} customerID={}".format(
                    verification, stockID, customerID
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_stock_type_customer, (customerID, stockID))

                    if len(sql.table) != 0:
                        self.LOG.info("update_customer_of_stock_type: END")

                        # Log change of stock type customerID
                        self.log_stock_type(
                            stockID,
                            f"CustomerID: {customerID}",
                            "CustomerID Updated",
                            verification,
                        )
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_customer_of_stock_type query!"
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("update_customer_of_stock_type: error={}".format(e))

        self.LOG.info("update_customer_of_stock_type: END")
        return -1

    # updates the priority of a stock type
    # input: verification, stockID, priority
    # output: 0 on success, -1 on error
    def update_priority_of_stock_type(
        self, verification: Verification, stockID: str, priority: int
    ) -> int:
        try:
            self.LOG.info(
                "update_priority_of_stock_type: verification={} stockID={} customerID={}".format(
                    verification, stockID, priority
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_stock_type_priority, (priority, stockID))

                    if len(sql.table) != 0:
                        self.LOG.info("update_priority_of_stock_type: END")

                        # Log change of stock type priority
                        self.log_stock_type(
                            stockID,
                            f"Priority: {priority}",
                            "Priority Updated",
                            verification,
                        )
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_priority_of_stock_type query!"
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("update_priority_of_stock_type: error={}".format(e))

        self.LOG.info("update_priority_of_stock_type: END")
        return -1

    # Creates a stock storage
    # input: stockType, location, verification, status
    # output: Stock storage on success, -1 on error
    def create_stock_storage(
        self,
        stockType: int,
        location: int,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                f'create_stock_storage: stockType="{stockType}" verification={verification} location={location}'
            )

            # define stock storage
            stockStorageID = -1

            # run employee check
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # continue on
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.insert_stock_into_storage,
                        (
                            verification.get_verification(),
                            stockType,
                            location,
                        ),
                    )
                    if len(sql.table) != 0:
                        stockStorageID = int(sql.table[0]["ID"])
                        self.log_stock_storage(
                            stockStorageID,
                            "create_stock_storage",
                            f"Stock Storage {stockStorageID} Created",
                            verification,
                            2,
                        )

                    else:
                        raise Exception(
                            "No results found with the insert_stock_into_storage query!"
                        )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_stock_storage: error={}".format(e))
            self.LOG.info("create_stock_storage: END")
            return -1  # other error

        self.LOG.info("create_stock_storage: stockID={}".format(stockStorageID))
        self.LOG.info("create_stock_storage: END")
        return stockStorageID  # no error

    # Allows for bulk stock storage creation
    # input: verification, stocks[{ID: int, quantity: int}], location, gauge, order, description
    # output: returns {stockStorages} or {}
    def create_bulk_stock_storages(
        self,
        verification: Verification,
        stocks: list,
        location: int,
        order: str,
        description: str,
        gaugeID: int | None = None,
    ) -> dict:
        try:
            info = {}
            self.LOG.info(
                "create_bulk_stock_storages: verification={} stocks={}".format(
                    verification,
                    stocks,
                )
            )
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                stockStorages = []
                failedCreations = []
                # Getting total length for Gauge
                gaugeLength = 0
                count = 0
                for stock in stocks:
                    gaugeLength += int(stock["quantity"])
                # Create a stock storage for each stock in stocks
                for stock in stocks:
                    for x in range(0, int(stock["quantity"])):
                        storage = self.create_stock_storage(
                            int(stock["ID"]), location, verification
                        )
                        if storage != -1:
                            stockStorages.append(storage)
                        else:
                            failedCreations.append(stock["ID"])

                        count += 1

                        self.gauge.update_gauge(
                            gaugeID,
                            self.LOG,
                            "Creating Stock Storages",
                            index=count,
                            length=gaugeLength,
                            limit=100,
                            label="Bulk Stock Storage Creation",
                        )
                # Create stock storage batch
                stockStorageBatch = self.create_stock_storage_batch(
                    list(stockStorages),
                    verification,
                    str(order),
                    str(description),
                    int(location),
                )
                if stockStorageBatch == -1:
                    raise Exception("Stock Storage Batch creation failed")

            else:
                raise Exception("Invalid verification!")
            # Set info keys to values obtained
            info["Success"] = stockStorages
            info["Failed"] = failedCreations
            info["BatchID"] = stockStorageBatch

        except Exception as e:
            self.LOG.error("create_bulk_stock_storages: error={}".format(e))
            return {}
        self.LOG.info(f"Successful bulk stock storage creations = {stockStorages}")
        self.LOG.info(f"Failed bulk stock storage creations = {failedCreations}")
        self.LOG.info("create_bulk_stock_storages: END")
        return info

    # Get Stock Storage Logs by StockID
    # input: stockID
    # output: list of logs
    def get_stock_logs_by_stockID(self, stockID) -> list:
        info = []
        try:
            self.LOG.info("get_stock_logs_by_stockID: stockID={}".format(stockID))
            if stockID is not None:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(self.get_stock_storage_logs_by_stockID, (stockID,))
                    if len(sql.table) != 0:
                        info = sql.table
            else:
                self.LOG.info("get_stock_logs_by_stockID: error= Invalid input")

        except Exception as e:
            self.LOG.error("get_stock_logs_by_stockID: error={}".format(e))
            return []
        self.LOG.info("get_stock_logs_by_stockID: END")
        return info

    # Receiving Stocks
    # input: stockStorages, verification, location, order, description
    # output: returns batchID or -1
    def receiving_stocks(
        self, stockStorages, verification, location, order, description
    ) -> int:
        info = -1
        try:
            self.LOG.info(
                "receiving_stocks: stockStorages={} verification={}  location={}  order={}  description={}  ".format(
                    stockStorages, verification, location, order, description
                )
            )

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.insert_stock_storage_batch,
                        (
                            str(order),
                            verification.get_verification(),
                            str(description),
                            int(location),
                        ),
                    )
                    stockStorageBatchID = int(sql.table[0]["ID"])
                    if stockStorageBatchID != 0:
                        for st in stockStorages:
                            sql.execute(
                                self.bulk_insert_stocks,
                                (
                                    stockStorageBatchID,
                                    st["quantity"],
                                    st["ID"],
                                    location,
                                    verification.get_verification(),
                                ),
                            )
                            self.log_stock_type(
                                st["ID"],
                                "stock_received",
                                verification,
                                "Received " + str(st["quantity"]) + " items",
                                45,
                            )
                        if len(sql.table) != 0:
                            info = stockStorageBatchID
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("receiving_stocks: error={}".format(e))
            return -1
        self.LOG.info("receiving_stocks: END")
        return info

    # Moving Stocks
    # input: verification, stocks
    # output: 1 or -1
    def moving_stocks(self, verification, stocks) -> int:
        info = -1
        try:
            self.LOG.info(
                "moving_stocks: stocks={} verification={} ".format(stocks, verification)
            )

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    for stk in stocks:
                        sql.execute(
                            self.bulk_moving_stocks,
                            (
                                stk["initialLocation"],
                                stk["destinationLocation"],
                                stk["quantity"],
                                stk["ID"],
                            ),
                        )
                        locations = self.locations.get_locations_by_status()
                        fromLocation = (
                            location["Location"]
                            for location in locations
                            if location["ID"] == int(stk["initialLocation"])
                        )
                        toLocation = (
                            location["Location"]
                            for location in locations
                            if location["ID"] == int(stk["destinationLocation"])
                        )
                        self.log_stock_type(
                            stk["ID"],
                            "stock_moved",
                            verification,
                            "Moved "
                            + str(stk["quantity"])
                            + " items From "
                            + next(fromLocation, "")
                            + " to "
                            + next(toLocation, ""),
                            1,
                        )
                    info = 1
            else:
                raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("moving_stocks: error={}".format(e))
            return -1
        self.LOG.info("moving_stocks: END")
        return info

    # Creates a stock storage batch
    # Input stockStorageIDs, EmployeeID, order, description, location, status
    # Output Stock Storage Batch ID on success, -1 on error
    def create_stock_storage_batch(
        self,
        stockStorageIDs: list,
        verification: Verification,
        order: str,
        description: str,
        location: int,
    ) -> int:
        try:
            self.LOG.info(
                f'insert_stock_storage_batch: stockStorageIDs="{stockStorageIDs}" verification="{verification}" order={order} description={description} location={location}'
            )

            stockStorageBatchID = -1

            # run employee check
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # continue on
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.insert_stock_storage_batch,
                        (
                            str(order),
                            verification.get_verification(),
                            str(description),
                            int(location),
                        ),
                    )
                    if len(sql.table) != 0:
                        stockStorageBatchID = int(sql.table[0]["ID"])
                        for stockStorage in stockStorageIDs:
                            sql.execute(
                                self.insert_stock_storage_batch_link,
                                (
                                    int(stockStorage),
                                    stockStorageBatchID,
                                    verification.get_verification(),
                                ),
                            )
                            if len(sql.table) == 0:
                                raise Exception(
                                    "No results found with the insert_aligner_batch_link query!"
                                )

                    else:
                        raise Exception(
                            "No results found with the insert_stock_storage_batch query!"
                        )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_stock_storage_batch: error={}".format(e))
            self.LOG.info("create_stock_storage_batch: END")
            return -1  # other error

        self.LOG.info(
            "create_stock_storage_batch: stockID={}".format(stockStorageBatchID)
        )
        self.LOG.info("create_stock_storage_batch: END")
        return stockStorageBatchID  # no error

    # Gets a stock storage batch by the batch ID
    # input: stockStorageBatchID
    # output: [StockStorages] on success, [] on error
    def get_stock_storage_batch_by_batchID(self, stockStorageBatchID: int) -> list:
        try:
            self.LOG.info(
                f"get_stock_storage_batch_by_ID : stockStorageBatchID={stockStorageBatchID}"
            )

            stock_storages = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stock_storage_batch_by_ID, (stockStorageBatchID))

                if len(sql.table) != 0:
                    stock_storages = sql.table
                else:
                    raise Exception(
                        "No results found with the get_stock_storage_batch_by_ID query!"
                    )

        except Exception as e:
            self.LOG.error("get_stock_storage_batch_by_batchID: error={}".format(e))
            self.LOG.info("get_stock_storage_batch_by_batchID: END")
            return []

        self.LOG.info(
            "get_stock_storage_batch_by_batchID: stock_storage={}".format(
                str(stock_storages)
            )
        )
        self.LOG.info("get_stock_storage_batch_by_batchID: END")
        return stock_storages  # no error

    # Gets a stock storage batch by a Location ID
    # input: location
    # output: [StockStorages] on success, [] on error
    def get_stock_storage_batch_by_locationID(self, location: int) -> list:
        try:
            self.LOG.info(f"get_stock_storage_batch_by_location : location={location}")

            stock_storages = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stock_storage_batch_by_location, (location))
                if len(sql.table) != 0:
                    stock_storages = sql.table
                else:
                    raise Exception(
                        "No results found with the get_stock_storage_batch_by_location query!"
                    )

        except Exception as e:
            self.LOG.error("get_stock_storage_batch_by_locationID: error={}".format(e))
            self.LOG.info("get_stock_storage_batch_by_locationID: END")
            return []

        self.LOG.info(
            "get_stock_storage_batch_by_locationID: stock_storage={}".format(
                str(location)
            )
        )
        self.LOG.info("get_stock_storage_batch_by_locationID: END")
        return stock_storages  # no error

    # Create Stock Storage Batch File Links
    # input: verification, stockStorageBatchID, fileIDs
    # output: List of Link IDs
    def insert_stock_storage_batch_file_link(
        self, verification: Verification, stockStorageBatchID: int, fileIDs: list
    ) -> list:
        try:
            self.LOG.info(
                "insert_stock_storage_batch_file_link: verification={} stockStorageBatchID={} fileIDs={} ".format(
                    verification, stockStorageBatchID, fileIDs
                )
            )

            linkIDs = []

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_stock_storage_batch_file_links,
                        (
                            int(stockStorageBatchID),
                            verification.get_verification(),
                            11,
                            ",".join(map(str, fileIDs)),
                        ),
                    )
                    if len(sql.table) != 0:
                        linkIDs = sql.table

                    else:
                        raise Exception(
                            "No results found with the insert_stock_storage_batch_file_link query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("insert_stock_storage_batch_file_link: error={}".format(e))
            self.LOG.info("insert_stock_storage_batch_file_link: END")
            return []  # other error

        self.LOG.info("insert_stock_storage_batch_file_link: linkID={}".format(linkIDs))
        self.LOG.info("insert_stock_storage_batch_file_link: END")
        return linkIDs  # no error

    # logs a file path to a stockStorageBatch
    # input: stockStorageBatchID, FileTypeID, Path, EmployeeID
    # output: LinkID on success, -1 on error
    def insert_file_to_stockStorageBatch(
        self,
        stockStorageBatchID: int,
        fileTypeID: int,
        path: str,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                "insert_stock_storage_batch_file: stockStorageBatchID={} fileTypeID={} path={} verification={}".format(
                    stockStorageBatchID, fileTypeID, path, verification
                )
            )

            linkID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_stock_storage_batch_file,
                        (
                            int(stockStorageBatchID),
                            int(fileTypeID),
                            str(path),
                            verification.get_verification(),
                        ),
                    )
                    if len(sql.table) != 0:
                        linkID = int(sql.table[0]["ID"])

                    else:
                        raise Exception(
                            "No results found with the insert_stock_storage_batch_file query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("insert_file_to_stockStorageBatch: error={}".format(e))
            self.LOG.info("insert_file_to_stockStorageBatch: END")
            return -1  # other error

        self.LOG.info("insert_file_to_stockStorageBatch: linkID={}".format(linkID))
        self.LOG.info("insert_file_to_stockStorageBatch: END")
        return linkID  # no error

    # gets a list of stockStorageIDs that carry a matching batchID
    # input: BatchID
    # output: stockStorageIDs on success, [] on error
    def get_stockStorage_by_batch(self, batchID: int) -> list:
        try:
            self.LOG.info("get_stockStorage_by_batch: batchID={}".format(batchID))

            stockStorageIDs = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stock_storage_by_batch, (batchID))
                if len(sql.table) != 0:
                    stockStorageIDs = sql.table
                else:
                    raise Exception(
                        "No results found with the get_stock_storage_by_batch query!"
                    )

        except Exception as e:
            self.LOG.error("get_stockStorage_by_batch: error={}".format(e))
            self.LOG.info("get_stockStorage_by_batch: END")
            return []  # other error

        self.LOG.info(
            "get_stockStorage_by_batch: alignerIDs={}".format(stockStorageIDs)
        )
        self.LOG.info("get_stockStorage_by_batch: END")
        return stockStorageIDs

    # gets a list of files that carry a matching stockStoragebatchID
    # input: BatchID
    # output: files on success, [] on error
    def get_stockStorageBatch_file_by_batch(self, batchID: int) -> list:
        try:
            self.LOG.info(
                "get_stockStorageBatch_file_by_batch: batchID={}".format(batchID)
            )

            stockStorageIDs = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stock_storage_batch_file_by_batch, (batchID))
                if len(sql.table) != 0:
                    files = sql.table
                else:
                    raise Exception(
                        "No results found with the get_stock_storage_batch_file_by_batch query!"
                    )

        except Exception as e:
            self.LOG.error("get_stockStorageBatch_file_by_batch: error={}".format(e))
            self.LOG.info("get_stockStorageBatch_file_by_batch: END")
            return []  # other error

        self.LOG.info(
            "get_stockStorageBatch_file_by_batch: alignerIDs={}".format(stockStorageIDs)
        )
        self.LOG.info("get_stockStorageBatch_file_by_batch: END")
        return files

    # Remove a stock from storage
    # input: verificationID, stockStorageID
    # output: 0 on success, -1 on error
    def remove_stock_storage(
        self, verification: Verification, stockStorageID: int
    ) -> int:
        try:
            self.LOG.info(
                "remove_stock_storage: verification={} stockStorageID={}".format(
                    verification,
                    stockStorageID,
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.remove_stock_from_storage,
                        (verification.get_verification(), int(stockStorageID)),
                    )

                    if len(sql.table) != 0:
                        self.LOG.info("remove_stock_storage: END")

                        self.log_stock_storage(
                            int(stockStorageID),
                            "REMOVED",
                            "Stock Removed",
                            verification,
                            34,
                        )

                        return 0
                    else:
                        raise Exception(
                            "No results found with the remove_stock_from_storage query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("remove_stock_storage: error={}".format(e))

        self.LOG.info("remove_stock_storage: END")
        return -1

    # updates the location of a stock storage
    # input: verification, stockStorageID, location
    # output: 0 on success, -1 on error
    def update_location_of_stock_storage(
        self, verification: Verification, stockStorageID: int, location: int
    ) -> int:
        try:
            self.LOG.info(
                "update_location_of_stock_storage: verification={} stockStorageID={} location={}".format(
                    verification, stockStorageID, location
                )
            )
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_stock_storage_location,
                        (int(location), int(stockStorageID)),
                    )
                    if len(sql.table) != 0:
                        self.LOG.info("update_location_of_stock_storage: END")

                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_stock_storage_location query!"
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("update_location_of_stock_storage: error={}".format(e))

        self.LOG.info("update_location_of_stock_storage: END")
        return -1

    # Updates the location of multiple stock Storages
    # input : verification, stocks [{ID: int, initialLocation: int , destinationLocation: int, quantity: int}]
    # output: {StockStorageIDs : { "Sucess" : [], Failed: []}} on success, {} on error
    def update_location_of_stock_storages(
        self, verification: Verification, stocks: list, gaugeID: int | None = None
    ) -> dict:
        try:
            info = {}

            self.LOG.info(
                "update_location_of_stock_storages: verification={} stocks={}".format(
                    verification,
                    stocks,
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # Getting total length for Gauge
                    gaugeLength = 0
                    for stock in stocks:
                        gaugeLength += int(stock["quantity"])
                        # Creates keys for info
                        info[stock["ID"]] = {"Success": [], "Failed": []}

                    # Generate list of stock storages at the initial location
                    for stock in stocks:
                        stockStorages = self.get_stock_storage_by_stock_location(
                            int(stock["ID"]),
                            int(stock["initialLocation"]),
                            int(stock["quantity"]),
                        )

                        # Loops through stock storage list and updates the location of each stock storage
                        for i, stockStorage in enumerate(stockStorages):
                            if (
                                sql.execute(
                                    self.update_stock_storage_location,
                                    (
                                        int(stock["destinationLocation"]),
                                        int(stockStorage["ID"]),
                                    ),
                                )
                                is not None
                            ):
                                info[stock["ID"]]["Success"].append(stockStorage["ID"])
                            else:
                                info[stock["ID"]]["Failed"].append(stockStorage["ID"])

                            self.log_stock_storage(
                                int(stockStorage["ID"]),
                                f"Moved : {stock['destinationLocation']}",
                                f"Moved stock to {stock['destinationLocation']}",
                                verification,
                                1,
                            )

                            self.gauge.update_gauge(
                                gaugeID,
                                self.LOG,
                                "updating Location of stock storage",
                                index=i + 1,
                                length=gaugeLength,
                                limit=100,
                                label="Moving Stock Storages",
                            )

                    if len(sql.table) != 0:
                        self.LOG.info("update_location_of_stock_storages: END")
                        return info
                    else:
                        raise Exception(
                            "An error occured with the update_location_of_stock_storage query"
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("update_location_of_stock_storages: error={}".format(e))
            return {}

    # updates the stock type of a stock storage
    # input: verification, stockStorageID, stockType
    # output: 0 on success, -1 on error
    def update_stockType_of_stock_storage(
        self, verification: Verification, stockStorageID: int, stockType: int
    ) -> int:
        try:
            self.LOG.info(
                "update_stockType_of_stock_storage: verification={} stockStorageID={} stockType={}".format(
                    verification, stockStorageID, stockType
                )
            )
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_stock_storage_stock_type,
                        (int(stockType), int(stockStorageID)),
                    )
                    if len(sql.table) != 0:
                        self.LOG.info("update_stockType_of_stock_storage: END")

                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_stock_storage_stockType query!"
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("update_stockType_of_stock_storage: error={}".format(e))

        self.LOG.info("update_stockType_of_stock_storage: END")
        return -1

    # gets the stock storage by location
    # input: locationID
    # output: stock_storage on success, [] on error
    def get_stock_storage_by_location_id(self, location: int) -> list:
        try:
            self.LOG.info(f"get_stock_storage_by_location: location={location}")

            # define stock_storage info
            stock_storage = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stock_storage_by_location, (location))
                if len(sql.table) != 0:
                    stock_storage = sql.table
                else:
                    raise Exception(
                        "No results found with the get_stock_storages_by_location query!"
                    )

        except Exception as e:
            self.LOG.error("get_stock_storage_by_location: error={}".format(e))
            self.LOG.info("get_stock_storage_by_location: END")
            return []

        self.LOG.info(
            "get_stock_storage_by_location: stock_storage={}".format(str(stock_storage))
        )
        self.LOG.info("get_stock_storage_by_location: END")
        return stock_storage  # no error

    # gets the stock storage by stockID and location
    # input: stockID, location
    # output: stock_storage on success, [] on error
    def get_stock_storage_by_stock_location(
        self, stockID: int, location: int, top: int
    ) -> list:
        try:
            self.LOG.info(
                f"get_stock_storage_by_stock_location: stockID={stockID} location={location} top={top}"
            )

            # define stock_storage info
            stock_storage = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_active_stock_storages_by_id_location,
                    (stockID, location, top),
                )

                if len(sql.table) != 0:
                    stock_storage = sql.table
                else:
                    raise Exception(
                        "No results found with the get_active_stock_storages_by_id_location query!"
                    )

        except Exception as e:
            self.LOG.error("get_stock_storage_by_stock_location: error={}".format(e))
            self.LOG.info("get_stock_storage_by_stock_location: END")
            return []

        self.LOG.info(
            "get_stock_storage_by_stock_location: stock_storage={}".format(
                str(stock_storage)
            )
        )
        self.LOG.info("get_stock_storage_by_stock_location: END")
        return stock_storage  # no error

    # Gets the stock storage batch information from a date range at a location along with their file links
    # input: location, date range, offset
    # output: stock_storage_batches + File links on success, [] on error
    def get_stock_storage_batches_with_file_links_by_location(
        self, location: int, dateFrom: str, dateTo: str, offset: int, rows: int
    ) -> list:
        try:
            self.LOG.info(
                f"get_stock_storage_batch_history_by_location: location={location} dateFrom={dateFrom} dateTo={dateTo} offset={offset} rows={rows}"
            )

            # define stock_storage_batches info
            stock_storage_batches = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_stock_storage_batch_history_by_location,
                    (dateFrom, dateTo, location, offset, rows),
                )

                if len(sql.table) != 0:
                    stock_storage_batches = sql.table
                else:
                    raise Exception(
                        "No results found with the get_stock_storage_batch_history_by_location query!"
                    )

        except Exception as e:
            self.LOG.error(
                "get_stock_storage_batches_with_file_links_by_location: error={}".format(
                    e
                )
            )
            self.LOG.info("get_stock_storage_batches_with_file_links_by_location: END")
            return []

        self.LOG.info(
            "get_stock_storage_batches_with_file_links_by_location: stock_storage={}".format(
                str(stock_storage_batches)
            )
        )
        self.LOG.info("get_stock_storage_batches_with_file_links_by_location: END")
        return stock_storage_batches  # no error

    # Checks if stockstorage location has more than input stock and can be moved
    # input: stocks
    # output: List of items that can't be moved on error, [] on success
    def check_if_stocks_can_be_moved(self, stocks) -> list:
        try:
            self.LOG.info(f"check_if_stocks_can_be_moved: stocks={stocks}")
            lowQty = []

            allValid = list(
                map(
                    lambda x: (
                        x["ID"],
                        len(
                            self.get_stock_storage_by_stock_location(
                                int(x["ID"]),
                                int(x["initialLocation"]),
                                int(x["quantity"]),
                            )
                        )
                        >= int(x["quantity"]),
                    ),
                    stocks,
                )
            )

            if any(False in stock for stock in allValid):
                for stockID, valid in allValid:
                    if valid is False:
                        lowQty.append(stockID)
                    else:
                        continue

            if len(lowQty) > 0:
                raise Exception(
                    "Not enough stock available for these items! {}!".format(lowQty)
                )

        except Exception as e:
            self.LOG.error("check_if_stocks_can_be_moved: error={}".format(e))
            self.LOG.info("check_if_stocks_can_be_moved: END")
            return lowQty

        self.LOG.info("check_if_stocks_can_be_moved: END")
        return lowQty  # no error

    # gets all stock storages including inactive stock storages
    # input: N/A
    # output: [stock_storage] on success, [] on error
    def get_all_stock_storages(self) -> list:
        try:
            self.LOG.info("get_all_stock_storages: BEGIN")

            # define stock_storages info
            stock_storages = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stock_storage)
                if len(sql.table) != 0:
                    stock_storages = sql.table
                else:
                    raise Exception(
                        "No results found with the get_stock_storage query!"
                    )

        except Exception as e:
            self.LOG.error("get_all_stock_storages: error={}".format(e))
            self.LOG.info("get_all_stock_storages: END")
            return []

        self.LOG.info(
            "get_all_stock_storages: stock_storages={}".format(str(stock_storages))
        )
        self.LOG.info("get_all_stock_storages: END")
        return stock_storages  # no error

    # Gets the logs of a particular location
    # input: location
    # output: logs on success, [] on error
    def get_log_of_stock_storage_by_location(self, location: int) -> list:
        try:
            self.LOG.info(
                "get_log_of_stock_storage_by_location: location={}".format(location)
            )

            logs = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stock_storage_log_by_location, (location))
                if len(sql.table) != 0:
                    logs = sql.table
                else:
                    raise Exception("No results found with the ")

        except Exception as e:
            self.LOG.error("get_log_of_stock_storage_by_location: error={}".format(e))
            self.LOG.info("get_log_of_stock_storage_by_location: END")
            return []

        self.LOG.info("get_log_of_stock_storage_by_location: logs={}".format(len(logs)))
        self.LOG.info("get_log_of_stock_storage_by_location: END")
        return logs

    # log a change for a stock storage
    # input: verification, stockStorageID, description
    # output: 0 on success, -1 on error
    def log_stock_storage(
        self,
        stockStorageID: int,
        change: str,
        description: str,
        verification: Verification,
        logTypeID: int,
    ) -> int:
        try:
            self.LOG.info(
                'log_stock_storage: logtypeID={} stockStorageID={} change="{}" description="{}" verification={}'.format(
                    logTypeID,
                    stockStorageID,
                    change,
                    description,
                    verification,
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_stock_storage_log,
                        (
                            int(logTypeID),
                            str(change),
                            str(description),
                            verification.get_verification(),
                            int(stockStorageID),
                            int(stockStorageID),
                            int(stockStorageID),
                            int(stockStorageID),
                            int(stockStorageID),
                            int(stockStorageID),
                            int(stockStorageID),
                            int(stockStorageID),
                        ),
                    )
                    if len(sql.table) != 0:
                        self.LOG.info("log_stock_storage: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the insert_stock_storage_log query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_stock_storage: error={}".format(e))

        self.LOG.info("log_stock_storage: END")
        return -1

    # gets all stock actions including inactive stock actions
    # input: N/A
    # output: [stock_actions] on success, [] on error
    def get_all_stock_actions(self) -> list:
        try:
            self.LOG.info("get_all_stock_actions: BEGIN")

            # define stock_actions info
            stock_actions = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stock_actions)
                if len(sql.table) != 0:
                    stock_actions = sql.table
                else:
                    raise Exception(
                        "No results found with the get_stock_actions query!"
                    )

        except Exception as e:
            self.LOG.error("get_all_stock_actions: error={}".format(e))
            self.LOG.info("get_all_stock_actions: END")
            return []

        self.LOG.info(
            "get_all_stock_actions: stock_actions={}".format(str(stock_actions))
        )
        self.LOG.info("get_all_stock_actions: END")
        return stock_actions  # no error

    # gets all active stock actions
    # input: N/A
    # output: [stock_actions] on success, [] on error
    def get_stock_actions_active(self) -> list:
        try:
            self.LOG.info("get_stock_actions_active: BEGIN")

            # define stock_actions info
            stock_actions = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_active_stock_actions)
                if len(sql.table) != 0:
                    stock_actions = sql.table
                else:
                    raise Exception(
                        "No results found with the get_active_stock_actions query!"
                    )

        except Exception as e:
            self.LOG.error("get_stock_actions_active: error={}".format(e))
            self.LOG.info("get_stock_actions_active: END")
            return []

        self.LOG.info(
            "get_stock_actions_active: stock_actions={}".format(str(stock_actions))
        )
        self.LOG.info("get_stock_actions_active: END")
        return stock_actions  # no error

    # Gets all stock action by ID
    # input: N/A
    # output: [stock_actions] on success, [] on error
    def get_stock_action_by_action_id(self, stockID: int) -> list:
        try:
            # define stock_actions info
            stock_actions = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stock_action_by_ID, (stockID,))
                if len(sql.table) != 0:
                    stock_actions = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_stock_actions query!"
                    )

        except Exception as e:
            self.LOG.error("get_all_stock_actions: error={}".format(e))
            self.LOG.info("get_all_stock_actions: END")
            return []

        self.LOG.info(
            "get_all_stock_actions: stock_actions={}".format(str(stock_actions))
        )
        self.LOG.info("get_all_stock_actions: END")
        return stock_actions  # no error

    # Gets stock action by barcode
    # input: barcode
    # output: stock action info. error on -1
    def get_stock_action_by_barcode(self, barcode: str) -> object:
        try:
            # define stock_action info
            stock_action = -1

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stock_action_by_Barcode, (barcode,))
                if len(sql.table) != 0:
                    stock_action = sql.table[0]
                else:
                    raise Exception(
                        "No results found with the get_stock_action_by_barcode query!"
                    )

        except Exception as e:
            self.LOG.error("get_stock_action_by_barcode: error={}".format(e))
            self.LOG.info("get_stock_action_by_barcode: END")
            return -1

        self.LOG.info(
            "get_stock_action_by_barcode: stock_actions={}".format(stock_action)
        )
        self.LOG.info("get_stock_action_by_barcode: END")
        return stock_action  # no error

    # Gets stock action by locations
    # input: locations
    # output: stock action info. error on -1
    def get_stock_action_by_locations(self, locations) -> list:
        try:
            self.LOG.info(f"get_stock_action_by_locations: BEGIN locations={locations}")
            # define stock_action info
            stock_action = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_stock_action_by_Location,
                    (
                        locations,
                        locations,
                    ),
                )
                if len(sql.table) != 0:
                    stock_action = sql.table
                else:
                    raise Exception(
                        "No results found with the get_stock_action_by_locations query!"
                    )

        except Exception as e:
            self.LOG.error("get_stock_action_by_locations: error={}".format(e))
            self.LOG.info("get_stock_action_by_locations: END")
            return []
        self.LOG.info(
            "get_stock_action_by_locations: stock_actions={}".format(stock_action)
        )
        self.LOG.info("get_stock_action_by_locations: END")
        return stock_action  # no error

    # Creates a stock action
    # input: verification, description, barcode, createBy, verification
    # output: Stock action on success, -1 on error
    def create_stock_action(
        self,
        name: str,
        description: str,
        barcode: str,
        priority: int,
        customerID: str,
        locationID: int,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                f'insert_stock: name={name} verification="{verification}"  description="{description}" barcode={barcode} priority={priority} customerID={customerID} locationID={locationID}'
            )

            stockActionID = -1

            # run employee check
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # continue on
                with SQL_Pull()(self.sql_config)() as sql:
                    # custom barcode
                    if barcode is not None:
                        sql.execute(
                            self.insert_stock_action,
                            (
                                name,
                                description,
                                priority,
                                customerID,
                                verification.get_verification(),
                                barcode,
                                locationID,
                            ),
                        )
                    # auto generate barcode
                    else:
                        sql.execute(
                            self.insert_stock_action_auto_barcode,
                            (
                                name,
                                description,
                                priority,
                                customerID,
                                verification.get_verification(),
                                locationID,
                            ),
                        )
                    if len(sql.table) != 0:
                        stockActionID = int(sql.table[0]["ID"])

                    else:
                        raise Exception(
                            "No results found with the insert_stock_action query!"
                        )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_stock_action: error={}".format(e))
            self.LOG.info("create_stock_action: END")
            return -1  # other error

        self.LOG.info("create_stock_action: stockID={}".format(stockActionID))
        self.LOG.info("create_stock_action: END")
        return stockActionID  # no error

    # Update a stock action
    # input: name, description, barcode, createBy, verification
    # output: Stock action on success, -1 on error
    def update_stock_action_info(
        self,
        actionID: int,
        name: str,
        description: str,
        priority: int,
        locationID,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                f'update_stock_action_info: actionID={actionID} name="{name}" description="{description}" priority={priority} locationID={locationID} createBy={verification}'
            )

            stockActionID = -1

            # run employee check
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # continue on
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.update_stock_action,
                        (
                            name,
                            description,
                            priority,
                            locationID,
                            actionID,
                        ),
                    )
                    if len(sql.table) != 0:
                        stockActionID = int(sql.table[0]["ID"])

                    else:
                        raise Exception(
                            "No results found with the update_stock_action_info query!"
                        )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_stock_action_info: error={}".format(e))
            self.LOG.info("update_stock_action_info: END")
            return -1  # other error

        self.LOG.info("update_stock_action_info: stockID={}".format(stockActionID))
        self.LOG.info("update_stock_action_info: END")
        return stockActionID  # no error

    # Removes a stock action
    # input: verification, stockStorageID
    # output: 0 on success, -1 on error
    def delete_stock_action(
        self, verification: Verification, stockActionID: int
    ) -> int:
        try:
            self.LOG.info(
                "delete_stock_action: stockActionID={}".format(
                    stockActionID,
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.remove_stock_action, (int(stockActionID)))
                    if len(sql.table) != 0:
                        self.LOG.info("remove_stock_action: END")

                        return 0
                    else:
                        raise Exception(
                            "No results found with the remove_stock_action query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("delete_stock_action: error={}".format(e))

        self.LOG.info("delete_stock_action: END")
        return -1

    # gets links by action
    # input: actionID
    # output: [links] on success, [] on error
    def get_links_by_action_ID(self, actionID: int) -> list:
        try:
            self.LOG.info(f"get_links_by_action_ID: actionID={actionID}")

            # define stock_links info
            stock_links = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_links_by_action, (int(actionID)))
                if len(sql.table) != 0:
                    stock_links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_links_by_action query!"
                    )

        except Exception as e:
            self.LOG.error("get_links_by_action_ID: error={}".format(e))
            self.LOG.info("get_links_by_action_ID: END")
            return []

        self.LOG.info("get_links_by_action_ID: stock_links={}".format(str(stock_links)))
        self.LOG.info("get_links_by_action_ID: END")
        return stock_links  # no error

    # gets stock type action links by action
    # input: actionID
    # output: [links] on success, [] on error
    def get_stock_type_action_links_by_action_ID(self, actionID: int) -> list:
        try:
            self.LOG.info(
                f"get_stock_type_action_links_by_action_ID: actionID={actionID}"
            )

            # define stock_links info
            stock_links = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_stock_type_action_links_by_action,
                    (
                        actionID,
                        actionID,
                    ),
                )
                if len(sql.table) != 0:
                    stock_links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_stock_type_action_links_by_action_ID query!"
                    )

        except Exception as e:
            self.LOG.error(
                "get_stock_type_action_links_by_action_ID: error={}".format(e)
            )
            self.LOG.info("get_stock_type_action_links_by_action_ID: END")
            return []

        self.LOG.info(
            "get_stock_type_action_links_by_action_ID: stock_links={}".format(
                str(stock_links)
            )
        )
        self.LOG.info("get_stock_type_action_links_by_action_ID: END")
        return stock_links  # no error

    # gets stock type action links by action barcode
    # input: action barcode
    # output: [links] on success, [] on error
    def get_stock_type_action_links_by_action_barcode(self, barcode: str) -> list:
        try:
            self.LOG.info(
                f"get_stock_type_action_links_by_action_barcode: barcode={barcode}"
            )

            # define stock_links info
            stock_links = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stock_action_links_by_barcode, (barcode,))
                if len(sql.table) != 0:
                    stock_links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_stock_type_action_links_by_action_barcode query!"
                    )

        except Exception as e:
            self.LOG.error(
                "get_stock_type_action_links_by_action_barcode: error={}".format(e)
            )
            self.LOG.info("get_stock_type_action_links_by_action_barcode: END")
            return []

        self.LOG.info(
            "get_stock_type_action_links_by_action_barcode: stock_links={}".format(
                str(stock_links)
            )
        )
        self.LOG.info("get_stock_type_action_links_by_action_barcode: END")
        return stock_links  # no error

    # Links a stock with a action
    # input: ActionID, StockID, Count, CreatedBy
    # output: stockactionlink, -1 on error
    def create_stock_action_link(
        self,
        actionID: int,
        stockID: int,
        count: int,
        verification: Verification,
        initial: int | None = None,
        destination: int | None = None,
    ) -> int:
        try:
            self.LOG.info(
                f"create_stock_action_link: actionID={actionID} stockID={stockID} count={count} initialLocation={initial} destinationLocation={destination} verification={verification}"
            )

            stock_action_link = []

            # run employee check
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # continue on
                if initial == None:
                    initial = "null"
                if destination == None:
                    destination = "null"
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.link_stock_with_action,
                        (
                            int(actionID),
                            int(stockID),
                            int(count),
                            verification.get_verification(),
                            initial,
                            destination,
                        ),
                    )
                    if len(sql.table) != 0:
                        stock_action_link = int(sql.table[0]["ID"])

                    else:
                        raise Exception(
                            "No results found with the link_stock_with_action query!"
                        )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_stock_action_link: error={}".format(e))
            self.LOG.info("create_stock_action_link: END")
            return -1  # other error

        self.LOG.info("create_stock_action_link: stockID={}".format(stock_action_link))
        self.LOG.info("create_stock_action_link: END")
        return stock_action_link  # no error

    # bulk Creates stock action links
    # input: actionID, empID, list of linkStocks [{stockID: int, initial: int, destination: int, count: int},{...},...]
    # # output: Stock action on success, -1 on error
    def bulk_create_stock_action_links(
        self,
        actionID: int,
        verification: Verification,
        linkStocks: list,
    ) -> list:
        try:
            self.LOG.info(
                f'insert_stock_action_link_bulk: actionID="{actionID}"  verification="{verification}" linkStocks={linkStocks}'
            )

            action_links = []

            # run employee check
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # continue on
                with SQL_Pull()(self.sql_config)() as sql:
                    stockIDs = ",".join([str(item["stockID"]) for item in linkStocks])
                    initials = ",".join([str(item["initial"]) for item in linkStocks])
                    destinations = ",".join(
                        [str(item["destination"]) for item in linkStocks]
                    )
                    counts = ",".join([str(item["count"]) for item in linkStocks])
                    sql.execute(
                        self.bulk_insert_stock_type_action_links,
                        (
                            actionID,
                            verification.get_verification(),
                            11,
                            initials,
                            destinations,
                            stockIDs,
                            counts,
                        ),
                    )
                    if len(sql.table) != 0:
                        action_links = sql.table

                    else:
                        raise Exception(
                            "No results found with the bulk_create_stock_action_links query!"
                        )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("bulk_create_stock_action_links: error={}".format(e))
            self.LOG.info("bulk_create_stock_action_links: END")
            return []  # other error

        self.LOG.info(
            "bulk_create_stock_action_links: action_links={}".format(action_links)
        )
        self.LOG.info("bulk_create_stock_action_links: END")
        return action_links  # no error

    # Update a stock action link
    # input: verification, stockLinkID
    # output: 0 on success, -1 on error
    def update_stock_action_link_info(
        self,
        verification: Verification,
        actionLinkID: int,
        count: int,
        initialLocation: int,
        destinationLocation: int,
    ) -> int:
        try:
            self.LOG.info(
                "update_stock_action_link_info: verification={} actionLinkID={}  count={}  initialLocation={}  destinationLocation={} ".format(
                    verification,
                    actionLinkID,
                    count,
                    initialLocation,
                    destinationLocation,
                )
            )
            info = -1
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_stock_action_link,
                        (count, initialLocation, destinationLocation, actionLinkID),
                    )
                    if len(sql.table) != 0:
                        self.LOG.info("update_stock_action_link_info: END")
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "No results found with the update_stock_action_link_info query!"
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("update_stock_action_link_info: error={}".format(e))
            return -1

        self.LOG.info("update_stock_action_link_info: END")
        return info

    # Removes a stock action link
    # input: verification, stockLinkID
    # output: 0 on success, -1 on error
    def delete_stock_action_link(
        self, verification: Verification, stockLinkID: int
    ) -> int:
        try:
            self.LOG.info(
                "delete_stock_action_link: stockLinkID={}".format(
                    stockLinkID,
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.remove_stock_action_link, (int(stockLinkID)))
                    if len(sql.table) != 0:
                        self.LOG.info("remove_stock_action_link: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the remove_stock_action_link query!"
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("delete_stock_action_link: error={}".format(e))

        self.LOG.info("delete_stock_action_link: END")
        return -1

    # Gets all stock storages by each ID
    # input: N/A
    # output: [stock_storages] on success, [] on error
    def get_stock_storage_by_ids(self) -> int:
        try:
            # define stock_links info
            stock_storages = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_stock_storage_by_each_id)
                if len(sql.table) != 0:
                    stock_storages = sql.table
                else:
                    raise Exception(
                        "No results found with the get_stock_storage_by_each_id query!"
                    )

        except Exception as e:
            self.LOG.error("get_stock_storage_by_ids: error={}".format(e))
            self.LOG.info("get_stock_storage_by_ids: END")
            return []

        self.LOG.info(
            "get_stock_storage_by_ids: stock_storages={}".format(len(stock_storages))
        )
        self.LOG.info("get_stock_storage_by_ids: END")
        return stock_storages  # no error

    # Update Stocks statuses
    # input: verification, stocks
    # output: 1 or -1
    def bulk_update_stocks_status(self, verification, stocks) -> int:
        info = -1
        try:
            self.LOG.info(
                "update_stocks_status: stocks={} verification={} ".format(
                    stocks, verification
                )
            )

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    for stk in stocks:
                        sql.execute(
                            self.bulk_update_status_stocks,
                            (
                                stk["location"],
                                stk["fromStatus"],
                                stk["toStatus"],
                                stk["quantity"],
                                stk["ID"],
                            ),
                        )

                        locations = self.locations.get_locations_by_status()
                        location = (
                            location["Location"]
                            for location in locations
                            if location["ID"] == int(stk["location"])
                        )

                        self.log_stock_type(
                            stk["ID"],
                            "stock_checkout",
                            verification,
                            "Checkout "
                            + str(stk["quantity"])
                            + " items from "
                            + next(location, ""),
                            59,
                        )
                    info = 1
            else:
                raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("update_stocks_status: error={}".format(e))
            return -1
        self.LOG.info("update_stocks_status: END")
        return info


# UNIT TESTING


def main():
    return


if __name__ == "__main__":
    main()
