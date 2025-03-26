#!/usr/bin/env python3.7
import logging
from typing import List, Dict
import json
import os

from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .laser_config import KeyenceLaserConfig
from .employee_pull import Employee
from .aligner_pull import Aligner
from .case_pull import Case
from .gauge_pull import Gauge


# Set up logger
LOG = logging.getLogger("laser_pull")
# path = "{}/logs/laser_pull.log".format(os.getcwd())
# file_handler = logging.FileHandler(path)
console_handler = logging.StreamHandler()
formatter = logging.Formatter(
    "%(asctime)s %(levelname)s %(process)d %(filename)s:%(lineno)d %(message)s"
)
# file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)
# LOG.addHandler(file_handler)
LOG.addHandler(console_handler)
LOG.setLevel(logging.INFO)


class KeyenceLaser(KeyenceLaserConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        KeyenceLaserConfig.__init__(self, sql_config)

        # Create a case object
        self.cas = Case()

        # initialize gauge
        self.gauge = Gauge()

        # Create an employee object
        self.emp = Employee()

        # Create aligner object
        self.alg = Aligner()

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

    def blk_req_placement(
        self,
        alignerIDs: list,
        product: str | None = None,
        customer: str | None = None,
        profile: str = "Default",
    ) -> dict:
        try:
            self.LOG.info("blk_req_placement: alignerIDs={}".format(alignerIDs))

            # define return value
            blks = {}

            # get aligner object
            if product is None or customer is None:
                # get aligner from endpoint
                aligners = self.alg.get_aligners_by_ids(alignerIDs)
                # check aligner
                if len(aligners) == 0:
                    raise Exception(
                        "The acquired aligner information fails to contain any data!"
                    )

            # for each aligner get blk replacement set
            for aligner in aligners:
                # define alignerID
                alignerID = aligner["AlignerID"]

                # get product from aligner
                if product is None:
                    product = aligner["ProductID"]

                # get customerID from case of aligner
                if customer is None:
                    customer = aligner["CustomerID"]

                # check profile
                if profile not in self.blks_placement.keys():
                    profile = "Default"
                    if "Default" not in self.blks_placement.keys():
                        raise Exception(
                            "Default profile not found in customer profile set!"
                        )

                # check if customer is in keys of customers
                if customer not in self.blks_placement[profile].keys():
                    customer = "Default"
                    if "Default" not in self.blks_placement[profile].keys():
                        raise Exception("Default customer not found in profile set!")
                self.LOG.info('blk_req_placement: customer="{}"'.format(customer))

                # check if product from alignerID is found in customer profile
                if product not in self.blks_placement[profile][customer].keys():
                    product = "Default"
                    if "Default" not in self.blks_placement[profile][customer].keys():
                        raise Exception("Default customer's default profile not found!")
                self.LOG.info('blk_req_placement: product="{}"'.format(product))

                # set blks
                blks[alignerID] = self.blks_placement[profile][customer][product]

            self.LOG.info("blk_req_placement: SUCCESS")
            return blks
        except Exception as e:
            self.LOG.error("blk_req_placement: error={}".format(e))
        self.LOG.info("blk_req_placement: FAILURE")
        return {}

    def generate_klps(
        self,
        alignerIDs: list,
        customer: str | None = None,
        product: str | None = None,
        profile: str = "Default",
        alg_blks: dict = {},
        gaugeID: int | None = None,
    ) -> dict:
        """
        Gets the klps for a given set of alignerIDs through customer, product, and profile matching.
        Parameters:
            - alignerIDs -> [1142, 3332, 4443]
            - customer -> "Default"
            - product -> "Default"
            - profile -> "Default"
            - alg_blks -> {"1142": {"0": {"value": "test", "x": 0, "y": 100, "z": 0, "theta": 0} ...} ...}
            - gauegID -> 0
        """
        try:
            self.LOG.info(
                "generate_klps: alignerIDs={} customer={} product={} profile={} alg_blks={} gaugeID={}".format(
                    alignerIDs, customer, product, profile, alg_blks, gaugeID
                )
            )

            # get aligner object
            if product is None or customer is None:
                # get aligner from endpoint
                temp = self.alg.get_aligners_by_ids(alignerIDs)
                # check aligner
                if len(temp) == 0:
                    raise Exception(
                        "The acquired aligner information fails to contain any data for the given alignerIDs!"
                    )

                # loop through and build a dictionary
                aligners = {}
                for aligner in temp:
                    # there are no two alignerIDs that are the same, replace existing alignerID with most recent provided
                    aligners[aligner["AlignerID"]] = aligner

            # get each aligners aligner info
            klps = {}
            for i, alignerID in enumerate(alignerIDs):
                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    LOG,
                    "generate_klps",
                    index=i,
                    length=len(alignerIDs),
                    limit=100,
                    label="Getting {}".format(alignerID),
                )

                # get product from aligner
                if product is None:
                    if alignerID not in aligners.keys():
                        product = "Default"
                    else:
                        product = aligners[alignerID]["ProductID"]

                # get customerID from case of aligner
                if customer is None:
                    if alignerID not in aligners.keys():
                        customer = "Default"
                    else:
                        customer = aligners[alignerID]["CustomerID"]

                # get override for given aligner
                blks = {}
                if str(alignerID) in alg_blks.keys():
                    blks = alg_blks[str(alignerID)]
                # generate the klp
                klps[alignerID] = self.generate_klp(
                    alignerID,
                    profile=profile,
                    product=product,
                    customer=customer,
                    blks=blks,
                )

            # update gauge
            self.gauge.update_gauge(
                gaugeID,
                LOG,
                "generate_klps",
                index=0,
                length=1,
                limit=100,
                constant=100,
                label="Complete",
            )

            self.LOG.info("generate_klps: SUCCESS")
            return klps
        except Exception as e:
            self.LOG.error("generate_klps: error={}".format(e))
        self.LOG.info("generate_klps: FAILURE")
        return []

    # given provided blks, adds and removes blks based on customer requirements
    # given an already existing file
    def generate_klp(
        self,
        alignerID: int,
        profile: str = "Default",
        product: str | None = None,
        customer: str | None = None,
        blks: dict = {},
    ) -> dict:
        try:
            self.LOG.info(
                "generate_klp: alignerID={} profile={} product={} customer={} blks={}".format(
                    alignerID, profile, product, customer, blks
                )
            )

            # get aligner object
            if product is None or customer is None:
                # get aligner from endpoint
                aligner = self.alg.get_aligner_by_id(alignerID)
                # check aligner
                if len(aligner) == 0:
                    raise Exception(
                        "The acquired aligner information fails to contain any data!\n{0}".format(
                            alignerID
                        )
                    )

            # get product from aligner
            if product is None:
                product = aligner[0]["ProductID"]

            # get customerID from case of aligner
            if customer is None:
                customer = aligner[0]["CustomerID"]

            # check if profile is in customer keys
            if profile not in self.customers.keys():
                profile = "Default"
                if "Default" not in self.customers.keys():
                    raise Exception(
                        "Default profile for customer profile set not found"
                    )

            # check if customer is in keys of customers
            if customer not in self.customers[profile].keys():
                customer = "Default"
                if "Default" not in self.customers[profile].keys():
                    raise Exception(
                        "Default customer for customer profile set not found!"
                    )
            self.LOG.info('generate_klp: customer="{}"'.format(customer))

            # check if product from alignerID is found in customer profile
            if product not in self.customers[profile][customer].keys():
                product = "Default"
                if "Default" not in self.customers[profile][customer].keys():
                    raise Exception("Default product for customer profile not found!")
            self.LOG.info('generate_klp: product="{}"'.format(product))

            # create each blk if they dont already exist given customer and
            # product or in the blk already
            for blk in self.customers[profile][customer][product].keys():
                if blk not in blks.keys():
                    blks[blk] = {}

            # for blk in our imported blks
            # adjust the values for each blk given customer and product
            with SQL_Pull()(self.sql_config)() as sql:
                tobepop = []
                for blk in blks.keys():
                    self.LOG.info("generate_klp: blk={}".format(blk))

                    # if the blk is found in our customer profile
                    if blk in self.customers[profile][customer][product].keys():
                        for key in self.customers[profile][customer][product][
                            blk
                        ].keys():
                            # define default
                            key_val = None
                            if key in blks[blk].keys():
                                key_val = blks[blk][key]
                            blks[blk][key] = key_val

                            # only update value if it doesnt exist already and the value is None
                            if key == "value" and blks[blk][key] is None:
                                # get the key_val based on the commands given from the customer profile
                                if (
                                    self.customers[profile][customer][product][blk][key]
                                    in self.commands.keys()
                                ):
                                    # get command to be run
                                    command = self.commands[
                                        self.customers[profile][customer][product][blk][
                                            key
                                        ]
                                    ]

                                    # execute command
                                    sql.execute(command, (alignerID))
                                    key_val = sql.table[0]["Result"]
                                    # make sure we get a response
                                    if len(key_val) == 0:
                                        raise Exception(
                                            "No value returned from command {}! \
                                                Please check to make sure format is correct and only alignerID is present as a parameter!".format(
                                                command
                                            )
                                        )
                                else:
                                    # else default to what is in the value field
                                    key_val = self.customers[profile][customer][
                                        product
                                    ][blk][key]

                            # only update x,y,z,theta if value is None
                            elif blks[blk][key] is None:
                                # else default to whatever the key is as the
                                # value
                                key_val = self.customers[profile][customer][product][
                                    blk
                                ][key]

                            # set new key_val for specific key
                            blks[blk][key] = key_val
                            self.LOG.info("generate_klp: {}={}".format(key, key_val))

                        # remove blks in removal list
                        if blk in self.blk_removal.keys():
                            for key in self.blk_removal[blk]:
                                if key in blks[blk]:
                                    blks[blk].pop(key)
                                    self.LOG.info("generate_klp: popped={}".format(key))

                    # blk was not found in the customer profile
                    else:
                        # append the blk that isnt found in the customer profile
                        tobepop.append(blk)

                        self.LOG.info("generate_klp: popped={}".format(blk))

                # pop the blks in tobepop
                for tobe in tobepop:
                    blks.pop(tobe)

            return blks
        except Exception as e:
            self.LOG.error("generate_klp: error={}".format(e))
        self.LOG.info("generate_klp: FAILURE")
        return {}


# UNIT TESTING


def main():
    return


if __name__ == "__main__":
    main()
