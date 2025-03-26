#!/usr/bin/env python3.7

import json
from os import link, getenv
from typing import List, Dict
from datetime import date

from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .shade_regex import gen_steps
from .product_config import ProductConfig
from .verification_pull import Verification
import requests


class Product(ProductConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        ProductConfig.__init__(self, sql_config)

        # Current working values
        result = []
        with SQL_Pull()(self.sql_config)() as sql:
            result, _ = sql.execute(self.get_status)
            for stat in result:
                self.statuses[stat["ID"]] = stat["StatusType"]

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    def create_kit(
        self,
        catalog: str,
        customerID: str,
        productID: str,
        name: str,
        description: str,
        verification: Verification,
    ) -> list:
        try:
            self.LOG.info(
                "create_kit: catalog={} customerID={} productID={} name={} description={} verification={}".format(
                    catalog, customerID, productID, name, description, verification
                )
            )

            kit = []

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_product_kit,
                        (
                            catalog,
                            customerID,
                            productID,
                            name,
                            description,
                            verification.get_verification(),
                        ),
                    )
                    if len(sql.table) > 0:
                        kit = sql.table
                else:
                    raise Exception("Invalid Verification!")

        except Exception as e:
            self.LOG.error("create_kit: error={}".format(e))
            self.LOG.info("create_kit: END")
            return []  # other error

        self.LOG.info("create_kit: kits={}".format(kit))
        self.LOG.info("create_kit: END")
        return kit  # no error

    # # Create Kit File Link
    # Input: KitID ,FileID , CreatedBy
    def create_new_kit_file_link(
        self, kitID: int, files: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "create_new_kit_file_link: kitID={} files={} verification={}".format(
                    kitID, files, verification
                )
            )

            result = []

            if kitID is not None and files is not None:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    with SQL_Pull()(self.sql_config)() as sql:
                        for file in files:
                            # define default values
                            if "OrderID" not in file.keys():
                                file["OrderID"] = 0
                            if "Description" not in file.keys():
                                file["Description"] = ""

                            sql.execute(
                                self.insert_product_kit_file_link,
                                (
                                    kitID,
                                    file["FileID"],
                                    file["typeID"],
                                    verification.get_verification(),
                                    file["OrderID"],
                                    file["Description"],
                                ),
                            )
                            if len(sql.table) > 0:
                                result.extend(sql.table)
                else:
                    raise Exception("Invalid Verification!")
            else:
                raise Exception("Missing Inputs!")

        except Exception as e:
            self.LOG.error("create_new_kit_file_link: error={}".format(e))
            return []

        self.LOG.info("create_new_kit_file_link: result={}".format(result))
        self.LOG.info("create_new_kit_file_link: END")
        return result

    def get_product_kits(self, products: list = []) -> list:
        try:
            self.LOG.info("get_product_kits: products={}".format(products))

            kits = []

            with SQL_Pull()(self.sql_config)() as sql:
                product_list = ",".join(map(str, products))
                if len(products) > 0:
                    sql.execute(self.get_product_kits_by_products, (product_list))
                else:
                    sql.execute(self.get_all_product_kits)
                if len(sql.table) != 0:
                    kits = sql.table
                else:
                    raise Exception(
                        "No results found with the get_product_kits_by_products query!"
                    )

        except Exception as e:
            self.LOG.error("get_product_kits: error={}".format(e))
            self.LOG.info("get_product_kits: END")
            return []  # other error

        self.LOG.info("get_product_kits: kits={}".format(kits))
        self.LOG.info("get_product_kits: END")
        return kits  # no error

    def get_file_links_by_kits(self, kits: list) -> list:
        try:
            self.LOG.info("get_file_links_by_kits: kits={}".format(kits))

            files = []
            with SQL_Pull()(self.sql_config)() as sql:
                kit_list = ",".join(map(str, kits))
                sql.execute(self.get_product_kit_file_links_by_kits, (kit_list))
                if len(sql.table) != 0:
                    files = sql.table
                else:
                    raise Exception(
                        "No results found with the get_product_kit_file_links_by_kits query!"
                    )

        except Exception as e:
            self.LOG.error("get_file_links_by_kits: error={}".format(e))
            self.LOG.info("get_file_links_by_kits: END")
            return []  # other error

        self.LOG.info("get_file_links_by_kits: files={}".format(files))
        self.LOG.info("get_file_links_by_kits: END")
        return files  # no error

    def update_kit_file_link_orderID_and_description(
        self, verification: Verification, links: dict
    ) -> list:
        try:
            self.LOG.info(
                "update_kit_file_link_orderID_and_description: verification={} links={}".format(
                    verification, links
                )
            )

            result = []

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_product_kit_file_link_order_and_description,
                        (json.dumps(links)),
                    )
                    if len(sql.table) != 0:
                        result = sql.table
                    else:
                        raise Exception(
                            "No results found with the update_product_kit_file_link_order_and_description query!"
                        )
                else:
                    raise Exception("Invalid Verification!")

        except Exception as e:
            self.LOG.error(
                "update_kit_file_link_orderID_and_description: error={}".format(e)
            )
            self.LOG.info("update_kit_file_link_orderID_and_description: END")
            return []  # other error

        self.LOG.info(
            "update_kit_file_link_orderID_and_description: result={}".format(result)
        )
        self.LOG.info("update_kit_file_link_orderID_and_description: END")
        return result  # no error

    def update_kit_file_link_status(
        self, verification: Verification, links: list, status: int = 12
    ) -> list:
        try:
            self.LOG.info(
                "update_product_kit_status: verification={} links={} status={}".format(
                    verification, links, status
                )
            )

            result = []

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    kit_list = ",".join(map(str, links))
                    sql.execute(
                        self.update_product_kit_file_link_status, (status, kit_list)
                    )
                    if len(sql.table) != 0:
                        result = sql.table
                    else:
                        raise Exception(
                            "No results found with the update_product_kit_file_link_status query!"
                        )
                else:
                    raise Exception("Invalid Verification!")

        except Exception as e:
            self.LOG.error("update_product_kit_status: error={}".format(e))
            self.LOG.info("update_product_kit_status: END")
            return []  # other error

        self.LOG.info("update_product_kit_status: result={}".format(result))
        self.LOG.info("update_product_kit_status: END")
        return result  # no error

    def update_kit_status(
        self, verification: Verification, kits: list, status: int = 12
    ) -> list:
        try:
            self.LOG.info(
                "update_kit_status: verification={} kits={} status={}".format(
                    verification, kits, status
                )
            )

            result = []

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    kit_list = ",".join(map(str, kits))
                    sql.execute(self.update_product_kit_status, (status, kit_list))
                    if len(sql.table) != 0:
                        result = sql.table
                    else:
                        raise Exception(
                            "No results found with the update_product_kit_status query!"
                        )
                else:
                    raise Exception("Invalid Verification!")

        except Exception as e:
            self.LOG.error("update_kit_status: error={}".format(e))
            self.LOG.info("update_kit_status: END")
            return []  # other error

        self.LOG.info("update_kit_status: result={}".format(result))
        self.LOG.info("update_kit_status: END")
        return result  # no error

    def get_products_of_case(self, case: str) -> list:
        try:
            self.LOG.info("get_products_of_case: case={}".format(case))

            products = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_case_products_by_case, (case))
                if len(sql.table) != 0:
                    products = sql.table
                else:
                    raise Exception(
                        "No results found with the get_case_products_by_case query!"
                    )

        except Exception as e:
            self.LOG.error("get_products_of_case: error={}".format(e))
            self.LOG.info("get_products_of_case: END")
            return []  # other error

        self.LOG.info("get_products_of_case: products={}".format(products))
        self.LOG.info("get_products_of_case: END")
        return products  # no error

    def get_products_of_catalog(self, catalog: str) -> list:
        try:
            self.LOG.info("get_products_of_catalog: catalog={}".format(catalog))

            products = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_products_by_customer_catalog, (catalog))
                if len(sql.table) != 0:
                    products = sql.table
                else:
                    raise Exception(
                        "No results found with the get_products_by_customer_catalog query!"
                    )

        except Exception as e:
            self.LOG.error("get_products_of_catalog: error={}".format(e))
            self.LOG.info("get_products_of_catalog: END")
            return []  # other error

        self.LOG.info("get_products_of_catalog: products={}".format(products))
        self.LOG.info("get_products_of_catalog: END")
        return products  # no error

    def get_product_by_id(self, productID: str) -> list:
        try:
            self.LOG.info("get_product_by_id: productID={}".format(productID))

            products = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_product_by_ID, (productID))
                if len(sql.table) != 0:
                    products = sql.table
                else:
                    raise Exception(
                        "No results found with the get_product_by_ID query!"
                    )

        except Exception as e:
            self.LOG.error("get_product_by_id: error={}".format(e))
            self.LOG.info("get_product_by_id: END")
            return []  # other error

        self.LOG.info("get_product_by_id: products={}".format(products))
        self.LOG.info("get_product_by_id: END")
        return products  # no error

    # pulls an aligner's data from a particular station
    # input: AlignerID
    # output: Products on success, [] on error
    def get_products_by_aligner(self, alignerID: int) -> list:
        try:
            self.LOG.info("get_products_by_aligner: alignerID={}".format(alignerID))

            products = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_product_by_alignerID, (alignerID))
                if len(sql.table) != 0:
                    products = sql.table
                else:
                    raise Exception(
                        "No results found with the get_product_by_alignerID query!"
                    )

        except Exception as e:
            self.LOG.error("get_products_by_aligner: error={}".format(e))
            self.LOG.info("get_products_by_aligner: END")
            return []  # other error

        self.LOG.info("get_product_ref_by_id: products={}".format(products))
        self.LOG.info("get_product_ref_by_id: END")
        return products  # no error

    def get_product_catalogs(self) -> list:
        try:
            self.LOG.info("get_products: START")

            result = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_all_products_by_catalogs,
                )
                if len(sql.table) != 0:
                    result = sql.table
                else:
                    raise Exception("No results found with the get_products query!")

            # initialize return variable
            final_obj = {}

            # Replace all null customerIDs with "Default" to match current return
            for instance in result:
                # replace all null labs to "Default"
                if instance["Catalog"] is None:
                    instance["Catalog"] = "Default"
                # replace all null customers to "Default"
                if instance["CustomerID"] is None:
                    instance["CustomerID"] = "Default"

            # create final_obj
            for instance in result:
                catalog = instance["Catalog"]
                customer = instance["CustomerID"]
                product = instance["ProductID"]

                # initialize instance
                if catalog not in final_obj.keys():
                    final_obj[catalog] = {}
                if "Customers" not in final_obj[catalog].keys():
                    final_obj[catalog]["Customers"] = [
                        "Default"
                    ]  # provide a default customer
                if "Products" not in final_obj[catalog].keys():
                    final_obj[catalog]["Products"] = []

                # append instance
                if customer not in final_obj[catalog]["Customers"]:
                    final_obj[catalog]["Customers"].append(customer)
                if product not in final_obj[catalog]["Products"]:
                    final_obj[catalog]["Products"].append(product)

        except Exception as e:
            self.LOG.error("get_products: error={}".format(e))
            self.LOG.info("get_products: END")
            return {}  # other error

        self.LOG.info("get_products: products={}".format(len(final_obj)))
        self.LOG.info("get_products: END")
        return final_obj  # no error

    def get_product_material_types(self) -> list:
        try:
            self.LOG.info("get_products: START")

            products = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_all_product_types,
                )
                if len(sql.table) != 0:
                    products = sql.table
                else:
                    raise Exception("No results found with the get_products query!")

            final_obj = {}

            # Replace all null customerIDs with "Default" to match current return
            fixed_products = map(
                lambda prod: (
                    prod
                    if prod["CustomerID"] != None
                    else {**prod, "CustomerID": "Default"}
                ),
                products,
            )

            for customer in fixed_products:
                # If CustomerID exists as a key
                if customer["CustomerID"] in final_obj:
                    # If ProductID is in the customerID add Type
                    if customer["ProductID"] in final_obj[customer["CustomerID"]]:
                        final_obj[customer["CustomerID"]][customer["ProductID"]].append(
                            customer["Type"]
                        )

                    # Else create ProductID Key and add type
                    else:
                        final_obj[customer["CustomerID"]] = {
                            **final_obj[customer["CustomerID"]],
                            customer["ProductID"]: [customer["Type"]],
                        }

                # Initialize Key with default value and ProductID: Type
                else:
                    final_obj[customer["CustomerID"]] = {
                        "Default": [""],
                        customer["ProductID"]: [customer["Type"]],
                    }

        except Exception as e:
            self.LOG.error("get_products: error={}".format(e))
            self.LOG.info("get_products: END")
            return {}  # other error

        self.LOG.info("get_products: products={}".format(len(final_obj)))
        self.LOG.info("get_products: END")
        return final_obj  # no error

    def get_dlcpm_products(self, verification: Verification) -> list:
        try:
            # Default products
            products = []

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):

                response = requests.get(
                    getenv("MAGIC_TOUCH_URL")
                    + "/Product/GetAllProducts/labID=Phase&token={}".format(
                        getenv("MAGIC_TOUCH_TOKEN")
                    ),
                )

                if response.status_code != 200:
                    raise Exception("Failed to retrieve Magictouch products!")

                products = response.json()

        except Exception as e:
            self.LOG.error("get_dlcpm_products: error={}".format(e))
            self.LOG.info("get_dlcpm_products: END")
            return []  # other error

        self.LOG.info("get_dlcpm_products: products={}".format(products))
        self.LOG.info("get_dlcpm_products: END")
        return products  # no error


# UNIT TESTING


def main():
    return


if __name__ == "__main__":
    main()
