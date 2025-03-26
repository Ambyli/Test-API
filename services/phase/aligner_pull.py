#!/usr/bin/env python3.7

import re
import ntpath
import time
from typing import List, Dict


from .lot_pull import Lot
from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .shade_regex import gen_steps, gen_shade
from .aligner_config import AlignerConfig
from .case_pull import Case
from .location_pull import Location
from .gauge_pull import Gauge
from .bag_pull import Bag
from .token_pull import Token
from .file_pull import File
from .verification_pull import Verification
from .threading_return import ThreadWithReturnValue
from .constants import Endpoints, Parameters, Statuses, Locations, LogTypes
from .carbon_pull import Carbon


class Aligner(AlignerConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        AlignerConfig.__init__(self, sql_config)

        # # Create a case object
        self.cas = Case()

        # # Create a location object
        self.loc = Location()

        # # Create a Bag object
        self.bag = Bag()

        # # initialize gauge
        self.gauge = Gauge()

        # # Create a Token object
        self.tok = Token()

        # # Create a Carbon object
        self.car = Carbon()

        # # initialize files
        self.files = File()

        # Current working values
        result = []
        with SQL_Pull()(self.sql_config)() as sql:
            result, _ = sql.execute(self.get_status)
            for stat in result:
                self.statuses[stat["ID"]] = stat["StatusType"]
            result, _ = sql.execute(self.get_file_types)
            for loc in result:
                self.file_types[loc["ID"]] = loc["Name"]
            result, _ = sql.execute(self.get_log_types)
            for log_type in result:
                self.log_types[log_type["ID"]] = log_type["LogType"]
            result, _ = sql.execute(self.get_severity_types)
            for severity_type in result:
                self.severity_types[severity_type["ID"]] = severity_type["SeverityType"]

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # Matches individual aligners with a given path through a filtering config
    # input: Paths, AlignerIDs, Gauge
    # output: Matches on success, {} on error
    def match_files_with_aligners(
        self,
        paths: list,
        alignerIDs: list,
        gaugeID: int | None = None,
        customer: str | None = None,
    ) -> dict:
        try:
            self.LOG.info(
                "match_files_with_aligners: paths={} alignerIDs={}".format(
                    paths, alignerIDs
                )
            )

            # update gauge
            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "match_files_with_aligners",
                index=0,
                length=1,
                limit=100,
                constant=0,
                label="Initializing",
            )

            # define matches
            matches = {}

            # get each aligners aligner info
            aligners = []
            for i, alignerID in enumerate(alignerIDs):
                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "match_files_with_aligners",
                    index=i,
                    length=len(alignerIDs),
                    limit=50,
                    label="Getting {}".format(alignerID),
                )

                # get aligner info from aligner
                result = self.get_aligner_by_id(alignerID)
                # check result
                if len(result) == 0:
                    raise Exception(
                        "The given aligner {} fails to have any aligner information!".format(
                            alignerID
                        )
                    )
                # set aligner
                # we only get first instance of alignerID as they should be unique
                aligner = result[0]

                # append aligner to aligners
                aligners.append(aligner)

            # go through each aligner and match path
            for i, aligner in enumerate(aligners):
                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "match_files_with_aligners",
                    index=i,
                    length=len(aligners),
                    limit=50,
                    constant=50,
                    label="Matching {}".format(aligner["AlignerID"]),
                )

                # get alignerID
                alignerID = aligner["AlignerID"]
                # get step
                step = aligner["Step"]
                # get product
                product = aligner["ProductID"]
                # get customer
                customer = aligner["CustomerID"]

                # for each path, find a match with the current aligner
                for j, path in enumerate(paths):
                    # convert path with provided step, customer, and product
                    converted, weight = self.path_convert(
                        ntpath.basename(path),
                        customer=customer,
                        product=product,
                    )

                    # check if converted path was a match
                    if len(converted) > 0 and step == converted:
                        if converted not in matches.keys():
                            matches[alignerID] = []
                        # edit ith entry with new converted path
                        matches[alignerID].append(
                            {
                                "Path": path,
                                "Aligner": aligner,
                                "Weight": weight,
                            }
                        )

                        # pop successful path, we dont need it anymore
                        paths.pop(j)

            # run weight adjustment
            matches = self.match_weight_adjustment(matches)

            # update gauge
            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "match_files_with_aligners",
                index=0,
                length=1,
                limit=100,
                constant=100,
                label="Complete",
            )
        except Exception as e:
            self.LOG.error("match_files_with_aligners: error={}".format(e))
            self.LOG.info("match_files_with_aligners: END")
            return {}  # error

        self.LOG.info("match_files_with_aligners: matches={}".format(len(matches)))
        self.LOG.info("match_files_with_aligners: END")
        return matches  # no error

    def match_weight_adjustment(self, matches):
        try:
            self.LOG.info("match_weight_adjustment: matches={}".format(len(matches)))

            # Weight refinement
            # Get all entries for each step and find the max weight
            # deconstructed = map(lambda x: list(map(lambda y: {"Weight": y["Weight"], "Path": y["Path"]}, matches[x]))[0], matches.keys())
            deconstructed = []
            for key in matches.keys():
                for match in matches[key]:
                    deconstructed.append(
                        {"Weight": match["Weight"], "Path": match["Path"]}
                    )
            # Check for matches before getting max of possibly empty list
            weight_list = [value["Weight"] for value in deconstructed]
            max_weight = 0
            if len(weight_list) > 0:
                max_weight = max(weight_list)

            # refine matches
            tobeadded = {}
            while max_weight >= 0:
                # define objects to be removed
                toberemoved = {}

                # find a key that is max
                for key in matches.keys():
                    for index, match in enumerate(matches[key]):
                        if match["Weight"] == max_weight:
                            if key not in tobeadded.keys():
                                tobeadded[key] = []
                            tobeadded[key].append(index)

                # find duplicates that need to be removed for the current weight
                for key in tobeadded.keys():
                    for index in tobeadded[key]:
                        # find duplicates of active_match with a lower weight
                        active_match = matches[key][index]
                        for match_key in matches.keys():
                            for index, match in enumerate(matches[key]):
                                # check if we have already gone over this item in the toberemoved list
                                if (
                                    match_key not in toberemoved.keys()
                                    or index not in toberemoved[match_key]
                                ):
                                    # check if we need to add this item to the to be removed list
                                    if (
                                        match["Path"] == active_match["Path"]
                                        and match["Weight"] < active_match["Weight"]
                                    ):
                                        if key not in toberemoved.keys():
                                            toberemoved[key] = []
                                        toberemoved[key].append(index)

                # remove matches in toberemoved for this current weight selection
                for key in toberemoved.keys():
                    for index in toberemoved[key]:
                        del matches[key][index]

                # descend max_weight
                max_weight -= 1

            # create new matches
            new_matches = {}
            for key in tobeadded.keys():
                for index in tobeadded[key]:
                    if key not in new_matches.keys():
                        new_matches[key] = []
                    new_matches[key].append(matches[key][index])
            matches = dict(sorted(new_matches.items()))

        except Exception as e:
            self.LOG.error("match_weight_adjustment: error={}".format(e))
            self.LOG.info("match_weight_adjustment: END")
            return {}  # error

        self.LOG.info("match_weight_adjustment: matches={}".format(len(matches)))
        self.LOG.info("match_weight_adjustment: END")
        return matches  # no error

    # Returns a list of Steps with their Paths if matched
    # input: Paths, Steps, Customer, ProductID
    # output: Matches on success, [] on error
    def match_paths_to_steps(
        self, paths: list, steps: list, customers: list, products: dict
    ) -> dict:
        try:
            self.LOG.info(
                "match_paths_to_steps: paths={} alignerIDs={} customers={} products={}".format(
                    paths, steps, customers, products
                )
            )

            # define matches
            matches = {}
            # Generate Step matches for each path given
            for customer in customers:
                for product in products:
                    # for each path, find a match with the current aligner
                    for path in paths:
                        # convert path with provided step, customer, and product
                        step_match, weight = self.path_convert(
                            ntpath.basename(path),
                            customer=customer,
                            product=product,
                        )

                        # check if step_match path was a match
                        if len(step_match) > 0 and step_match in steps:
                            if step_match not in matches.keys():
                                matches[step_match] = []
                            # edit ith entry with new step_match path
                            matches[step_match].append(
                                {
                                    "Path": path,
                                    "Customer": customer,
                                    "Product": product,
                                    "Weight": weight,
                                }
                            )

            # run weight adjustment
            matches = self.match_weight_adjustment(matches)

        except Exception as e:
            self.LOG.error("match_paths_to_steps: error={}".format(e))
            self.LOG.info("match_paths_to_steps: END")
            return {}  # error

        self.LOG.info("match_paths_to_steps: matches={}".format(len(matches)))
        self.LOG.info("match_paths_to_steps: END")
        return matches  # no error

    def convert_paths_to_steps(
        self,
        paths: list,
        customers: list = ["Default"],
        products: list = ["Default"],
        gaugeID: int | None = None,
    ) -> list:
        try:
            self.LOG.info(
                "convert_paths_to_steps: paths={} customers={} products={}".format(
                    paths, customers, products
                )
            )

            # initialize predicted result
            results = {}

            # loop through each path
            for i, path in enumerate(paths):
                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "convert_paths_to_steps",
                    index=i,
                    length=len(paths),
                    limit=100,
                )

                # define initial object, attempt in loop because we dont want results updated unless paths exists
                if "Paths" not in results.keys():
                    results["Paths"] = {}

                # find all matches for each customer and product pair
                for customer in customers:
                    for product in products:
                        # convert path
                        result, weight = self.path_convert(path, customer, product)
                        # only add if we get a result
                        if len(result) > 0:
                            # define path object
                            if path not in results["Paths"].keys():
                                results["Paths"][path] = {}
                            # define customer object
                            if customer not in results["Paths"][path].keys():
                                results["Paths"][path][customer] = {}
                            # set results
                            results["Paths"][path][customer][product] = {
                                "Result": result,
                                "Weight": weight,
                            }

        except Exception as e:
            self.LOG.error("convert_paths_to_steps: error={}".format(e))
            self.LOG.info("convert_paths_to_steps: END")
            return {}  # no error

        self.LOG.info("convert_paths_to_steps: results={}".format(len(results)))
        self.LOG.info("convert_paths_to_steps: END")
        return results  # no error

    # Given a path, deconstructs it to represent an aligner's label
    # input: Path, Steps, Customer, Product, Gauge
    # output: Result on success, "" on error
    def path_convert(
        self,
        path: str,
        customer: str = "Default",
        product: str = "Default",
        gaugeID: int | None = None,
    ) -> str:
        try:
            self.LOG.info(
                "path_convert: path={} customer={} product={}".format(
                    path, customer, product
                )
            )

            # initialize predicted result
            result = ""
            weight = 0

            # confirm customer is found in file_match_config dictionary
            if customer not in self.file_match_config.keys():
                self.LOG.info(
                    "path_convert: Customer '{}' not found in file_match_config settings!\nReverting to default profile!".format(
                        customer
                    )
                )
                customer = "Default"
                if "Default" not in self.file_match_config.keys():
                    raise Exception(
                        "Default customer profile set not found in file_match_config settings!"
                    )

            # confirm product is found in customer file_match_config dictionary
            if product not in self.file_match_config[customer].keys():
                self.LOG.info(
                    "path_convert: Product '{}' not found in file_match_config customer '{}' settings!\nReverting to default profile!".format(
                        product, customer
                    )
                )
                product = "Default"
                if "Default" not in self.file_match_config[customer].keys():
                    raise Exception(
                        "Default product profile set not found in file_match_config customer '{}' settings!".format(
                            customer
                        )
                    )
            self.LOG.info('path_convert: product="{}"'.format(product))

            # check if removed is a key in customer, then run removal
            if "Removed" in self.file_match_config[customer][product].keys():
                for pattern in self.file_match_config[customer][product]["Removed"]:
                    path = re.sub(pattern, "", path)
                    self.LOG.info('path_convert: updated: path="{}"'.format(path))

            # pull weight if given
            if "WeightModifier" in self.file_match_config[customer][product].keys():
                weight = self.file_match_config[customer][product]["WeightModifier"]

            # check if identifiers is a key in customer
            if "Identifiers" not in self.file_match_config[customer][product].keys():
                raise Exception(
                    "The customer '{}' and its product '{}' profile in the file_match_config settings contains no Identifiers key!".format(
                        customer, product
                    )
                )

            # get identifiers and perform them in order
            identifiers = self.file_match_config[customer][product]["Identifiers"]

            # deconstruct path
            temp = ""
            for i, identifier in enumerate(identifiers):
                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "path_convert",
                    index=i,
                    length=len(identifiers),
                    limit=100,
                )

                # for each part, find a valid result and break
                for j, part in enumerate(identifier):
                    # check if part has the required fields
                    if "Value" not in part.keys():
                        raise Exception(
                            "The given part '{}' fails to have any value field!".format(
                                part
                            )
                        )
                    if "Terms" not in part.keys():
                        raise Exception(
                            "The given part '{}' fails to have any terms field!".format(
                                part
                            )
                        )

                    if "Weight" not in part.keys():
                        raise Exception(
                            "The given part '{}' fails to have a weight!".format(part)
                        )

                    # update gauge
                    self.gauge.update_gauge(
                        gaugeID,
                        self.LOG,
                        "path_convert",
                        index=i + j / len(identifier),
                        length=len(identifiers),
                        limit=100,
                    )

                    # if there is a default value, set temp to it now
                    default = ""
                    if "DefaultValue" in part.keys():
                        default = part["DefaultValue"]

                    # for pattern in part
                    temp = default
                    for pattern in part["Terms"]:
                        # check for pattern in path
                        match = re.search(pattern, path)

                        # if match is found, else continue
                        if match is not None:
                            self.LOG.info(
                                "path_convert: match: match={} pattern={} path={}".format(
                                    match.group(0), pattern, path
                                )
                            )

                            # check if match should be searched with value
                            if "SearchTermResultWithValue" in part.keys():
                                if part["SearchTermResultWithValue"] is True:
                                    # update match with the new value using the TermResult
                                    sub_match = re.search(part["Value"], match.group(0))

                                    # if the part's value was found in the original matches' group
                                    if sub_match is not None:
                                        self.LOG.info(
                                            "path_convert: sub_match: match={} pattern={} path={}".format(
                                                sub_match.group(0), pattern, path
                                            )
                                        )

                                        # we found a match
                                        temp = sub_match.group(0)
                                        # update weight with match found
                                        weight += part["Weight"]
                                        self.LOG.info(
                                            "path_convert: result={} temp={}".format(
                                                result, temp
                                            )
                                        )
                                        break

                            # else we do set temp to a new value since we are not searching the result with value
                            temp = part["Value"]
                            # update weight with match found
                            weight += part["Weight"]
                            self.LOG.info(
                                "path_convert: result={} temp={}".format(temp, temp)
                            )
                            break

                    # insert default value into temp for the number of digits
                    if "MinimumDigits" in part.keys():
                        # always have a minimum digit of 1
                        for k in range(0, part["MinimumDigits"]):
                            # check if length of temp isnt already >= minimum
                            if len(temp) < part["MinimumDigits"]:
                                # update temp with default to extend length
                                temp = default + temp
                        self.LOG.info(
                            "path_convert: result={} temp={}".format(result, temp)
                        )

                    # append temp to result
                    result += temp
                    self.LOG.info(
                        "path_convert: result={} temp={}".format(result, temp)
                    )

            self.LOG.info("path_convert: result={}".format(result))
            # update gauge
            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "path_convert",
                index=100,
                length=100,
                limit=100,
            )

        except Exception as e:
            self.LOG.error("path_convert: error={}".format(e))
            self.LOG.info("path_convert: END")
            return "", 0  # other error

        self.LOG.info("path_convert: result={} weight={}".format(result, weight))
        self.LOG.info("path_convert: END")
        return result, weight  # no error

    # logs a file path to an aligner
    # input: AlignerID, FileID, Path, Verification
    # output: FileID on success, -1 on error
    def insert_file_to_aligner(
        self,
        alignerID: int,
        filetypeID: int,
        path: str,
        verification: Verification,
        status: int = Statuses.ACTIVE.value,
    ) -> int:
        try:
            self.LOG.info(
                "insert_file_to_aligner: alignerID={} filetypeID={} path={} verification={}".format(
                    alignerID, filetypeID, path, verification
                )
            )

            linkID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # insert files through File object
                    files = self.files.create_new_files(
                        verification, [{"path": path, "typeID": filetypeID}]
                    )
                    if len(files) == 0:
                        raise Exception(
                            "No files were created within the files table! Cancelling aligner file links!"
                        )

                    # link each file with aligner
                    sql.execute(
                        self.insert_aligner_file,
                        (
                            alignerID,
                            files[0]["FileID"],
                            verification.get_verification(),
                            status,
                        ),
                    )
                    if len(sql.table) != 0:
                        linkID = int(sql.table[0]["ID"])

                        # update aligner location
                        self.log_aligner(
                            alignerID,
                            "File: {0}".format(
                                ntpath.basename(path)[:150]
                            ),  # limit character length to SQL limit
                            "File Added",
                            verification,
                            10,
                        )
                    else:
                        raise Exception(
                            "No results found with the insert_aligner_file query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("insert_file_to_aligner: error={}".format(e))
            self.LOG.info("insert_file_to_aligner: END")
            return -1  # other error

        self.LOG.info("insert_file_to_aligner: linkID={}".format(linkID))
        self.LOG.info("insert_file_to_aligner: END")
        return linkID  # no error

    # logs a list of Dicts containg a filepath key and an AlignerID key
    # Example input :
    # {
    #   "path": "\\phasestorage.file.core.windows.net\prod-phasestorage\RemoteMain\ALIGNERS\Completed-Files\90047\90047LA-868995.stl",
    #   "alignerID": 478629,
    #   "typeID":5
    # }
    # input: Verification, alignerID_paths
    # output: FileIDs on success, [] on error
    def insert_files_to_aligners(
        self,
        verification: Verification,
        alignerID_paths: list,
    ) -> int:
        try:
            self.LOG.info(
                "insert_files_to_aligners: alignerID_paths={} verification={}".format(
                    alignerID_paths, verification
                )
            )

            linkIDs = []

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # Create file entries with Path and typeID
                    files = self.files.create_new_files(verification, alignerID_paths)
                    if len(files) == 0:
                        raise Exception(
                            "No files were created within the files table! Cancelling aligner file links!"
                        )

                    for aligner_file in alignerID_paths:
                        # find fileID to use
                        fileID = None
                        for file in files:
                            # match the generated fileID with the provided path and types since it is lost after execution
                            if (
                                aligner_file["path"] == file["Path"]
                                and aligner_file["typeID"] == file["FileTypeID"]
                            ):
                                fileID = file["FileID"]
                        # check if we got a fileID
                        if fileID is None:
                            raise Exception(
                                "The path for the given alignerID {0} fails to have an inserted file!".format(
                                    aligner_file["alignerID"]
                                )
                            )

                    for aligner_file in alignerID_paths:
                        # find fileID to use
                        fileID = None
                        for file in files:
                            # match the generated fileID with the provided path and types since it is lost after execution
                            if (
                                aligner_file["path"] == file["Path"]
                                and aligner_file["typeID"] == file["FileTypeID"]
                            ):
                                fileID = file["FileID"]
                        # check if we got a fileID
                        if fileID is None:
                            raise Exception(
                                "The path for the given alignerID {0} fails to have an inserted file!".format(
                                    aligner_file["alignerID"]
                                )
                            )

                        # link each file with given aligners
                        sql.execute(
                            self.insert_aligner_file,
                            (
                                aligner_file["alignerID"],
                                fileID,
                                verification.get_verification(),
                                11,
                            ),
                        )
                        if len(sql.table) != 0:
                            linkIDs.append(int(sql.table[0]["ID"]))

                            # update aligner locations
                            self.log_aligner(
                                aligner_file["alignerID"],
                                "File: {0}".format(
                                    ntpath.basename(aligner_file["path"])
                                ),
                                "File Added",
                                verification,
                                10,
                            )
                        else:
                            raise Exception(
                                "No results found with the insert_aligner_file query!"
                            )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("insert_files_to_aligners: error={}".format(e))
            self.LOG.info("insert_files_to_aligners: END")
            return []  # other error

        self.LOG.info("insert_files_to_aligners: linkID={}".format(linkIDs))
        self.LOG.info("insert_files_to_aligners: END")
        return linkIDs  # no error

    def get_files_by_bulk(
        self,
        alignerIDs: list,
        filetypeID: int | None = None,
        gaugeID: int | None = None,
    ) -> list:
        try:
            self.LOG.info(
                "get_files_by_bulk: alignerIDs={} filetypeID={} gaugeID={}".format(
                    alignerIDs, filetypeID, gaugeID
                )
            )

            files = {}

            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "getting_file_links",
                index=0,
                length=100,
                limit=100,
                constant=0,
                label="Initializing",
            )

            # for each aligner get its file links
            for i, alignerID in enumerate(alignerIDs):
                # append files from the alignerID
                result = []
                if filetypeID is None:
                    result = self.get_all_files_by_aligner(alignerID)
                else:
                    result = self.get_files_by_aligner(alignerID, filetypeID)
                if len(result) > 0:
                    files[alignerID] = result

                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "getting_file_links",
                    index=i + 1,
                    length=len(alignerIDs),
                    limit=100,
                    label="getting links for '{}' using type id '{}'".format(
                        alignerID, filetypeID
                    ),
                )

        except Exception as e:
            self.LOG.error("get_files_by_bulk: error={}".format(e))
            self.LOG.info("get_files_by_bulk: END")
            return []  # other error

        self.LOG.info("get_files_by_bulk: files={}".format(len(files)))
        self.LOG.info("get_files_by_bulk: END")
        return files  # no error

    # gets all files associated with an aligner by a given filetypeID
    # input: AlignerID, FileTypeID
    # output: Files on success, [] on error
    def get_files_by_aligner(self, alignerID: int, filetypeID: int) -> list:
        try:
            self.LOG.info(
                "get_files_by_aligner: alignerID={} filetypeID={}".format(
                    alignerID, filetypeID
                )
            )

            files = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_aligner_files, (alignerID, filetypeID))
                if len(sql.table) != 0:
                    files = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligner_files query!"
                    )

        except Exception as e:
            self.LOG.error("get_files_by_aligner: error={}".format(e))
            self.LOG.info("get_files_by_aligner: END")
            return []  # other error

        self.LOG.info("get_files_by_aligner: files={}".format(files))
        self.LOG.info("get_files_by_aligner: END")
        return files  # no error

    # gets all files associated with an aligner by a given filetypeID
    # input: AlignerID
    # output: Files on success, [] on error
    def get_all_files_by_aligner(self, alignerID: int) -> list:
        try:
            self.LOG.info("get_all_files_by_aligner: alignerID={}".format(alignerID))

            files = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_aligner_files, (alignerID))
                if len(sql.table) != 0:
                    files = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_aligner_files query!"
                    )

        except Exception as e:
            self.LOG.error("get_all_files_by_aligner: error={}".format(e))
            self.LOG.info("get_all_files_by_aligner: END")
            return []  # other error

        self.LOG.info("get_all_files_by_aligner: files={}".format(len(files)))
        self.LOG.info("get_all_files_by_aligner: END")
        return files  # no error

    # gets all files associated with an aligner by a given filetypeID
    # input: AlignerID, FileTypeID
    # output: Files on success, [] on error
    def get_active_files_by_aligner(self, alignerID: int, filetypeID: int) -> list:
        try:
            self.LOG.info(
                "get_active_files_by_aligner: alignerID={} filetypeID={}".format(
                    alignerID, filetypeID
                )
            )

            files = {}
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_active_aligner_files, (alignerID, filetypeID))
                if len(sql.table) != 0:
                    files[alignerID] = sql.table
                else:
                    raise Exception(
                        "No results found with the get_active_aligner_files query!"
                    )

        except Exception as e:
            self.LOG.error("get_active_files_by_aligner: error={}".format(e))
            self.LOG.info("get_active_files_by_aligner: END")
            return []  # other error

        self.LOG.info("get_active_files_by_aligner: files={}".format(files))
        self.LOG.info("get_active_files_by_aligner: END")
        return files  # no error

    # gets all files associated with an aligner by a given filetypeID
    # input: AlignerID
    # output: Files on success, [] on error
    def get_all_active_files_by_aligner(self, alignerID: int) -> list:
        try:
            self.LOG.info(
                "get_all_active_files_by_aligner: alignerID={}".format(alignerID)
            )

            files = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_active_aligner_files, (alignerID))
                if len(sql.table) != 0:
                    files = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_active_aligner_files query!"
                    )

        except Exception as e:
            self.LOG.error("get_all_active_files_by_aligner: error={}".format(e))
            self.LOG.info("get_all_active_files_by_aligner: END")
            return []  # other error

        self.LOG.info("get_all_active_files_by_aligner: files={}".format(files))
        self.LOG.info("get_all_active_files_by_aligner: END")
        return files  # no error

    # generates a filename to be linked to a given aligner by a given alignerIDs
    # input: AlignerIDs, FileTypeID
    # output: Filename on success, "" on error
    def generate_filename_by_aligners(self, alignerIDs: list, filetypeID: int) -> dict:
        try:
            self.LOG.info(
                "generate_filename_by_aligner: alignerIDs={} filetypeID={}".format(
                    alignerIDs, filetypeID
                )
            )

            filenames = {}

            # pull custom filename based on aligner
            with SQL_Pull()(self.sql_config)() as sql:
                results, _ = sql.execute(
                    self.name_importer,
                    (filetypeID, ",".join(str(_) for _ in alignerIDs)),
                )
                if len(results) == 0:
                    raise Exception(
                        "No results found trying to import a custom filename for the given aligners {} using query {}!".format(
                            alignerIDs, self.name_importer
                        )
                    )
                # convert to dictionary from list
                for result in results:
                    filenames[result["AlignerID"]] = result["Name"]

        except Exception as e:
            self.LOG.error("generate_filename_by_aligner: error={}".format(e))
            self.LOG.info("generate_filename_by_aligner: END")
            return {}  # other error

        self.LOG.info(
            "generate_filename_by_aligner: filenames={}".format(len(filenames))
        )
        self.LOG.info("generate_filename_by_aligner: END")
        return filenames  # no error

    # updates the status of a given file link
    # input: Verification, FileLink, Status
    # output: 0 on success, -1 on error
    def update_file_status(
        self,
        verification: Verification,
        link: int,
        status: int = Statuses.ACTIVE.value,
    ) -> int:
        try:
            self.LOG.info("update_file_status: link={} status={}".format(link, status))

            # get label of status id given
            label = self.statuses[status]
            if len(label) == 0:
                raise Exception(
                    "Unable to find a matching status with given status id {0}!".format(
                        status
                    )
                )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_status_of_file, (status, link))
                    if len(sql.table) != 0:
                        self.LOG.info("update_status: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_status_of_file query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_file_status: error={}".format(e))

        self.LOG.info("update_file_status: END")
        return -1  # other error

    # Creates an Aligner Batch. Accepts an verification, note, location, gaugeID (optional), and shade (optional)
    # Input Verification, note, location, gaugeID, shade
    # Output batchID on success
    def create_batch(
        self,
        verification: Verification,
        note: str,
        location: int,
        gaugeID: int | None = None,
        auxiliary: dict | None = None,
    ) -> int:
        try:
            self.LOG.info(
                "create_batch: verification={} note={} location={} auxiliary={}".format(
                    verification, note, location, auxiliary
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_aligner_batch,
                        (
                            verification.get_verification(),
                            note,
                            location,
                            gaugeID,
                            auxiliary,
                        ),
                    )

                    if len(sql.table) != 0:
                        batchID = int(sql.table[0]["ID"])
                    else:
                        raise Exception(
                            "No results found with the insert_aligner_batch query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_batch: error={}".format(e))
            return -1

        self.LOG.info("create_batch: END")
        return batchID

    # logs a list of aligners in a batch, used on bulk aligner submission entry
    # and lookbacks for aligner history
    # input: AlignerIDs, Verification
    # output: BatchID on success, -1 on error
    def batch_aligners(
        self,
        alignerIDs: List[int],
        verification: Verification,
        note: str,
        location: int | None = None,
        gaugeID: int | None = None,
        batchID: int | None = None,
    ) -> int:
        try:
            self.LOG.info(
                'batch_aligners: alignerIDs={} verification={} note="{}" gaugeID={}'.format(
                    alignerIDs, verification, note, gaugeID
                )
            )

            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "batch_aligners",
                index=0,
                limit=100,
                constant=0,
                label="Batching",
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # create batch if none provided
                    if batchID is None:
                        self.LOG.info(
                            "batch_aligners: No batch provided, generating..."
                        )

                        steps = []
                        sql.execute(
                            self.get_steps_from_alignerIDs,
                            (",".join(map(str, alignerIDs))),
                        )
                        if len(sql.table) != 0:
                            steps = [_["Step"] for _ in sql.table]
                        else:
                            raise Exception(
                                "No results found with the get_steps_from_alignerIDs query!"
                            )

                        # generate shade from steps
                        shade = gen_shade(steps)
                        self.LOG.info("batch_aligners: shade={}".format(shade))

                        # get batchID
                        batchID = self.create_batch(
                            verification,
                            note,
                            location,
                            gaugeID,
                            '{{ "shade": "{0}" }}'.format(shade),
                        )
                        if batchID < 0:
                            raise Exception(
                                "No results found generating the batch, aborting submission!"
                            )

                    # link aligners to batch
                    self.LOG.info("batch_aligners: batchID={}".format(batchID))

                    self.gauge.update_gauge(
                        gaugeID,
                        self.LOG,
                        "batch_aligners",
                        index=25,
                        length=100,
                        limit=100,
                        constant=0,
                        label="Initializing Aligner Linking",
                    )

                    # create each aligner link
                    threads = []
                    for alignerID in alignerIDs:
                        # check if step is in pattern
                        self.LOG.info(
                            "batch_aligners: linking aligner {} with batch {}".format(
                                alignerID, batchID
                            )
                        )

                        thread = ThreadWithReturnValue(
                            target=Aligner.batch_aligner,
                            args=(self, verification, alignerID, batchID),
                        )
                        thread.handled = False
                        thread.alignerID = alignerID
                        threads.append(thread)
                        thread.start()

                    # update gauge
                    self.gauge.update_gauge(
                        gaugeID,
                        self.LOG,
                        "batch_aligners",
                        index=50,
                        length=100,
                        limit=100,
                        label="Linking Aligners",
                    )

                    # rejoin threads
                    timeout = time.time() + 200  # timeout after 200 seconds
                    while len(threads) > 0:
                        threads = [t for t in threads if t.handled is False]

                        # timeout checker
                        if time.time() > timeout:
                            raise Exception("Threading timeout reached!")

                        # find a thread thats done
                        for thread in threads:
                            if thread.done() is False:
                                continue

                            linkID = thread.join()
                            thread.handled = True
                            if linkID == -1:
                                raise Exception(
                                    "Aligner batch linking failed for step {}!".format(
                                        thread.alignerID
                                    )
                                )

                        # old gauge updating
                        """
                        # update gauge
                        self.gauge.update_gauge(
                            gaugeID,
                            self.LOG,
                            "batch_aligners",
                            index=i + 5,
                            length=len(threads) + 5,
                            limit=100,
                            label="Created {}".format(thread.step),
                        )
                        """

                    # enable logging
                    # self.LOG.disabled = False

                    # update gauge
                    self.gauge.update_gauge(
                        gaugeID,
                        self.LOG,
                        "batch_aligners",
                        index=100,
                        length=100,
                        limit=100,
                        label="Aligners Batched",
                    )

                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("batch_aligners: error={}".format(e))
            self.LOG.info("batch_aligners: END")
            return -1

        self.LOG.info("batch_aligners: batchID={}".format(batchID))
        self.LOG.info("batch_aligners: END")
        return batchID

    # links an individual alignerID to a batchID
    def batch_aligner(
        self, verification: Verification, alignerID: int, batchID: int
    ) -> int:
        try:
            self.LOG.info(
                "batch_aligner: alignerID={} verification={} batchID={}".format(
                    alignerID, verification, batchID
                )
            )

            linkID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_aligner_batch_link,
                        (alignerID, batchID, verification.get_verification()),
                    )

                    if len(sql.table) != 0:
                        # set linkID
                        linkID = sql.table[0]["ID"]

                        # log aligner
                        self.log_aligner(
                            alignerID,
                            "Linked to Batch: {}".format(batchID),
                            "Aligner linked to Batch",
                            verification,
                            58,
                        )
                    else:
                        raise Exception(
                            "No results found with the insert_aligner_batch_link query!"
                        )

                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("batch_aligner: error={}".format(e))
            self.LOG.info("batch_aligner: END")
            return -1

        self.LOG.info("batch_aligner: batchID={}".format(linkID))
        self.LOG.info("batch_aligner: END")
        return linkID

    # gets a list of alignerIDs that carry matching BatchIDs
    # input: [BatchIDs]
    # output: AlignerIDs on success, [] on error
    def get_aligners_by_bulk_batch_links(self, batchIDs: list) -> list:
        self.LOG.info("get_aligners_by_bulk_batch_links: batchIDs={}".format(batchIDs))

        alignerIDs = {}
        with SQL_Pull()(self.sql_config)() as sql:
            for batchID in batchIDs:
                sql.execute(self.get_aligners_by_batch, (batchID))
                if len(sql.table) != 0:
                    alignerIDs[batchID] = sql.table
                else:
                    alignerIDs[batchID] = -1

        self.LOG.info(
            "get_aligners_by_bulk_batch_links: alignerIDs={}".format(alignerIDs)
        )
        self.LOG.info("get_aligners_by_bulk_batch_links: END")
        return alignerIDs

    # gets a list of alignerIDs that carry a matching batchID
    # input: BatchID
    # output: AlignerIDs on success, [] on error
    def get_aligners_by_batch_links(self, batchID: int) -> list:
        try:
            self.LOG.info("get_aligners_by_batch_links: batchID={}".format(batchID))

            alignerIDs = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_aligners_by_batch, (batchID))
                if len(sql.table) != 0:
                    alignerIDs = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligners_by_batch query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligners_by_batch_links: error={}".format(e))
            self.LOG.info("get_aligners_by_batch_links: END")
            return []  # other error

        self.LOG.info("get_aligners_by_batch_links: alignerIDs={}".format(alignerIDs))
        self.LOG.info("get_aligners_by_batch_links: END")
        return alignerIDs

    # gets a list of batchIDs given a location in descending order
    # input: Location
    # output: BatchIDs on success, [] on error
    def get_aligner_batches_by_location(
        self, location: int, startdate: str, enddate: str, offset: int, rows: int
    ) -> list:
        try:
            self.LOG.info(
                "get_aligner_batches_by_location: location={} startdate={} enddate={} offset={} rows={}".format(
                    location, startdate, enddate, offset, rows
                )
            )

            batches = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_batches_by_location,
                    (location, startdate, enddate, offset, rows),
                )

                if len(sql.table) != 0:
                    batches = sql.table
                else:
                    raise Exception(
                        "No results found with the get_batches_by_location query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligner_batches_by_location: error={}".format(e))
            self.LOG.info("get_aligner_batches_by_location: END")
            return []  # other error

        self.LOG.info(
            "get_aligner_batches_by_location: batches={}".format(len(batches))
        )
        self.LOG.info("get_aligner_batches_by_location: END")
        return batches

    # logs an aligner change given a description, used in other functions if a
    # value of an aligner is updated or changed from its initial creation form
    # input: AlignerID, Change, Description, Verification
    # output: 0 on success, -1 on error
    def log_aligner(
        self,
        alignerID: int,
        change: str,
        description: str,
        verification: Verification,
        logtype: int,
        severity: int | None = None,
    ) -> int:
        try:
            self.LOG.info(
                'log_aligner: alignerID={} change="{}" description="{}" verification={} logtype={} severity={}'.format(
                    alignerID, change, description, verification, logtype, severity
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_aligner_log,
                        (
                            logtype,
                            change,
                            description,
                            verification.get_verification(),
                            severity,
                            alignerID,
                            alignerID,
                            alignerID,
                            alignerID,
                            alignerID,
                            alignerID,
                            alignerID,
                            alignerID,
                            alignerID,
                            alignerID,
                            alignerID,
                            alignerID,
                            alignerID,
                        ),
                    )

                    if len(sql.table) != 0:
                        self.LOG.info("log_aligner: END")
                        return sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "No results found with the insert_aligner_log query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_aligner: error={}".format(e))

        self.LOG.info("log_aligner: END")
        return -1

    # pulls bulk log info for an entire case number
    # input: CaseNumber
    # output: Logs on success, [] on error
    def get_log_by_case(self, caseNumber: int) -> List[str]:
        try:
            self.LOG.info("get_log_by_case: caseNumber={}".format(caseNumber))

            logs = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_aligner_log_by_case, (caseNumber))
                if len(sql.table) != 0:
                    logs = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligner_log_by_case query!"
                    )

        except Exception as e:
            self.LOG.error("get_log_by_case: error={}".format(e))
            self.LOG.info("get_log_by_case: END")
            return []  # other error

        self.LOG.info("get_log_by_case: logs={}".format(len(logs)))
        self.LOG.info("get_log_by_case: END")
        return logs  # no error

    # pulls bulk log info for an entire case number
    # input: CaseNumber
    # output: Logs on success, [] on error
    def get_log_by_aligner(self, alignerID: int) -> List[str]:
        try:
            self.LOG.info("get_log_by_case: alignerID={}".format(alignerID))

            logs = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_aligner_log_by_aligner, (alignerID))
                if len(sql.table) != 0:
                    logs = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligner_log_by_aligner query!"
                    )

        except Exception as e:
            self.LOG.error("get_log_by_case: error={}".format(e))
            self.LOG.info("get_log_by_case: END")
            return []  # other error

        self.LOG.info("get_log_by_case: logs={}".format(len(logs)))
        self.LOG.info("get_log_by_case: END")
        return logs  # no error

    # updates an aligner to the following location given an instance iterator
    # location wont update if weight override is false and location's weight is less than following's weight
    # input: Verification, AlignerID, CurrentLocation, InstanceIdentifier
    # output: Location on success, -1 on error
    def move_location_to_following(
        self,
        verification: Verification,
        alignerID: int,
        instance: int | None = None,
        location: int | None = None,
        weight_override: bool = False,
        update_case: bool = False,
        case_info: dict | None = None,
        update_fixit: bool = False,
        fixit_info: dict | None = None,
    ) -> int:
        try:
            self.LOG.info(
                "move_location_to_following: verification={} alignerID={} instance={} location={} weight_override={} update_case={} case_info={} update_fixit={} fixit_info={}".format(
                    verification,
                    alignerID,
                    instance,
                    location,
                    weight_override,
                    update_case,
                    case_info,
                    update_fixit,
                    fixit_info,
                )
            )

            # define default return value
            final_location = -1

            # get aligners location
            # only run query if location was not provided
            aligners = []
            if weight_override is False or location is None or location < 0:
                aligners = self.get_aligner_by_id(alignerID)
                if len(aligners) == 0:
                    raise Exception(
                        "No aligner location was found for the given alignerID {}!".format(
                            alignerID
                        )
                    )

            # only update location to this if none was provided
            if location is None or location < 0:
                location = aligners[0]["CurrentLocation"]

            # get following location of current location
            results = self.loc.get_locations_following_location(location)
            self.LOG.info(
                "move_location_to_following: relationships={}".format(results)
            )
            if len(results) > 0:
                # set following location
                following = results[0]["FollowingLocationID"]
                # override with instance
                if instance is not None:
                    for result in results:
                        if instance == result["ID"]:
                            following = result["FollowingLocationID"]
                            break

                # define weight objects
                aligner_location_weight = 0
                case_location_weight = 0
                fixit_location_weight = 0
                following_weight = 0
                locations = []

                # update weights
                if weight_override is False:
                    # get all locations to acquire weights
                    locations = self.loc.get_locations_by_status(
                        status=Statuses.PRODUCTION.value
                    )  # status 20 is to acquire production locations
                    if len(locations) == 0:
                        raise Exception(
                            "No locations could be found from the locations table using status 20!"
                        )

                    # get location weight
                    filter_object = list(
                        filter(
                            lambda x: x["ID"] == aligners[0]["CurrentLocation"],
                            locations,
                        )
                    )
                    if len(filter_object) > 0:
                        aligner_location_weight = filter_object[0]["Weight"]

                    # get following location weight
                    filter_object = list(
                        filter(lambda x: x["ID"] == following, locations)
                    )
                    if len(filter_object) > 0:
                        following_weight = filter_object[0]["Weight"]

                # check if current location's weight is less than the following locations
                # only update location if current location's weight is less than following's
                if (
                    following_weight > aligner_location_weight
                    or weight_override is True
                ):
                    # update location
                    self.LOG.info("move_location_to_following: END")
                    final_location = self.update_location(
                        verification,
                        alignerID,
                        following,
                    )

                # pull relevant info for update_case and update_fixit
                # only get aligners if we need to acquire case_info and/or fixit_info
                aligners = []
                if (
                    update_case is True and (case_info is None or len(case_info) == 0)
                ) or (
                    update_fixit is True
                    and (fixit_info is None or len(fixit_info) == 0)
                ):
                    # get aligner info from an aligner
                    aligners = self.get_aligners_by_ids([alignerID])
                    if len(aligners) == 0:
                        raise Exception(
                            "The provided aligner '{}' fails to have any results upon acquisition!".format(
                                alignerID
                            )
                        )

                # check if the case's location needs updated
                if update_case is True:
                    # pull case info if we dont have it already
                    if case_info is None or len(case_info) == 0:
                        # get case info from aligners
                        with Case(self.sql_config) as cas:
                            caseID = aligners[0]["CaseID"]
                            result = cas.get_cases_by_id(caseID)
                            if len(result) == 0:
                                raise Exception(
                                    "The provided case '{}' from the given aligner '{}' failed to have any results upon acquisition!".format(
                                        caseID, alignerID
                                    )
                                )
                            # only get first result
                            case_info = result[0]

                    # get location weight
                    filter_object = list(
                        filter(
                            lambda x: x["ID"] == case_info["LocationID"],
                            locations,
                        )
                    )
                    if len(filter_object) > 0:
                        case_location_weight = filter_object[0]["Weight"]

                    # update location
                    if (
                        following_weight > case_location_weight
                        or weight_override is True
                    ):
                        with Case(self.sql_config) as cas:
                            cas.update_location(
                                verification, case_info["CaseID"], following
                            )

                if update_fixit is True:
                    # pull case info if we dont have it already
                    if fixit_info is None or len(fixit_info) == 0:
                        # get case info from aligners
                        with Fixit(self.sql_config) as fix:
                            fixitID = aligners[0]["FixitCID"]
                            # skip fixit grab if no fixit is given
                            if fixitID is not None:
                                result = fix.get_fixit_by_id(fixitID)
                                if len(result) == 0:
                                    raise Exception(
                                        "The provided case '{}' from the given aligner '{}' failed to have any results upon acquisition!".format(
                                            fixitID, alignerID
                                        )
                                    )
                                # only get first result
                                fixit_info = result[0]

                    # skip fixit location update if no fixit found
                    if fixit_info is not None and len(fixit_info) > 0:
                        # get location weight
                        filter_object = list(
                            filter(
                                lambda x: x["ID"] == fixit_info["LocationID"],
                                locations,
                            )
                        )
                        if len(filter_object) > 0:
                            fixit_location_weight = filter_object[0]["Weight"]

                        # update location
                        if (
                            following_weight > fixit_location_weight
                            or weight_override is True
                            and fixit_info["Status"] == Statuses.INPROGRESS.value
                        ):
                            with Fixit(self.sql_config) as fix:
                                fix.update_location(
                                    verification,
                                    fixit_info["FixitID"],
                                    following,
                                )
            else:
                raise Exception(
                    "No results found pulling a following location from a the given location {}!".format(
                        location
                    )
                )

        except Exception as e:
            self.LOG.error("move_location_to_following: error={}".format(e))
            return -1

        self.LOG.info(
            "move_location_to_following: final_location={}".format(final_location)
        )
        return final_location

    # updates an aligner to the previous location given an instance iterator
    # location wont update if weight override is false and location's weight is greater than previous' weight
    # input: Verification, AlignerID, CurrentLocation, InstanceIdentifier
    # output: Location on success, -1 on error
    def move_location_to_previous(
        self,
        verification: Verification,
        alignerID: int,
        instance: int | None = None,
        location: int | None = None,
        weight_override: bool = False,
        update_case: bool = False,
        case_info: dict | None = None,
        update_fixit: bool = False,
        fixit_info: dict | None = None,
    ) -> int:
        try:
            self.LOG.info(
                "move_location_to_previous: verification={} alignerID={} instance={} location={} weight_override={} update_case={} case_info={} update_fixit={} fixit_info={}".format(
                    verification,
                    alignerID,
                    instance,
                    location,
                    weight_override,
                    update_case,
                    case_info,
                    update_fixit,
                    fixit_info,
                )
            )

            # define default return value
            final_location = -1

            # get aligners location
            # only run query if location was not provided
            aligners = []
            if weight_override is False or location is None or location < 0:
                aligners = self.get_aligner_by_id(alignerID)
                if len(aligners) == 0:
                    raise Exception(
                        "No aligner location was found for the given alignerID {}!".format(
                            alignerID
                        )
                    )

            # only update location to this if none was provided
            if location is None or location < 0:
                location = aligners[0]["CurrentLocation"]

            # get previous location of current location
            results = self.loc.get_locations_previous_location(location)
            self.LOG.info("move_location_to_previous: relationships={}".format(results))
            if len(results) > 0:
                # get previous location based off instance
                previous = results[0]["PreviousLocationID"]
                if instance is not None:
                    for result in results:
                        if instance == result["ID"]:
                            previous = result["PreviousLocationID"]

                # define weight objects
                aligner_location_weight = 0
                case_location_weight = 0
                fixit_location_weight = 0
                previous_weight = 0
                locations = []

                # update weights
                if weight_override is False:
                    # get all locations to acquire weights
                    locations = self.loc.get_locations_by_status(
                        status=20
                    )  # location 20 is to acquire production locations
                    if len(locations) == 0:
                        raise Exception(
                            "No locations could be found from the locations table using status 20!"
                        )

                    # get location weight
                    filter_object = list(
                        filter(
                            lambda x: x["ID"] == aligners[0]["CurrentLocation"],
                            locations,
                        )
                    )
                    if len(filter_object) > 0:
                        aligner_location_weight = filter_object[0]["Weight"]

                    # get following location based off instance
                    filter_object = list(
                        filter(lambda x: x["ID"] == previous, locations)
                    )
                    if len(filter_object) > 0:
                        previous_weight = filter_object[0]["Weight"]

                # check if current location's weight is greater than the previous locations
                # only update location if current location's weight is greater than previous'
                if previous_weight < aligner_location_weight or weight_override is True:
                    # update location
                    self.LOG.info("move_location_to_previous: END")
                    final_location = self.update_location(
                        verification,
                        alignerID,
                        previous,
                    )

                # pull relevant info for update_case and update_fixit
                # only get aligners if we need to acquire case_info and/or fixit_info
                aligners = []
                if (
                    update_case is True and (case_info is None or len(case_info) == 0)
                ) or (
                    update_fixit is True
                    and (fixit_info is None or len(fixit_info) == 0)
                ):
                    # get aligner info from an aligner
                    aligners = self.get_aligners_by_ids([alignerID])
                    if len(aligners) == 0:
                        raise Exception(
                            "The provided aligner '{}' fails to have any results upon acquisition!".format(
                                alignerID
                            )
                        )

                # check if the case's location needs updated
                if update_case is True:
                    # pull case info if we dont have it already
                    if case_info is None or len(case_info) == 0:
                        # get case info from aligners
                        with Case(self.sql_config) as cas:
                            caseID = aligners[0]["CaseID"]
                            result = cas.get_cases_by_id(caseID)
                            if len(result) == 0:
                                raise Exception(
                                    "The provided case '{}' from the given aligner '{}' failed to have any results upon acquisition!".format(
                                        caseID, alignerID
                                    )
                                )
                            # only get first result
                            case_info = result[0]

                    # get location weight
                    filter_object = list(
                        filter(
                            lambda x: x["ID"] == case_info[0]["LocationID"],
                            locations,
                        )
                    )
                    if len(filter_object) > 0:
                        case_location_weight = filter_object[0]["Weight"]

                    # update location
                    if (
                        previous_weight < case_location_weight
                        or weight_override is True
                    ):
                        with Case(self.sql_config) as cas:
                            cas.update_location(
                                verification, case_info["CaseID"], previous
                            )

                if update_fixit is True:
                    # pull case info if we dont have it already
                    if fixit_info is None or len(fixit_info) == 0:
                        # get case info from aligners
                        with Fixit(self.sql_config) as fix:
                            fixitID = aligners[0]["FixitCID"]
                            result = fix.get_fixit_by_id(fixitID)
                            # skip fixit grab if no fixit is given
                            if fixitID is not None:
                                if len(result) == 0:
                                    raise Exception(
                                        "The provided case '{}' from the given aligner '{}' failed to have any results upon acquisition!".format(
                                            fixitID, alignerID
                                        )
                                    )
                                # only get first result
                                fixit_info = result[0]

                    # skip fixit location update if no fixit found
                    if fixit_info is not None and len(fixit_info) > 0:
                        # get location weight
                        filter_object = list(
                            filter(
                                lambda x: x["ID"] == fixit_info[0]["LocationID"],
                                locations,
                            )
                        )
                        if len(filter_object) > 0:
                            fixit_location_weight = filter_object[0]["Weight"]

                        # update location
                        if (
                            previous_weight < fixit_location_weight
                            or weight_override is True
                            and fixit_info["Status"] == Statuses.INPROGRESS.value
                        ):
                            with Fixit(self.sql_config) as fix:
                                fix.update_location(
                                    verification,
                                    fixit_info["FixitID"],
                                    previous,
                                )
            else:
                raise Exception(
                    "No results found pulling a previous location from a the given location {}!".format(
                        location
                    )
                )

        except Exception as e:
            self.LOG.error("move_location_to_previous: error={}".format(e))
            return -1

        self.LOG.info("move_location_to_previous: END")
        return final_location

    # updates the location assigned to a given aligner
    # input: Verification, AlignerID, Location
    # output: Location on success, -1 on error
    def update_location(
        self,
        verification: Verification,
        alignerID: int,
        location: int,
    ) -> int:
        try:
            self.LOG.info(
                "update_location: verification={} alignerID={} location={}".format(
                    verification,
                    alignerID,
                    location,
                )
            )

            # get label
            label = self.loc.locations[location]
            if len(label) == 0:
                raise Exception(
                    "Unable to find a matching location with given location id {0}!".format(
                        location
                    )
                )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_aligner_location, (location, alignerID))

                    if len(sql.table) != 0:  # didn't receive a response

                        self.log_aligner(
                            alignerID,
                            "Location: {0}".format(label),
                            "Location Updated",
                            verification,
                            LogTypes.ALIGNER_LOCATION_UPDATED.value,
                        )

                        self.LOG.info("update_location: END")
                        return location
                    else:
                        raise Exception(
                            "No results found with the update_aligner_location query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_location: error={}".format(e))

        self.LOG.info("update_location: END")
        return -1

    # updates an aligner's fixitid
    # input: Verification, AlignerID, FixitID
    # output: 0 on success, -1 on error
    def update_fixitid(
        self, verification: Verification, alignerID: int, fixitID: str
    ) -> int:
        try:
            self.LOG.info(
                "update_fixitid: verification={} alignerID={} fixitID={}".format(
                    verification, alignerID, fixitID
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_aligner_fixitid, (fixitID, alignerID))
                    if len(sql.table) != 0:  # didn't receive a response
                        self.LOG.info("update_fixitid: END")
                        self.log_aligner(
                            alignerID,
                            "FixitID: {0}".format(fixitID),
                            "FixiID Updated",
                            verification,
                            4,
                        )
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_aligner_fixitid query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_fixitid: error={}".format(e))

        self.LOG.info("update_fixitid: END")
        return -1

    # updates an aligner's status
    # input: Verification, AlignerID, FixitID, index of predefined statuses
    # output: 0 on success, -1 on error
    def update_status(
        self, verification: Verification, alignerID: int, status: int = 5
    ) -> int:
        try:
            self.LOG.info(
                "update_status: verification={} alignerID={} status={}".format(
                    verification, alignerID, status
                )
            )

            # get label of status id given
            label = self.statuses[status]
            if len(label) == 0:
                raise Exception(
                    "Unable to find a matching status with given status id {0}!".format(
                        status
                    )
                )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_aligner_status, (status, alignerID))
                    if len(sql.table) != 0:
                        self.LOG.info("update_status: END")
                        self.log_aligner(
                            alignerID,
                            "Status: {0}".format(label),
                            "Status Updated",
                            verification,
                            5,
                        )
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_aligner_status query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_status: error={}".format(e))

        self.LOG.info("update_status: END")
        return -1

    # updates a list of aligners status
    # input: Verification, AlignerIDs, Status, Gauge
    # output: 0 on success, -1 on error
    def update_aligners_status(
        self,
        verification: Verification,
        alignerIDs: list,
        status: int = 3,
        gaugeID: int | None = None,
    ) -> list:
        try:
            self.LOG.info(
                "delete_aligners: verification={} alignerIDs={} status={}".format(
                    verification, alignerIDs, status
                )
            )

            result = -1

            # update aligners status
            for i, alignerID in enumerate(alignerIDs):
                result = self.update_status(verification, alignerID, status=status)
                if result != 0:
                    raise Exception(
                        "No results found updating the status of alignerID {} to status {}!".format(
                            alignerID, status
                        )
                    )

                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "update_aligners",
                    index=i + 1,
                    length=len(alignerIDs),
                    limit=100,
                )

        except Exception as e:
            self.LOG.error("update_status: error={}".format(e))
            return -1

        self.LOG.info("update_status: END")
        return result

    # updates an aligner's productID
    # input: Verification, AlignerID, ProductID
    # output: 0 on success, -1 on error
    def update_product(
        self, verification: Verification, alignerID: int, productID: str = "POCA"
    ) -> int:
        try:
            self.LOG.info(
                "update_product: verification={} alignerID={} productID={}".format(
                    verification, alignerID, productID
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_aligner_product, (productID, alignerID))

                    if len(sql.table) != 0:
                        self.LOG.info("update_product: END")
                        self.log_aligner(
                            alignerID,
                            "Product: {0}".format(productID),
                            "Product Updated",
                            verification,
                            6,
                        )
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_aligner_product query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_product: error={}".format(e))

        self.LOG.info("update_product: END")
        return -1

    # creates aligners
    # input: verification, caseNumber, pattern
    # output: list on success, [] on error
    def create_aligners(
        self,
        owner_verification: Verification,
        verification: Verification,
        caseNumber: int,
        steps: list = [],
        pattern: str = "",
        gaugeID: int | None = None,
        locationID: int = Locations.CAD_IMPORT.value,
        update_case: bool = True,
    ) -> list:
        try:
            self.LOG.info(
                "create_aligners: owner_verification={} verification={} caseNumber={} steps={} pattern={} locationID={}".format(
                    owner_verification,
                    verification,
                    caseNumber,
                    steps,
                    pattern,
                    locationID,
                )
            )

            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "create_aligners",
                index=0,
                length=100,
                limit=100,
                constant=0,
                label="Initializing",
            )

            # aligners creation
            aligners = []

            # run verification check
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "create_aligners",
                    index=15,
                    length=100,
                    limit=100,
                    label="Pulling Case Info",
                )

                # get case product info
                case_products = self.cas.get_products_by_case(caseNumber)

                # get caseID and steps for caseNumber
                result = self.cas.get_info_by_case(caseNumber)
                if len(result) != 0:
                    # define case_info
                    case_info = result[0]

                    # get generic info
                    caseID = case_info["CaseID"]
                    shade = case_info["Shade"]

                    # check if case is even real, if not then create instance
                    with Case(self.sql_config) as cas:
                        phase_case = cas.get_phase_cases_by_ids([caseID])
                        if len(phase_case) == 0:
                            result = cas.create_phase_case(caseID, verification)
                            if len(result) == 0:
                                raise Exception(
                                    "A phase case creation for caseID '{}' was attempted but failed!".format(
                                        caseID
                                    )
                                )

                    # only gen steps from shade if specific steps werent provided
                    if len(steps) == 0:
                        steps = gen_steps(shade)

                    self.LOG.info(
                        "create_aligners: caseID={} shade={} steps={}".format(
                            caseID, shade, steps
                        )
                    )
                else:
                    raise Exception("No results found with the case_query query!")

                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "create_aligners",
                    index=25,
                    length=100,
                    limit=100,
                    label="Initializing Aligners",
                )

                # disable logging
                # self.LOG.disabled = True

                # create each aligner
                threads = []
                for step in steps:
                    # check if step is in pattern
                    if pattern in step:
                        self.LOG.info("create_aligners: step={}".format(step))

                        # create threaded aligner creation, only update_case once with inline if
                        thread = ThreadWithReturnValue(
                            target=Aligner.create_aligner,
                            args=(
                                self,
                                owner_verification,
                                verification,
                                caseNumber,
                                step,
                                None,
                                None,
                                None,
                                None,
                                (
                                    update_case if len(threads) == 0 else False
                                ),  # only update case once when threads is 0
                                case_info,
                                case_products,
                                locationID,
                            ),
                        )
                        thread.handled = False
                        thread.step = step
                        threads.append(thread)
                        thread.start()

                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "create_aligners",
                    index=50,
                    length=100,
                    limit=100,
                    label="Creating Aligners",
                )

                # rejoin threads
                timeout = time.time() + 200  # timeout after 200 seconds
                while len(threads) > 0:
                    threads = [t for t in threads if t.handled is False]

                    # timeout checker
                    if time.time() > timeout:
                        raise Exception("Threading timeout reached!")

                    # find a thread thats done
                    for thread in threads:
                        if thread.done() is False:
                            continue

                        aligner = thread.join()
                        thread.handled = True
                        if len(aligner) == 0:
                            raise Exception(
                                "Aligner creation failed for step {}!".format(
                                    thread.step
                                )
                            )
                        aligners.append(aligner)

                        # old gauge updating
                        """
                        # update gauge
                        self.gauge.update_gauge(
                            gaugeID,
                            self.LOG,
                            "create_aligners",
                            index=i + 5,
                            length=len(threads) + 5,
                            limit=100,
                            label="Created {}".format(thread.step),
                        )
                        """

                # confirm we have aligners
                if len(aligners) == 0:
                    raise Exception(
                        "No aligners generated for case {}!".format(caseNumber)
                    )

                # enable logging
                # self.LOG.disabled = False

                # upload batch
                batchID = self.batch_aligners(
                    list(map(lambda x: x["AlignerID"], aligners)),
                    verification,
                    "created_aligners",
                    location=24,
                    gaugeID=gaugeID,
                )
                if batchID == -1:
                    raise Exception(
                        "Batch submission of aligners {0} failed!".format(aligners)
                    )

                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "create_aligners",
                    index=100,
                    length=100,
                    limit=100,
                    label="Complete",
                )
            else:
                raise Exception("Invalid verificationID!")

        except Exception as e:
            self.LOG.error("create_aligners: error={}".format(e))
            self.LOG.info("create_aligners: END")
            return []  # other error

        self.LOG.info("create_aligners: aligners={}".format(len(aligners)))
        self.LOG.info("create_aligners: END")
        return aligners

    # gets a new step extender based on the current step extenders existing for the
    # given pattern caseNumber and step.
    # input: CaseNumber, Step
    # output: StepExtender
    def __get_new_step_extender(self, caseNumber, step) -> int:
        try:
            self.LOG.info(
                "get_new_step_extender: caseNumber={} step={}".format(caseNumber, step)
            )

            # define step_extender
            step_extender = -1

            # get aligners from case and step
            aligners = self.get_aligners_by_case_step(caseNumber, step)
            if len(aligners) == 0:
                # return 0 as step extender
                self.LOG.info("get_new_step_extender: extender=0")
                self.LOG.info("get_new_step_extender: END")
                return 0

            # sort steps by product
            aligner_products = {}
            for aligner in aligners:
                # skip invalid products
                if aligner["ProductID"] == "N/A" or aligner["ProductID"] is None:
                    continue

                # create product key if does not exist
                if aligner["ProductID"] not in aligner_products.keys():
                    aligner_products[aligner["ProductID"]] = {}

                # create extender key if does not exist
                if (
                    aligner["StepExtender"]
                    not in aligner_products[aligner["ProductID"]].keys()
                ):
                    aligner_products[aligner["ProductID"]][aligner["StepExtender"]] = []

                # append aligner to product and extender keys
                aligner_products[aligner["ProductID"]][aligner["StepExtender"]].append(
                    aligner["Step"]
                )

            # get products from case
            products = self.cas.get_products_by_case(caseNumber)
            if len(products) == 0:
                raise Exception(
                    "No products were found for case {}, this is required for determining the step extender!".format(
                        caseNumber
                    )
                )

            # find matching products
            for product in products:
                # get productID
                productID = product["ProductID"]

                # generate steps list
                try:
                    steps = gen_steps(product["Shade"])
                except AttributeError:
                    # skip this product if it fails to generate a shade
                    continue

                # check if this product is full
                # this determines which productID is the right productID
                if step not in steps:
                    continue

                # check if productID exists in aligner products
                if productID in aligner_products.keys():
                    # check if step is found in this product
                    total = 0
                    for extender in aligner_products[productID].keys():
                        total += len(aligner_products[productID][extender])
                    if len(steps) == total:
                        continue

                    # determine extender, it can never go past the length of the
                    # steps for this valid productID
                    for extender in range(0, len(steps)):
                        # check if the extender exists or not
                        if extender not in aligner_products[productID].keys():
                            # no extender yet, make one
                            step_extender = extender
                            break
                        # extender exists, check if the step has been put in
                        # there yet
                        if step not in aligner_products[productID][extender]:
                            # no step in extender, make one
                            step_extender = extender
                            break

                    # leave loop we found an extender for the current product
                    # and step
                    break

                # productID for step has no entries yet, make the first one as 0
                else:
                    step_extender = 0

        except Exception as e:
            self.LOG.error("get_new_step_extender: error={}".format(e))
            self.LOG.info("get_new_step_extender: END")
            return -1  # other error

        self.LOG.info("get_new_step_extender: extender={}".format(int(step_extender)))
        self.LOG.info("get_new_step_extender: END")
        return int(step_extender)

    # creates an aligner with the given information
    # input: Verification, CaseNumber, Step, StepExtender, Priority, Product
    # output: AlignerID on success, -1 on error
    def create_aligner(
        self,
        owner_verification: Verification,
        verification: Verification,
        caseNumber: int,
        step: str,
        step_extender: int | None = None,
        priority: int | None = None,
        custom_product: str | None = None,
        machineID: int | None = None,
        update_case: bool = False,
        case_info: dict | None = None,
        case_products: list | None = None,
        locationID: int = Locations.CAD_IMPORT.value,
    ) -> dict:
        try:
            self.LOG.info(
                "create_aligner: owner_verification={} verification={} caseNumber={} step={} step_extender={} priority={} custom_product={} machineID={} update_case={} case_info={} case_products={} locationID={}".format(
                    owner_verification,
                    verification,
                    caseNumber,
                    step,
                    step_extender,
                    priority,
                    custom_product,
                    machineID,
                    update_case,
                    case_info,
                    case_products,
                    locationID,
                )
            )

            aligner = {}

            # run verification check
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # pull case info if not provided
                if case_info is None:
                    result = self.cas.get_info_by_case(caseNumber)
                    case_info = result[0]
                # pull relevant info from case_info
                if case_info is not None and len(case_info) != 0:
                    # set global caseID
                    caseID = case_info["CaseID"]

                    # check if case is even real, if not then create instance
                    with Case(self.sql_config) as cas:
                        phase_case = cas.get_phase_cases_by_ids([caseID])
                        if len(phase_case) == 0:
                            result = cas.create_phase_case(caseID, verification)
                            if len(result) == 0:
                                raise Exception(
                                    "A phase case creation for caseID '{}' was attempted but failed!".format(
                                        caseID
                                    )
                                )

                    # check to see if step_extender needs to be incremented by 1 if an aligner with the original step_extender already exists
                    # dont determine new step extender if we are using a custom product
                    # if step_extender < 0 and len(custom_product) == 0:
                    #     step_extender = self.__get_new_step_extender(caseNumber, step)
                    # set local priority
                    if priority is not None and priority < 0:
                        priority = 0
                    # set local shade
                    shade = case_info["Shade"]
                    # set local steps
                    steps = gen_steps(shade)
                    self.LOG.info(
                        "create_aligner: caseID={} caseNumber={} step={} step_extender={} priority={} shade={} steps={} locationID={}".format(
                            caseID,
                            caseNumber,
                            step,
                            step_extender,
                            priority,
                            shade,
                            steps,
                            locationID,
                        )
                    )
                else:
                    raise Exception("No results found with the case_query query!")

                # use provided product or auto-generate it
                productID = None  # reinitialize productID
                if custom_product is None:
                    # get productID for step from caseNumber
                    products = case_products
                    if products is None:
                        products = self.cas.get_products_by_case(caseNumber)
                    self.LOG.info("create_aligner: products={}".format(products))
                    if products is None or len(products) == 0:
                        raise Exception(
                            "No products were found for case {}, this is required for determining the aligner's product!".format(
                                caseNumber
                            )
                        )

                    # go through each product type and look at its sub_shade
                    for product in products:
                        if len(product) < 2:
                            raise Exception(
                                "product={} from products seems to be missing it's ID and or Shade!".format(
                                    product
                                )
                            )
                        # get the sub_product
                        sub_product = product["ProductID"]
                        sub_shade = product["Shade"]  # get the sub_shade

                        # skip if none
                        if sub_shade is None:
                            continue

                        # generate sub_steps
                        sub_steps = gen_steps(sub_shade)  # convert to steps

                        # old product checking
                        """
                        # quickly get aligners that share a case, step, and sub product
                        aligners_of_like_step = []
                        with SQL_Pull()(self.sql_config)() as sql:
                            # execute
                            sql.execute(
                                self.get_aligners_by_CaseStepProduct,
                                (",".join(map(str, statuses)), caseNumber, step, sub_product),
                            )

                            # get aligners of like step and product
                            aligners_of_like_step = sql.table
                        self.LOG.info(
                            "create_aligner: like_steps={} sub_product={} sub_shade={} sub_steps={} sub_steps_count={}".format(
                                aligners_of_like_step,
                                sub_product,
                                sub_shade,
                                sub_steps,
                                sub_steps.count(step),
                            )
                        )

                        # check to see if step is in sub_steps
                        # check to see if step is in main steps
                        # check to see if the number of steps pulled from SQL, that already have the product type, is less than the number of duplicate steps found in sub_steps
                        if (
                            step in sub_steps
                            and step in steps
                            and len(aligners_of_like_step) < sub_steps.count(step)
                        ):  # check if step is in sub_steps for that product and in the general case shade
                            productID = sub_product  # we found a step that hasnt been made yet from the sub_shade
                            break
                        """

                        if step in sub_steps and step in steps:
                            productID = sub_product
                            break
                else:
                    # user provided a custom product
                    productID = custom_product

                # write to sql
                with SQL_Pull()(self.sql_config)() as sql:
                    # execute insert
                    sql.execute(
                        self.insert_aligner_initial,
                        (
                            caseID,
                            step,
                            step_extender,
                            Statuses.INPROGRESS.value,
                            productID,
                            priority,
                            verification.get_verification(),
                            owner_verification.get_verification(),
                        ),
                    )
                    if len(sql.table) != 0:
                        # get alignerID
                        aligner = sql.table[0]
                        self.LOG.info(
                            "create_aligner: aligner created: step={} aligner={} caseNumber={} caseID={} verification={}".format(
                                step,
                                aligner["AlignerID"],
                                caseNumber,
                                caseID,
                                verification.get_verification(),
                            )
                        )

                        # insert station
                        self.station_aligner(
                            verification,
                            aligner["AlignerID"],
                            locationID=Locations.CREATED.value,
                            machineID=machineID,
                            weight_override=True,
                            update_case=update_case,
                            case_info=case_info,
                        )

                        # update location
                        if locationID is not None:
                            # aligner location noverride
                            self.update_location(
                                verification,
                                aligner["AlignerID"],
                                locationID,
                            )
                            # case location override
                            if update_case is True:
                                self.cas.update_location(
                                    verification, aligner["CaseID"], locationID
                                )

                    else:
                        raise Exception(
                            "No results found with the insert_aligner_initial query!"
                        )

                # log aligner creation
                self.log_aligner(
                    aligner["AlignerID"],
                    "New",
                    "Aligner Created",
                    verification,
                    LogTypes.ALIGNER_CREATED.value,
                )

            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_aligner: error={}".format(e))
            self.LOG.info("create_aligner: END")
            return {}  # other error

        self.LOG.info("create_aligner: alignerID={}".format(str(aligner["AlignerID"])))
        self.LOG.info("create_aligner: END")
        return aligner  # no error

    # creates an aligner with the given information
    # input: AlignerID, Verification, CaseID, Step, StepExtender, Status, Priority
    # output: AlignerID on success, -1 on error
    def duplicate_aligner(
        self,
        alignerID: int,
        owner_verification: Verification,
        verification: Verification,
        fixitID: int | None = None,
        caseID: str | None = None,
        step: str | None = None,
        step_extender: int | None = None,
        priority: int | None = None,
        custom_product: str | None = None,
        machineID: int | None = None,
        update_fixit: bool = False,
        fixit_info: dict | None = None,
        locationID: int = Locations.CAD_IMPORT.value,
    ) -> dict:
        try:
            self.LOG.info(
                "duplicate_aligner: alignerID={} owner_verification={} verification={} fixitID={} caseID={} step={} step_extender={} product={} priority={}".format(
                    alignerID,
                    owner_verification,
                    verification,
                    fixitID,
                    caseID,
                    step,
                    step_extender,
                    custom_product,
                    priority,
                )
            )

            # define duplicate aligner
            duplicate = []

            # run verification check
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # get productID for step from caseNumber
                productID = None  # reinitialize productID
                result = self.get_aligner_by_id(alignerID)
                if len(result) != 0:
                    # check caseID
                    if caseID is None:
                        # 2 is the column for caseID
                        caseID = result[0]["CaseID"]
                    # check step
                    if step is None:
                        step = result[0]["Step"]  # 3 is the column for step
                    # check step_extender
                    if step_extender is None:
                        # 4 is the column for Extender
                        step_extender = result[0]["StepExtender"]
                    elif step_extender is not None and step_extender < 0:
                        # default step extender if its provided and its negative
                        step_extender = None
                    # check product
                    if custom_product is None:
                        # 8 is the column for ProductID
                        productID = result[0]["ProductID"]
                    # check priority
                    if priority is not None and priority < 0:
                        priority = 0
                else:
                    raise Exception(
                        "No results found with the get_aligner_by_ID query!"
                    )

                # get original aligner's file links
                file_links = self.get_all_files_by_aligner(alignerID)

                # log aligner remade
                self.log_aligner(
                    alignerID,
                    "duplicate",
                    "Aligner Remade",
                    verification,
                    LogTypes.ALIGNER_REMADE.value,
                )

                # write to sql
                self.LOG.info(
                    "duplicate_aligner: inserting aligner: caseID={} step={} step_extender={} duplicate={} status={} productID={} priority={} verification={} fixitCID={}".format(
                        caseID,
                        step,
                        step_extender,
                        alignerID,
                        self.statuses[Statuses.INPROGRESS.value],
                        productID,
                        priority,
                        verification,
                        fixitID,
                    )
                )
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.insert_aligner_initial,
                        (
                            caseID,
                            step,
                            step_extender,
                            Statuses.INPROGRESS.value,
                            productID,
                            priority,
                            verification.get_verification(),
                            owner_verification.get_verification(),
                        ),
                    )
                    if len(sql.table) != 0:
                        duplicate = sql.table[0]
                        self.station_aligner(
                            verification,
                            duplicate["AlignerID"],
                            locationID=Locations.CREATED.value,
                            machineID=machineID,
                            weight_override=True,
                            update_fixit=update_fixit,
                            fixit_info=fixit_info,
                        )

                        # update fixitID of old alignerID with given value
                        if fixitID is not None:
                            self.LOG.info(
                                "duplicate_aligner: updating fixitID: alignerID={} fixitID={} verification={}".format(
                                    alignerID, fixitID, verification
                                )
                            )
                            self.update_fixitid(
                                verification, duplicate["AlignerID"], fixitID
                            )

                        # update location if location is provided
                        if locationID is not None:
                            self.update_location(
                                verification, duplicate["AlignerID"], locationID
                            )
                            if update_fixit is True and fixitID is not None:
                                with Fixit(self.sql_config) as fix:
                                    fix.update_location(
                                        verification, fixitID, locationID
                                    )

                        # link each filelink with the given aligner
                        # constructs new links than reusing old ones to prevent cross deletion issues
                        alignerID_paths = []
                        for file_link in file_links:
                            alignerID_paths.append(
                                {
                                    "path": file_link["Path"],
                                    "alignerID": duplicate["AlignerID"],
                                    "typeID": file_link["FileTypeID"],
                                }
                            )
                        if len(alignerID_paths) > 0:
                            self.insert_files_to_aligners(verification, alignerID_paths)

                    else:
                        raise Exception(
                            "No results found with the insert_aligner_initial query!"
                        )

                # log aligner creation
                self.log_aligner(
                    duplicate["AlignerID"],
                    "New",
                    "Aligner Created",
                    verification,
                    LogTypes.ALIGNER_CREATED.value,
                )

            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("duplicate_aligner: error={}".format(e))
            self.LOG.info("duplicate_aligner: END")
            return {}  # other error

        self.LOG.info("duplicate_aligner: alignerID={}".format(duplicate["AlignerID"]))
        self.LOG.info("duplicate_aligner: END")
        return duplicate  # no error

    # creates an aligner with the given information
    # input: AlignerID, Verification, CaseID, Step, StepExtender, Status, Priority
    # output: AlignerID on success, -1 on error
    def remake_aligner(
        self,
        alignerID: int,
        owner_verification: Verification,
        verification: Verification,
        fixitID: int | None = None,
        caseID: str | None = None,
        step: str | None = None,
        step_extender: int | None = None,
        priority: int | None = None,
        custom_product: str | None = None,
        machineID: int | None = None,
        update_fixit: bool = False,
        fixit_info: dict | None = None,
        locationID: int = Locations.CAD_IMPORT.value,
    ) -> dict:
        try:
            self.LOG.info(
                "remake_aligner: alignerID={} owner_verification={} verification={} fixitID={} caseID={} step={} step_extender={} product={} priority={}".format(
                    alignerID,
                    owner_verification,
                    verification,
                    fixitID,
                    caseID,
                    step,
                    step_extender,
                    custom_product,
                    priority,
                )
            )

            # define remake aligner
            remake = []

            # run verification check
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # get productID for step from caseNumber
                productID = None  # reinitialize productID
                result = self.get_aligner_by_id(alignerID)
                if len(result) != 0:
                    # check caseID
                    if caseID is None:
                        # 2 is the column for caseID
                        caseID = result[0]["CaseID"]
                    # check step
                    if step is None:
                        step = result[0]["Step"]  # 3 is the column for step
                    # check step_extender
                    if step_extender is None:
                        # 4 is the column for Extender
                        step_extender = result[0]["StepExtender"]
                    elif step_extender is not None and step_extender < 0:
                        # default step extender if its provided and its negative
                        step_extender = None
                    # check product
                    if custom_product is None:
                        # 8 is the column for ProductID
                        productID = result[0]["ProductID"]
                    # check priority
                    if priority is not None and priority < 0:
                        priority = 0
                else:
                    raise Exception(
                        "No results found with the get_aligner_by_ID query!"
                    )

                # update status on old aligner to cancelled
                self.LOG.info(
                    "remake_aligner: updating status: alignerID={} status={} verification={}".format(
                        alignerID, Statuses.CANCELLED.value, verification
                    )
                )
                self.update_status(verification, alignerID, Statuses.CANCELLED.value)

                # update fixitID of old alignerID with given value
                if fixitID is not None:
                    self.LOG.info(
                        "remake_aligner: updating fixitID: alignerID={} fixitID={} verification={}".format(
                            alignerID, fixitID, verification
                        )
                    )
                    self.update_fixitid(verification, alignerID, fixitID)

                # log aligner remade
                self.log_aligner(
                    alignerID,
                    "Remake",
                    "Aligner Remade",
                    verification,
                    LogTypes.ALIGNER_REMADE.value,
                )

                # write to sql
                self.LOG.info(
                    "remake_aligner: inserting aligner: caseID={} step={} step_extender={} remake={} status={} productID={} priority={} verification={} fixitCID={}".format(
                        caseID,
                        step,
                        step_extender,
                        alignerID,
                        self.statuses[Statuses.INPROGRESS.value],
                        productID,
                        priority,
                        verification,
                        fixitID,
                    )
                )
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.insert_aligner_remake,
                        (
                            caseID,
                            step,
                            step_extender,
                            alignerID,
                            Statuses.INPROGRESS.value,
                            productID,
                            priority,
                            verification.get_verification(),
                            fixitID,
                            owner_verification.get_verification(),
                        ),
                    )
                    if len(sql.table) != 0:
                        remake = sql.table[0]
                        self.station_aligner(
                            verification,
                            remake["AlignerID"],
                            locationID=Locations.CREATED.value,
                            machineID=machineID,
                            weight_override=True,
                            update_fixit=update_fixit,
                            fixit_info=fixit_info,
                        )

                        if locationID is not None:
                            self.update_location(
                                verification, remake["AlignerID"], locationID
                            )
                            if update_fixit is True and fixitID is not None:
                                with Fixit(self.sql_config) as fix:
                                    fix.update_location(
                                        verification, fixitID, locationID
                                    )

                    else:
                        raise Exception(
                            "No results found with the insert_aligner_remake query!"
                        )

                # log aligner creation
                self.log_aligner(
                    remake["AlignerID"],
                    "New",
                    "Aligner Created",
                    verification,
                    LogTypes.ALIGNER_CREATED.value,
                )

            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("remake_aligner: error={}".format(e))
            self.LOG.info("remake_aligner: END")
            return {}  # other error

        self.LOG.info("remake_aligner: alignerID={}".format(remake["AlignerID"]))
        self.LOG.info("remake_aligner: END")
        return remake  # no error

    # retrieves an alignerID by alignerID
    # input: AlignerID
    # output: AlignerID info on success
    def get_aligners_by_ids(self, alignerIDs: list) -> list:
        try:
            self.LOG.info("get_aligners_by_ids: alignerIDs={}".format(alignerIDs))

            aligners = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get alignerIDs with info above
                sql.execute(
                    self.get_aligners_by_IDs, (",".join(str(_) for _ in alignerIDs))
                )
                # check table
                if len(sql.table) != 0:
                    aligners = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligners_by_IDs query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligners_by_ids: error={}".format(e))
            self.LOG.info("get_aligners_by_ids: END")
            return []  # other error

        self.LOG.info("get_aligners_by_ids: aligners={}".format(len(aligners)))
        self.LOG.info("get_aligners_by_ids: END")
        return aligners  # no error

    # retrieves an alignerID by alignerID
    # input: AlignerID
    # output: AlignerID info on success
    def get_aligner_by_id(self, alignerID: int) -> list:
        try:
            self.LOG.info("get_aligner_by_id: alignerID={}".format(alignerID))

            aligners = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get alignerID with info above
                sql.execute(self.get_aligner_by_ID, (alignerID))
                # check table
                if len(sql.table) != 0:
                    aligners = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligner_by_ID query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligner_by_id: error={}".format(e))
            self.LOG.info("get_aligner_by_id: END")
            return []  # other error

        self.LOG.info("get_aligner_by_id: aligners={}".format(len(aligners)))
        self.LOG.info("get_aligner_by_id: END")
        return aligners  # no error

    # retrieves an alignerID by alignerID
    # input: AlignerID
    # output: AlignerID info on success
    def get_remake_aligners_by_id(self, alignerID: int) -> list:
        try:
            self.LOG.info("get_remake_aligners_by_id: alignerID={}".format(alignerID))

            remakes = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get alignerID with info above
                sql.execute(self.get_remake_aligners_by_ID, (alignerID))
                if len(sql.table) != 0:
                    remakes = sql.table
                else:
                    raise Exception(
                        "No results found with the get_remake_aligners_by_ID query!"
                    )

        except Exception as e:
            self.LOG.error("get_remake_aligners_by_id: error={}".format(e))
            self.LOG.info("get_remake_aligners_by_id: END")
            return []  # other error

        self.LOG.info("get_remake_aligners_by_id: remakes={}".format(len(remakes)))
        self.LOG.info("get_remake_aligners_by_id: END")
        return remakes  # no error

    # retrieves a list of alignerIDs by case and step
    # input: CaseNumber, Step, StepExtender
    # output: AlignerID on success, -1 on error
    def get_aligners_by_case_step_ext(
        self,
        caseNumber: int,
        step: str,
        step_extender: int = 0,
        include_fixit: bool = True,
        statuses: list = [2, 4],
    ) -> list:
        try:
            self.LOG.info(
                "get_aligners_by_case_step_ext: caseNumber={} step={} step_extender={} statuses={}".format(
                    caseNumber, step, step_extender, statuses
                )
            )

            aligners = []

            with SQL_Pull()(self.sql_config)() as sql:

                # get alignerID with info above
                sql.execute(
                    self.get_aligners_by_CaseStepExt,
                    (",".join(statuses), caseNumber, step, step_extender),
                )

                # check table
                if len(sql.table) != 0:
                    # check fixits
                    if include_fixit:
                        aligners = sql.table
                    else:
                        with Fixit(self.sql_config) as fix:
                            for row in sql.table:
                                # check if fixit for aligner exists and
                                if fix.aligner_check(row["AlignerID"]) == 0:
                                    aligners.append(row)
                else:
                    raise Exception(
                        "No results found with the get_aligners_by_CaseStepExt query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligners_by_case_step_ext: error={}".format(e))
            self.LOG.info("get_aligners_by_case_step_ext: END")
            return []  # other error

        self.LOG.info(
            "get_aligners_by_case_step_ext: aligners={}".format(len(aligners))
        )
        self.LOG.info("get_aligners_by_case_step_ext: END")
        return aligners  # no error

    # retrieves a list of alignerIDs by case and step using a faster query
    # input: CaseNumber, Step, StepExtender
    # output: AlignerID on success, -1 on error
    def get_aligners_by_case_step_ext_simple(
        self,
        caseNumber: int,
        step: str,
        step_extender: int = 0,
        include_fixit: bool = True,
        statuses: list = [2, 4],
    ) -> list:
        try:
            self.LOG.info(
                "get_aligners_by_case_step_ext_simple: caseNumber={} step={} step_extender={} statuses={}".format(
                    caseNumber, step, step_extender, statuses
                )
            )

            aligners = []

            with SQL_Pull()(self.sql_config)() as sql:

                # get alignerID with info above
                sql.execute(
                    self.get_aligners_by_CaseStepExtSimple,
                    (",".join(map(str, statuses)), caseNumber, step, step_extender),
                )

                # check table
                if len(sql.table) != 0:
                    # check fixits
                    if include_fixit:
                        aligners = sql.table
                    else:
                        with Fixit(self.sql_config) as fix:
                            for row in sql.table:
                                # check if fixit for aligner exists and
                                if fix.aligner_check(row["AlignerID"]) == 0:
                                    aligners.append(row)
                else:
                    raise Exception(
                        "No results found with the get_aligners_by_CaseStepExtSimple query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligners_by_case_step_ext_simple: error={}".format(e))
            self.LOG.info("get_aligners_by_case_step_ext_simple: END")
            return []  # other error

        self.LOG.info(
            "get_aligners_by_case_step_ext_simple: aligners={}".format(len(aligners))
        )
        self.LOG.info("get_aligners_by_case_step_ext_simple: END")
        return aligners  # no error

    # retrieves a list of alignerIDs by case
    # input: CaseNumber
    # output: AlignerID on success, -1 on error
    def get_aligners_by_case(
        self,
        caseNumber: int,
        pattern: str = "",
        include_fixit: bool = True,
        statuses: list = [2, 4],
    ) -> list:
        try:
            self.LOG.info(
                "get_aligners_by_case: caseNumber={} pattern={} statuses={}".format(
                    caseNumber, pattern, statuses
                )
            )

            aligners = []
            with SQL_Pull()(self.sql_config)() as sql:

                # get alignerID with info above
                sql.execute(
                    self.get_aligners_by_Case,
                    (",".join(map(str, statuses)), caseNumber),
                )

                # check table
                if len(sql.table) != 0:
                    # check fixits
                    if include_fixit:
                        aligners = sql.table
                    else:
                        with Fixit(self.sql_config) as fix:
                            for row in sql.table:
                                # check if fixit for aligner exists and
                                if fix.aligner_check(row["AlignerID"]) == 0:
                                    aligners.append(row)

                    # get by pattern
                    if len(pattern) > 0:
                        temp = []
                        for aligner in aligners:
                            step = aligner["Step"]
                            if pattern in step:
                                temp.append(aligner)
                        aligners = temp

                else:
                    raise Exception(
                        "No results found with the get_aligners_by_Case query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligners_by_case: error={}".format(e))
            self.LOG.info("get_aligners_by_case: END")
            return []  # other error

        self.LOG.info("get_aligners_by_case: aligners={}".format(len(aligners)))
        self.LOG.info("get_aligners_by_case: END")
        return aligners  # no error

    # retrieves a list of alignerIDs by a comma separated string list of cases
    # input: cases
    # output: [Aligners] on success, [] on error
    def get_aligners_by_cases(
        self,
        cases: list,
        statuses: list = [2, 4],
    ) -> list:
        try:
            self.LOG.info(
                "get_aligners_by_cases: cases={} statuses={}".format(cases, statuses)
            )

            with SQL_Pull()(self.sql_config)() as sql:

                sql.execute(
                    self.get_aligners_by_string_list_cases,
                    (
                        ",".join(map(str, statuses)),
                        ",".join(map(str, cases)),
                    ),
                )

            DataList = sql.table

        except Exception as e:
            self.LOG.error("get_aligners_by_cases: error={}".format(e))
            self.LOG.info("get_aligners_by_cases: END")
            return []  # other error

        self.LOG.info("get_aligners_by_cases: aligners={}".format(DataList))
        self.LOG.info("get_aligners_by_cases: END")
        return DataList  # no error

    # retrieves a list of aligners with alignerID by caseNumber and step
    # input: CaseNumber, Step
    # output: List of AlignerIDs on success, "" on error
    def get_aligners_by_case_step(
        self,
        caseNumber: int,
        step: str,
        include_fixit: bool = True,
        statuses: list = [2, 4],
    ) -> list:
        try:
            self.LOG.info(
                "get_aligners_by_case_step: caseNumber={} step={} statuses={}".format(
                    caseNumber, step, statuses
                )
            )

            aligners = []
            with SQL_Pull()(self.sql_config)() as sql:

                # get alignerID with info above
                sql.execute(
                    self.get_aligners_by_CaseStep,
                    (",".join(map(str, statuses)), caseNumber, step),
                )

                # check table
                if len(sql.table) != 0:
                    # check fixits
                    if include_fixit:
                        aligners = sql.table
                    else:
                        with Fixit(self.sql_config) as fix:
                            for row in sql.table:
                                # check if fixit for aligner exists and
                                if fix.aligner_check(row["AlignerID"]) == 0:
                                    aligners.append(row)
                else:
                    raise Exception(
                        "No results found with the get_aligners_by_case_step query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligners_by_case_step: error={}".format(e))
            self.LOG.info("get_aligners_by_case_step: END")
            return []  # other error

        self.LOG.info("get_aligners_by_case_step: aligners={}".format(len(aligners)))
        self.LOG.info("get_aligners_by_case_step: END")
        return aligners  # no error

    # pulls a [aligners] data from a particular station(s)
    # input: AlignerIDs, Location
    # output: Aligner and station info if it exists
    def get_info_by_location(self, locations: list, alignerIDs: list) -> str:
        try:
            self.LOG.info("get_info_by_location: alignerID={}".format(alignerIDs))

            aligners = {}
            # Generates placeholder ? for pyodbc inserts
            aligner_placeholders = ",".join("?" * len(alignerIDs))
            location_placeholders = ",".join("?" * len(locations))

            for location in locations:
                aligners[location] = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_alignerLocationHistory.format(
                        aligner_placeholders, location_placeholders
                    ),
                    (*alignerIDs, *locations),
                )
                if len(sql.table) != 0:
                    for aligner in sql.table:
                        aligners[aligner["LocationID"]].append(aligner)

                else:
                    raise Exception(
                        "No results found with the get_info_by_location query!"
                    )

        except Exception as e:
            self.LOG.error("get_info_by_location: error={}".format(e))
            self.LOG.info("get_info_by_location: END")
            return aligners  # other error

        self.LOG.info("get_info_by_location: aligners={}".format(len(aligners)))
        self.LOG.info("get_info_by_location: END")
        return aligners  # no error

    # submits a set of aligners in bulk
    # input: Verification, AlignerIDs
    # output: BatchID
    def carbon_aligners(
        self,
        verification: Verification,
        aligners: list,
        flush: bool = False,
        machineID: int = -1,
        gaugeID: int | None = None,
        batchID: int | None = None,
        weight_override: bool = False,
        update_case: bool = True,
        update_fixit: bool = True,
    ) -> int:
        try:
            self.LOG.info(
                'carbon_aligners: verification="{}" alignerIDs={} flush={}'.format(
                    verification, aligners, flush
                )
            )

            # Grab alignerIDs from aligners
            alignerIDs = [aligner["AlignerID"] for aligner in aligners]

            # Initialize Index for Gauge to be shared across functions
            gaugeIndex = 0

            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "carbon_aligners",
                index=gaugeIndex,
                limit=100,
                constant=0,
                label="Initializing",
            )

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                caseIDs = []
                cases = []
                fixitIDs = []
                fixits = []
                if update_case is True or update_fixit is True:
                    # get aligner info from an aligner
                    caseIDs = []
                    for aligner in aligners:
                        if aligner["CaseID"] not in caseIDs:
                            caseIDs.append(aligner["CaseID"])

                    # get aligner info from an aligner
                    fixits = []
                    for aligner in aligners:
                        if aligner["FixitCID"] not in fixits:
                            fixits.append(aligner["FixitCID"])

                aligner_cases = {}
                if update_case is True:
                    # get case info from aligners
                    with Case(self.sql_config) as cas:
                        cases = cas.get_cases_by_ids(caseIDs)

                    # match cases to aligners for submission purposes
                    for aligner in aligners:
                        for case in cases:
                            # consolidate cases from given aligners to acquire a list of cases
                            if aligner["CaseID"] == case["CaseID"]:
                                aligner_cases[aligner["AlignerID"]] = case

                aligner_fixits = {}
                if update_fixit is True:
                    # get case info from aligners
                    with Fixit(self.sql_config) as fix:
                        fixits = fix.get_fixits_by_ids(fixitIDs)

                    # match fixits to aligners for submission purposes
                    for aligner in aligners:
                        for fixit in fixits:
                            # only allow fixits that are active
                            if fixit["Status"] == Statuses.INPROGRESS.value:
                                # consolidate fixits from given aligners to acquire a list of fixits
                                if aligner["FixitCID"] == fixit["FixitID"]:
                                    aligner_fixits[aligner["AlignerID"]] = case

                # get batchID with aligners
                batchID = self.batch_aligners(
                    alignerIDs,
                    verification,
                    "carbon_aligners",
                    location=12,
                    batchID=batchID,
                )
                if batchID == -1:
                    raise Exception(
                        "Batch submission of aligners {0} failed!".format(alignerIDs)
                    )

                # Generate the carbon build
                aligners, gaugeIndex = self.car.create_build(
                    verification, aligners, flush, gaugeID, gaugeIndex
                )

                # Submit built aligner data to carbon table
                threads = []
                for aligner in aligners:
                    thread = ThreadWithReturnValue(
                        target=Aligner.carbon_aligner,
                        args=(
                            self,
                            verification,
                            aligner,
                            machineID,
                            None,
                            weight_override,
                            update_case,
                            (
                                aligner_cases[aligner["AlignerID"]]
                                if aligner["AlignerID"] in aligner_cases.keys()
                                else None
                            ),
                            update_fixit,
                            (
                                aligner_cases[aligner["AlignerID"]]
                                if aligner["AlignerID"] in aligner_fixits.keys()
                                else None
                            ),
                        ),
                    )
                    thread.handled = False
                    thread.aligner = aligner
                    threads.append(thread)
                    thread.start()

                # rejoin threads
                timeout = time.time() + 200  # timeout after 200 seconds
                while len(threads) > 0:
                    threads = [t for t in threads if t.handled is False]

                    # timeout checker
                    if time.time() > timeout:
                        raise Exception("Threading timeout reached!")

                    # find a thread thats done
                    for thread in threads:
                        if thread.done() is False:
                            continue

                        # default value
                        result = -1

                        result = thread.join()
                        thread.handled = True
                        if result < 0:
                            raise Exception(
                                "Aligner {0} submission failed!".format(
                                    thread.aligner["AlignerID"]
                                )
                            )

                        gaugeIndex += 1
                        self.gauge.update_gauge(
                            gaugeID,
                            self.LOG,
                            "carbon_aligners",
                            index=gaugeIndex,
                            limit=100,
                            constant=0,
                            label="Submitting {}".format(thread.aligner["AlignerID"]),
                        )

            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("carbon_aligners: error={}".format(e))
            self.LOG.info("carbon_aligners: END")
            return -1  # other error

        self.LOG.info("carbon_aligners: batchID={}".format(batchID))
        self.LOG.info("carbon_aligners: END")
        return batchID  # no error

    def carbon_aligner(
        self,
        verification: Verification,
        aligner: dict,
        machineID: int | None = None,
        stationID: int | None = None,
        weight_override: bool = False,
        update_case: bool = False,
        case_info: dict | None = {},
        update_fixit: bool = False,
        fixit_info: dict | None = {},
    ) -> int:
        try:
            self.LOG.info(
                'carbon_aligner: verification="{}" aligner={} machineID={} stationID={}'.format(
                    verification, aligner, machineID, stationID
                )
            )

            entry = -1

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # insert into station
                    if stationID is None:
                        stationID = self.station_aligner(
                            verification,
                            aligner["AlignerID"],
                            12,
                            machineID,
                            weight_override=weight_override,
                            update_case=update_case,
                            case_info=case_info,
                            update_fixit=update_fixit,
                            fixit_info=fixit_info,
                        )
                    sql.execute(
                        self.insert_Carbon,
                        (
                            aligner["AlignerID"],
                            aligner["Step"],
                            aligner["AlignerID"],
                            ntpath.basename(aligner["Filename"]),
                            aligner["ModelUUID"],
                            aligner["PartUUID"],
                            aligner["PrintedPartUUID"],
                            aligner["OrderUUID"],
                            aligner["PartOrderNumber"],
                            aligner["ApplicationID"],
                            verification.get_verification(),
                            machineID,
                            stationID,
                        ),
                    )
                    if len(sql.table) != 0:
                        entry = int(sql.table[0]["CarbonID"])
                    else:
                        raise Exception(
                            "No results found with the insert_Carbon query!"
                        )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("carbon_aligner: error={}".format(e))
            self.LOG.info("carbon_aligner: END")
            return -1  # other error

        self.LOG.info("carbon_aligner: entry={}".format(entry))
        self.LOG.info("carbon_aligner: END")
        return entry  # no error

    # pulls an aligner's data from a particular station
    # input: AlignerID
    # output: Aligner on success, [] on error
    def get_aligner_by_carbon(self, alignerID: int) -> list:
        try:
            self.LOG.info("get_aligner_by_carbon: alignerID={}".format(alignerID))

            aligners = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_Carbon, (alignerID))
                if len(sql.table) != 0:
                    aligners = sql.table
                else:
                    raise Exception("No results found with the get_Carbon query!")

        except Exception as e:
            self.LOG.error("get_aligner_by_carbon: error={}".format(e))
            self.LOG.info("get_aligner_by_carbon: END")
            return []  # other error

        self.LOG.info("get_aligner_by_carbon: aligners={}".format(len(aligners)))
        self.LOG.info("get_aligner_by_carbon: END")
        return aligners  # no error

    # pulls an case's data from Carbon station
    # input: CaseNumber
    # output: CaseNumber on success, [] on error
    def get_case_by_carbon(self, caseNumber: int) -> list:
        try:
            self.LOG.info("get_case_by_carbon: caseNumber={}".format(caseNumber))

            aligners = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_Carbon_Case, (caseNumber))
                if len(sql.table) != 0:
                    aligners = sql.table
                else:
                    raise Exception(
                        "No results found with the get_case_by_carbon query!"
                    )

        except Exception as e:
            self.LOG.error("get_case_by_carbon: error={}".format(e))
            self.LOG.info("get_case_by_carbon: END")
            return []  # other error

        self.LOG.info("get_case_by_carbon: aligners={}".format(len(aligners)))
        self.LOG.info("get_case_by_carbon: END")
        return aligners  # no error

    # pulls the aligners history in carbon
    # input: ApplicationID
    # output: Aligner on success, [] on error
    def get_carbon_aligners(
        self, applicationID: str, startdate: str, enddate: str, offset: int, rows: int
    ) -> list:
        try:
            self.LOG.info(
                "get_carbon_aligners: applicationID={} startdate={} enddate={} offset={} rows={}".format(
                    applicationID, startdate, enddate, offset, rows
                )
            )

            aligners = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_aligners_in_Carbon,
                    (applicationID, startdate, enddate, offset, rows),
                )

                if len(sql.table) != 0:
                    aligners = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligners_in_Carbon query!"
                    )

        except Exception as e:
            self.LOG.error("get_carbon_aligners: error={}".format(e))
            self.LOG.info("get_carbon_aligners: END")
            return []  # other error

        self.LOG.info("get_carbon_aligners: aligners={}".format(len(aligners)))
        self.LOG.info("get_carbon_aligners: END")
        return aligners  # no error

    # pulls the aligners history in carbon
    # input: ApplicationID
    # output: Aligner on success, [] on error
    def get_carbon_aligners_by_filename(
        self, applicationID: str, filename: str
    ) -> list:
        try:
            self.LOG.info(
                "get_carbon_aligners_by_filename: applicationID={} filename={}".format(
                    applicationID, filename
                )
            )

            aligners = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_aligners_in_Carbon_by_filename, (filename, applicationID)
                )

                if len(sql.table) != 0:
                    aligners = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligners_in_Carbon_by_filename query!"
                    )

        except Exception as e:
            self.LOG.error("get_carbon_aligners_by_filename: error={}".format(e))
            self.LOG.info("get_carbon_aligners_by_filename: END")
            return []  # other error

        self.LOG.info(
            "get_carbon_aligners_by_filename: aligners={}".format(len(aligners))
        )
        self.LOG.info("get_carbon_aligners_by_filename: END")
        return aligners  # no error

    # given a lot number, updates the count and clears the lot if set to 0
    # input: Verification, LotNumber, Count, ClearLots
    # output: 0 on success, -1 on error
    def __subtract_from_lot(
        self,
        verification: Verification,
        lotID: str,
        count: int,
        clear_lots: bool = True,
    ) -> int:
        try:
            self.LOG.info(
                'subtract_from_lot: verification="{}" lotID={} count={} clear_lots={}'.format(
                    verification, lotID, count, clear_lots
                )
            )

            with Lot() as lot:
                # get yield from lot
                result = lot.get_yield_from_lot(lotID)
                if result == -1:
                    raise Exception(
                        "No results found retrieving the yield from the given lot {}!".format(
                            lotID
                        )
                    )
                yieldID = result

                # get quantity from yield
                result = lot.get_quantity_of_yield(yieldID)
                if len(result) == 0:
                    raise Exception(
                        "No results found retrieving the quantity from the given yield {}!".format(
                            yieldID
                        )
                    )
                # 2 is the column assigned to the quantity field
                quantity = result["Quantity"]

                # calculate difference
                difference = quantity - count

                # update yield's quantity
                result = lot.update_quantity_of_yield(
                    verification, yieldID, difference, clear_lots
                )
                if result == -1:
                    raise Exception(
                        "No results found updating the quantity of yieldID {} to {}!".format(
                            yieldID, difference
                        )
                    )

                self.LOG.info("subtract_from_lot: END")
                return 0

        except Exception as e:
            self.LOG.error("subtract_from_lot: error={}".format(e))

        self.LOG.info("subtract_from_lot: END")
        return -1  # other error

    # submits a set of aligners in bulk
    # input: Verification, AlignerIDs
    # output: BatchID
    def thermo_aligners(
        self,
        verification: Verification,
        alignerIDs: List[int],
        lotIDs: List[int],
        machineID: int | None = None,
        adjust_lot: bool = True,
        clear_lots: bool = True,
        gaugeID: int | None = None,
        batchID: int | None = None,
        lotbatchID: int | None = None,
        weight_override: bool = False,
        update_case: bool = True,
        update_fixit: bool = True,
    ) -> int:
        try:
            self.LOG.info(
                'thermo_aligners: verification="{}" alignerIDs={} lotIDs={}'.format(
                    verification, alignerIDs, lotIDs
                )
            )

            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "thermo_aligners",
                index=0,
                length=len(alignerIDs),
                limit=100,
                constant=0,
                label="Initializing",
            )

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                aligners = []
                caseIDs = []
                cases = []
                fixitIDs = []
                fixits = []
                if update_case is True or update_fixit is True:
                    # get aligner info from an aligner
                    aligners = self.get_aligners_by_ids(alignerIDs)

                    # get caseIDs
                    caseIDs = []
                    for aligner in aligners:
                        if aligner["CaseID"] not in caseIDs:
                            caseIDs.append(aligner["CaseID"])

                    # get fixitIDs
                    fixits = []
                    for aligner in aligners:
                        if aligner["FixitCID"] not in fixits:
                            fixits.append(aligner["FixitCID"])

                aligner_cases = {}
                if update_case is True:
                    # get case info from aligners
                    with Case(self.sql_config) as cas:
                        cases = cas.get_cases_by_ids(caseIDs)

                    # match cases to aligners for submission purposes
                    for aligner in aligners:
                        for case in cases:
                            # consolidate cases from given aligners to acquire a list of cases
                            if aligner["CaseID"] == case["CaseID"]:
                                aligner_cases[aligner["AlignerID"]] = case

                aligner_fixits = {}
                if update_fixit is True:
                    # get case info from aligners
                    with Fixit(self.sql_config) as fix:
                        fixits = fix.get_fixits_by_ids(fixitIDs)

                    # match fixits to aligners for submission purposes
                    for aligner in aligners:
                        for fixit in fixits:
                            # only allow fixits that are active
                            if fixit["Status"] == Statuses.INPROGRESS.value:
                                # consolidate fixits from given aligners to acquire a list of fixits
                                if aligner["FixitCID"] == fixit["FixitID"]:
                                    aligner_fixits[aligner["AlignerID"]] = case

                # get batchID with aligners
                batchID = self.batch_aligners(
                    alignerIDs,
                    verification,
                    "thermo_aligners",
                    location=14,
                    gaugeID=gaugeID,
                    batchID=batchID,
                )
                if batchID == -1:
                    raise Exception(
                        "Batch submission of aligners {0} failed!".format(alignerIDs)
                    )

                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "thermo_aligners",
                    index=25,
                    length=100,
                    limit=100,
                    label="Initializing Submission",
                )

                # checkout each aligner
                # set adjust_lot and clear_lots as False here and perform that separately below
                # otherwise each thread could update the table and cause number errors
                threads = []
                for alignerID in alignerIDs:
                    thread = ThreadWithReturnValue(
                        target=Aligner.thermo_aligner,
                        args=(
                            self,
                            verification,
                            alignerID,
                            lotIDs,
                            machineID,
                            False,
                            False,
                            lotbatchID,
                            weight_override,
                            update_case,
                            (
                                aligner_cases[alignerID]
                                if alignerID in aligner_cases.keys()
                                else None
                            ),
                            update_fixit,
                            (
                                aligner_fixits[alignerID]
                                if alignerID in aligner_fixits.keys()
                                else None
                            ),
                        ),
                    )
                    thread.handled = False
                    thread.alignerID = alignerID
                    threads.append(thread)
                    thread.start()

                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "thermo_aligners",
                    index=50,
                    length=100,
                    limit=100,
                    label="Submitting Aligners",
                )

                # rejoin threads
                timeout = time.time() + 200  # timeout after 200 seconds
                while len(threads) > 0:
                    threads = [t for t in threads if t.handled is False]

                    # timeout checker
                    if time.time() > timeout:
                        raise Exception("Threading timeout reached!")

                    # find a thread thats done
                    for thread in threads:
                        if thread.done() is False:
                            continue

                        result = thread.join()
                        thread.handled = True
                        if result < 0:
                            raise Exception(
                                "Aligner {0} submission failed!".format(
                                    thread.alignerID
                                )
                            )

                # old gauge update
                # """
                # self.gauge.update_gauge(
                #     gaugeID,
                #     self.LOG,
                #     "thermo_aligners",
                #     index=i + 1,
                #     length=len(alignerIDs),
                #     limit=100,
                #     label="Submitting {}".format(alignerIDs[i]),
                # )
                # """

                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "thermo_aligners",
                    index=75,
                    length=100,
                    limit=100,
                    label="Updating Lot",
                )

                # adjust lot count if adjust_lot is true
                if adjust_lot is True:
                    # declare count to remove from lot
                    count = len(alignerIDs)

                    # for each lotID provided
                    for lotID in lotIDs:
                        result = self.__subtract_from_lot(
                            verification, lotID, count, clear_lots
                        )
                        if result == -1:
                            raise Exception(
                                "No results found updating the lot {} yield quantity!".format(
                                    lotID
                                )
                            )

                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "thermo_aligners",
                    index=100,
                    length=100,
                    limit=100,
                    label="Complete",
                )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("thermo_aligners: error={}".format(e))
            self.LOG.info("thermo_aligners: END")
            return -1  # other error

        self.LOG.info("thermo_aligners: batchID={}".format(batchID))
        self.LOG.info("thermo_aligners: END")
        return batchID  # no error

    # modifies an aligner's Thermo submission time
    # input: Verification, AlignerID
    # output: AlignerID on success, -1 on error
    def thermo_aligner(
        self,
        verification: Verification,
        alignerID: int,
        lotIDs: List[int],
        machineID: int | None = None,
        adjust_lot: bool = True,
        clear_lots: bool = True,
        lotbatchID: int | None = None,
        weight_override: bool = False,
        update_case: bool = False,
        case_info: dict | None = {},
        update_fixit: bool = False,
        fixit_info: dict | None = {},
    ) -> int:
        try:
            self.LOG.info(
                'thermo_aligner: verification="{}" alignerID={} lotIDs={}'.format(
                    verification, alignerID, lotIDs
                )
            )

            entry = -1

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # insert into stations
                entry = self.station_aligner(
                    verification,
                    alignerID,
                    14,
                    machineID,
                    weight_override=weight_override,
                    update_case=update_case,
                    case_info=case_info,
                    update_fixit=update_fixit,
                    fixit_info=fixit_info,
                )

                # prevent lot subtraction if submission fails
                if entry > -1:
                    # insert lot entry for each lot provided
                    if (
                        len(
                            self.create_aligner_lot_links(
                                verification, alignerID, lotIDs, lotbatchID
                            )
                        )
                        == 0
                    ):
                        raise Exception(
                            "Unable to insert lots for aligner {}! Cancelling lot calculations!".format(
                                alignerID
                            )
                        )

                    # adjust lot count if adjust_lot is true
                    if adjust_lot is True:
                        for lotID in lotIDs:
                            result = self.__subtract_from_lot(
                                verification, lotID, 1, clear_lots
                            )
                            if result == -1:
                                raise Exception(
                                    "No results found updating the lot {} yield quantity!".format(
                                        lotID
                                    )
                                )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("thermo_aligner: error={}".format(e))
            self.LOG.info("thermo_aligner: END")
            return -1  # other error

        self.LOG.info("thermo_aligner: entry={}".format(entry))
        self.LOG.info("thermo_aligner: END")
        return entry  # no error

    # submits a set of aligners in bulk
    # input: Verification, AlignerIDs
    # output: BatchID
    def bag_aligners(
        self,
        verification: Verification,
        alignerIDs_bagUDIDs: Dict[int, int],
        machineID: int | None = None,
        gaugeID: int | None = None,
        batchID: int | None = None,
        weight_override: bool = False,
        update_case: bool = True,
        update_fixit: bool = True,
    ) -> int:
        try:
            self.LOG.info(
                'bag_aligners: verification="{}" alignerIDs_bagUDIDs={}'.format(
                    verification, alignerIDs_bagUDIDs
                )
            )

            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "bag_aligners",
                index=0,
                length=len(alignerIDs_bagUDIDs),
                limit=100,
                constant=0,
                label="Initializing",
            )

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # extract alignerIDs
                alignerIDs = list(alignerIDs_bagUDIDs.keys())

                aligners = []
                caseIDs = []
                cases = []
                fixitIDs = []
                fixits = []
                if update_case is True or update_fixit is True:
                    # get aligner info from an aligner
                    aligners = self.get_aligners_by_ids(alignerIDs)

                    # get caseIDs
                    caseIDs = []
                    for aligner in aligners:
                        if aligner["CaseID"] not in caseIDs:
                            caseIDs.append(aligner["CaseID"])

                    # get fixitIDs
                    fixits = []
                    for aligner in aligners:
                        if aligner["FixitCID"] not in fixits:
                            fixits.append(aligner["FixitCID"])

                aligner_cases = {}
                if update_case is True:
                    # get case info from aligners
                    with Case(self.sql_config) as cas:
                        cases = cas.get_cases_by_ids(caseIDs)

                    # match cases to aligners for submission purposes
                    for aligner in aligners:
                        for case in cases:
                            # consolidate cases from given aligners to acquire a list of cases
                            if aligner["CaseID"] == case["CaseID"]:
                                aligner_cases[aligner["AlignerID"]] = case

                aligner_fixits = {}
                if update_fixit is True:
                    # get case info from aligners
                    with Fixit(self.sql_config) as fix:
                        fixits = fix.get_fixits_by_ids(fixitIDs)

                    # match fixits to aligners for submission purposes
                    for aligner in aligners:
                        for fixit in fixits:
                            # only allow fixits that are active
                            if fixit["Status"] == Statuses.INPROGRESS.value:
                                # consolidate fixits from given aligners to acquire a list of fixits
                                if aligner["FixitCID"] == fixit["FixitID"]:
                                    aligner_fixits[aligner["AlignerID"]] = case

                # get batchID with aligners
                batchID = self.batch_aligners(
                    alignerIDs,
                    verification,
                    "bag_aligners",
                    location=20,
                    gaugeID=gaugeID,
                    batchID=batchID,
                )
                if batchID == -1:
                    raise Exception(
                        "Batch submission of aligners {0} failed!".format(alignerIDs)
                    )

                # checkout each aligner
                for i, alignerID in enumerate(alignerIDs_bagUDIDs.keys()):
                    result = self.bag_aligner(
                        verification,
                        int(alignerID),
                        alignerIDs_bagUDIDs[alignerID],
                        machineID,
                        weight_override=weight_override,
                        update_case=update_case,
                        case_info=(
                            aligner_cases[alignerID]
                            if alignerID in aligner_cases.keys()
                            else None
                        ),
                        update_fixit=update_fixit,
                        fixit_info=(
                            aligner_fixits[alignerID]
                            if alignerID in aligner_fixits.keys()
                            else None
                        ),
                    )
                    if result < 0:
                        raise Exception(
                            "Aligner {0} submission failed!".format(alignerIDs[i])
                        )
                    self.gauge.update_gauge(
                        gaugeID,
                        self.LOG,
                        "bag_aligners",
                        index=i + 1,
                        length=len(alignerIDs_bagUDIDs.keys()),
                        limit=100,
                        label="Submitting {}".format(alignerIDs[i]),
                    )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("bag_aligners: error={}".format(e))
            self.LOG.info("bag_aligners: END")
            return -1  # other error

        self.LOG.info("bag_aligners: batchID={}".format(batchID))
        self.LOG.info("bag_aligners: END")
        return batchID  # no error

    # modifies an aligner's Bag submission time
    # input: Verification, AlignerID
    # output: AlignerID on success, -1 on error
    def bag_aligner(
        self,
        verification: Verification,
        alignerID: int,
        bagUDID: int | None = None,
        machineID: int | None = None,
        update_case: bool = False,
        case_info: dict | None = None,
        weight_override: bool = False,
        update_fixit: bool = False,
        fixit_info: dict | None = None,
    ) -> int:
        try:
            self.LOG.info(
                'bag_aligner: verification="{}" alignerID={} bagUDID={}'.format(
                    verification, alignerID, bagUDID
                )
            )

            entry = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    entry = self.station_aligner(
                        verification,
                        alignerID,
                        20,
                        machineID,
                        weight_override=weight_override,
                        update_case=update_case,
                        case_info=case_info,
                        update_fixit=update_fixit,
                        fixit_info=fixit_info,
                    )

                    # link bag to alignerID
                    if bagUDID is not None:
                        if (
                            self.bag.insert_aligner_bag(
                                bagUDID, alignerID, verification
                            )
                            < 0
                        ):
                            raise Exception(
                                "No results found linking the bagUDID to the alignerID in the insert_Bag_Link query!"
                            )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("bag_aligner: error={}".format(e))
            self.LOG.info("bag_aligner: END")
            return -1  # other error

        self.LOG.info("bag_aligner: entry={}".format(entry))
        self.LOG.info("bag_aligner: END")
        return entry  # no error

    # pulls an aligner's data from a particular station
    # input: AlignerID
    # output: Aligner on success, [] on error
    def get_aligner_by_bag(self, alignerID: int) -> list:
        try:
            self.LOG.info("get_aligner_by_bag: alignerID={}".format(alignerID))

            aligners = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_Bag, (alignerID))
                if len(sql.table) != 0:
                    aligners = sql.table
                else:
                    raise Exception("No results found with the get_Bag query!")

        except Exception as e:
            self.LOG.error("get_aligner_by_bag: error={}".format(e))
            self.LOG.info("get_aligner_by_bag: END")
            return []  # other error

        self.LOG.info("get_aligner_by_bag: aligners={}".format(len(aligners)))
        self.LOG.info("get_aligner_by_bag: END")
        return aligners  # no error

    # logs a string prompt and response based on a batchID
    # input: BatchID, Prompt, Response, Verification
    # output: QuestionID on success, -1 on error
    def batch_question(
        self, batchID: int, prompt: str, response: str, verification: Verification
    ) -> int:
        try:
            self.LOG.info(
                'batch_question: batchID={} prompt="{}" response="{}" verification="{}"'.format(
                    batchID, prompt, response, verification
                )
            )

            questionID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                questionID, _ = sql.execute(
                    self.insert_question,
                    (batchID, prompt, response, verification.get_verification()),
                )

                if len(sql.table) == 0:
                    raise Exception("No results found with the insert_question query!")

        except Exception as e:
            self.LOG.error("batch_question: error={}".format(e))
            return -1

        self.LOG.info("batch_question: questionID={}".format(questionID))
        self.LOG.info("batch_question: END")
        return questionID

    # grabs all questions associated with a given batch ID
    # input: BatchID
    # output: Questions on success, [] on error
    def get_batch_questions_by_batch(self, batchID: int) -> list:
        try:
            self.LOG.info("get_batch_questions_by_batch: batchID={0}".format(batchID))

            questions = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_question_by_batch, (batchID))
                if len(sql.table) > 0:
                    questions = sql.table
                else:
                    raise Exception(
                        "No results found with the get_question_by_batch query!"
                    )

        except Exception as e:
            self.LOG.inf("get_batch_questions_by_batch: error={}".format(e))
            return []

        self.LOG.info("get_batch_questions_by_batch: questions={0}".format(questions))
        self.LOG.info("get_batch_questions_by_batch: END")
        return questions

    # grabs all aligners by given location by case
    # input: Location, CaseNumber
    # output: Aligners on success, [] on error
    def get_aligners_by_location(
        self, location: int, caseNumber: int | None = None, statuses: list = [2, 4]
    ) -> list:
        try:
            self.LOG.info(
                "get_aligners_by_location: location={0} caseNumber={1} statuses={2}".format(
                    location, caseNumber, statuses
                )
            )

            aligners = []

            with SQL_Pull()(self.sql_config)() as sql:

                if caseNumber is not None:

                    sql.execute(
                        self.get_aligners_by_loc_by_case,
                        (",".join(map(str, statuses)), location, caseNumber),
                    )

                else:
                    sql.execute(
                        self.get_aligners_by_loc,
                        (",".join(map(str, statuses)), location),
                    )
                if len(sql.table) > 0:
                    aligners = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligners_by_loc query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligners_by_location: error={}".format(e))
            return []

        self.LOG.info("get_aligners_by_location: aligners={0}".format(len(aligners)))
        self.LOG.info("get_aligners_by_location: END")
        return aligners

    # gets all aligners at each location for a given case
    # input: CaseNumber
    # output: Locations, {} on error
    def get_aligners_by_each_location(
        self, caseNumber: int | None = None, gaugeID: int | None = None
    ) -> dict:
        try:
            self.LOG.info("get_aligners_by_each_location: BEGIN")

            locations = {}

            for i, location in enumerate(self.locations.keys()):
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "get_aligners_by_each_location",
                    index=i,
                    length=len(self.locations),
                    limit=100,
                    label="Location {}".format(self.locations[location]),
                )

                # get aligners from location
                aligners = self.get_aligners_by_location(location, caseNumber)

                # append to dict
                locations[self.locations[location]] = aligners

            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "get_aligners_by_each_location",
                index=100,
                length=100,
                limit=100,
                label="Complete",
            )

        except Exception as e:
            self.LOG.error("get_aligners_by_each_location: error={}".format(e))
            return {}

        self.LOG.info(
            "get_aligners_by_each_location: locations={0}".format(len(locations))
        )
        self.LOG.info("get_aligners_by_each_location: END")
        return locations

    # Gets a list of aligners by a given plastic lot number directly
    # inputs: plasticLotNumber
    # outputs: Aligners on success, [] on error
    def get_aligners_by_plastic_lotnumber(self, lotnum: str) -> list:
        try:
            self.LOG.info("get_aligners_by_plastic_lotnumber: lotnum={}".format(lotnum))

            aligners = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_aligners_by_plastic_Lotnumber, (lotnum))
                if len(sql.table) > 0:
                    aligners = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligners_by_plastic_Lotnumber query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligners_by_plastic_lotnumber: error={}".format(e))
            self.LOG.info("get_aligners_by_plastic_lotnumber: END")
            return []

        self.LOG.info(
            "get_aligners_by_plastic_lotnumber: aligners={}".format(len(aligners))
        )
        self.LOG.info("get_aligners_by_plastic_lotnumber: END")
        return aligners  # no error

    # Gets a list of aligners by a given lot
    # inputs: plasticLotNumber
    # outputs: Aligners on success, [] on error
    def get_aligners_by_lot(self, lotID: str) -> list:
        try:
            self.LOG.info("get_aligners_by_lot: lotID={}".format(lotID))

            aligners = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_aligners_by_Lot, (lotID))
                if len(sql.table) > 0:
                    aligners = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligners_by_Lot query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligners_by_lot: error={}".format(e))
            self.LOG.info("get_aligners_by_lot: END")
            return []

        self.LOG.info("get_aligners_by_lot: aligners={}".format(len(aligners)))
        self.LOG.info("get_aligners_by_lot: END")
        return aligners  # no error

    # retrieves an fixitID by location
    # input: FixitID
    # output: Aligner List for success, [] for error
    def get_aligners_by_fixitID(self, fixitID: int, statuses: list = [2, 4]) -> list:
        try:
            self.LOG.info("get_aligners_by_fixitID: fixitID={}".format(fixitID))

            aligners = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get fixitID with info above

                # execute query
                sql.execute(
                    self.get_aligners_by_FixitID,
                    (",".join(map(str, statuses)), fixitID),
                )

                if len(sql.table) != 0:
                    aligners = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligners_by_FixitID query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligners_by_fixitID: error={}".format(e))
            self.LOG.info("get_aligners_by_fixitID: END")
            return []  # other error

        self.LOG.info("get_aligners_by_fixitID: aligners={}".format(len(aligners)))
        self.LOG.info("get_aligners_by_fixitID: END")
        return aligners  # no error

    # retrieves an fixitID by location
    # input: FixitID
    # output: Aligner List for success, [] for error
    def get_aligners_by_fixitCID(self, fixitID: int, statuses: list = [2, 4]) -> list:
        try:
            self.LOG.info("get_aligners_by_fixitCID: fixitID={}".format(fixitID))

            aligners = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get fixitID with info above

                # execute query
                sql.execute(
                    self.get_aligners_by_FixitCID,
                    (",".join(map(str, statuses)), fixitID),
                )

                if len(sql.table) != 0:
                    aligners = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligners_by_FixitCID query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligners_by_fixitCID: error={}".format(e))
            self.LOG.info("get_aligners_by_fixitCID: END")
            return []  # other error

        self.LOG.info("get_aligners_by_fixitCID: aligners={}".format(len(aligners)))
        self.LOG.info("get_aligners_by_fixitCID: END")
        return aligners  # no error

    # retrieves fixit aligners by date range
    # input: startdate, Dates2
    # output: Aligner List for success, [] for error
    def get_aligners_by_dates(
        self,
        startdate: str,
        enddate: str,
        offset: int,
        rows: int,
        statuses: list = [2, 4],
    ) -> list:
        try:
            self.LOG.info(
                "get_aligners_by_dates: startdate={0} enddate={1} offset={2} rows={3} statuses={4}".format(
                    startdate, enddate, offset, rows, statuses
                )
            )

            aligners = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get fixitID with info above
                sql.execute(
                    self.get_aligners_by_Dates,
                    (",".join(map(str, statuses)), startdate, enddate, offset, rows),
                )

                if len(sql.table) != 0:
                    aligners = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligners_by_Dates query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligners_by_dates: error={}".format(e))
            self.LOG.info("get_aligners_by_dates: END")
            return []  # other error

        self.LOG.info("get_aligners_by_dates: aligners={}".format(len(aligners)))
        self.LOG.info("get_aligners_by_dates: END")
        return aligners  # no error

    def get_aligners_by_location_fixit(
        self, location: int, caseNumber: int | None = None, statuses: list = [2, 4]
    ) -> list:
        try:
            self.LOG.info(
                "get_aligners_by_location_fixit: location={0} caseNumber={1} statuses={2}".format(
                    location, caseNumber, statuses
                )
            )

            aligners = []

            with SQL_Pull()(self.sql_config)() as sql:

                if caseNumber is not None:
                    sql.execute(
                        self.get_aligners_by_loc_fixit_by_case,
                        (",".join(map(str, statuses)), location, caseNumber),
                    )

                else:
                    sql.execute(
                        self.get_aligners_by_loc_fixit,
                        (",".join(map(str, statuses)), location),
                    )

                if len(sql.table) > 0:
                    aligners = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligners_by_loc query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligners_by_location_fixit: error={}".format(e))
            return []

        self.LOG.info(
            "get_aligners_by_location_fixit: aligners={0}".format(len(aligners))
        )
        self.LOG.info("get_aligners_by_location_fixit: END")
        return aligners

    def get_aligners_by_each_location_fixit(
        self, caseNumber: int | None = None, gaugeID: int | None = None
    ) -> dict:
        try:
            self.LOG.info("get_aligners_by_each_location_fixit: BEGIN")

            locations = {}

            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "get_aligners_by_each_location_fixit",
                index=0,
                length=1,
                limit=100,
                constant=0,
                label="Initializing",
            )

            for i, location in enumerate(self.loc.locations.keys()):
                # get aligners from location
                aligners = self.get_aligners_by_location_fixit(location, caseNumber)

                # append to dict
                locations[self.loc.locations[location]] = aligners

                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "get_aligners_by_each_location_fixit",
                    index=i + 1,
                    length=len(self.loc.locations),
                    limit=100,
                    label="Location {}".format(self.loc.locations[location]),
                )

        except Exception as e:
            self.LOG.error("get_aligners_by_each_location_fixit: error={}".format(e))
            return {}

        self.LOG.info(
            "get_aligners_by_each_location_fixit: locations={0}".format(len(locations))
        )
        self.LOG.info("get_aligners_by_each_location_fixit: END")
        return locations

    def get_files_by_id(
        self,
        linkID: int,
    ) -> dict:
        try:
            self.LOG.info("get_files_by_ID: BEGIN")

            files = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_aligner_files_by_linkID, (linkID))
                if len(sql.table) != 0:
                    files = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligner_files_by_linkID query!"
                    )

        except Exception as e:
            self.LOG.error("get_files_by_id: error={}".format(e))
            self.LOG.info("get_files_by_id: END")
            return []  # other error

        self.LOG.info("get_files_by_id: files={}".format(files))
        self.LOG.info("get_files_by_id: END")
        return files  # no error

    def purge_aligner_files(
        self,
        verification: Verification,
        alignerIDs: List[int],
        file_types: List[int] = [3, 4, 5, 6, 7, 9, 10, 11],
    ) -> list:
        try:
            self.LOG.info(
                "purge_aligner_files: verification={} alignerIDs={}".format(
                    verification, alignerIDs
                )
            )

            file_links = []

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.update_aligner_filelink_status,
                        (
                            12,
                            ",".join([str(_) for _ in alignerIDs]),
                            ",".join([str(_) for _ in file_types]),
                        ),
                    )
                    if len(sql.table) != 0:
                        file_links = sql.table
                    else:
                        raise Exception(
                            "No results found with the update_aligner_filelink_status query!"
                        )
            else:
                raise Exception("Invalid employeeID!")

        except Exception as e:
            self.LOG.error("purge_aligner_files: error={}".format(e))
            self.LOG.info("purge_aligner_files: END")
            return []  # other error

        self.LOG.info("purge_aligner_files: file_links={}".format(len(file_links)))
        self.LOG.info("purge_aligner_files: END")
        return file_links  # no error

    # grabs all aligner location information for given aligners
    # input: Aligners, Locations
    # output: Aligners on success, [] on error
    def get_aligners_by_station_locations(
        self,
        alignerIDs: list,
        locations: list,
        statuses: list = [2],
        gaugeID: int | None = None,
    ) -> list:
        try:
            self.LOG.info(
                "get_aligners_by_station_locations: aligners={0} locations={1} statuses={2}".format(
                    alignerIDs, locations, statuses
                )
            )

            alignerData = []

            with SQL_Pull()(self.sql_config)() as sql:

                if len(alignerIDs) > 0:
                    # update aligners status
                    count = 0
                    for alignerID in alignerIDs:
                        for location in locations:
                            sql.execute(
                                self.get_aligner_by_aligner_and_location,
                                (",".join(map(str, statuses)), alignerID, location),
                            )

                            if len(sql.table) != 0:
                                alignerData.append(sql.table)

                            count += 1

                            # update gauge
                            self.gauge.update_gauge(
                                gaugeID,
                                self.LOG,
                                "Fetching Aligner Data",
                                index=count,
                                length=len(alignerIDs) * len(locations),
                                limit=100,
                                label="Bulk Aligner Location Fetch",
                            )

                else:
                    raise Exception("No Aligner IDs Given")

        except Exception as e:
            self.LOG.error("get_aligners_by_station_locations: error={}".format(e))
            return []

        self.LOG.info(
            "get_aligners_by_station_locations: alignerData={0}".format(
                len(alignerData)
            )
        )
        self.LOG.info("get_aligners_by_station_locations: END")
        return alignerData

    # grabs all aligner location information for given aligners
    # input: Aligners, Locations
    # output: Aligners on success, [] on error
    def get_aligners_by_station_locations_fixit(
        self,
        alignerIDs: list,
        locations: list,
        statuses: list = [2],
        gaugeID: int | None = None,
    ) -> list:
        try:
            self.LOG.info(
                "get_aligners_by_station_locations_fixit: aligners={0} locations={1} statuses={2}".format(
                    alignerIDs, locations, statuses
                )
            )

            alignerData = []

            with SQL_Pull()(self.sql_config)() as sql:

                if len(alignerIDs) > 0:
                    # update aligners status
                    count = 0
                    for alignerID in alignerIDs:
                        for location in locations:
                            sql.execute(
                                self.get_aligner_by_aligner_and_location_fixit,
                                (",".join(map(str, statuses)), alignerID, location),
                            )

                            if len(sql.table) != 0:
                                alignerData.append(sql.table)

                            count += 1

                            # update gauge
                            self.gauge.update_gauge(
                                gaugeID,
                                self.LOG,
                                "Fetching Aligner Data with Fixits",
                                index=count,
                                length=len(alignerIDs) * len(locations),
                                limit=100,
                                label="Bulk Aligner Location Fetch",
                            )

                else:
                    raise Exception("No Aligner IDs Given")

        except Exception as e:
            self.LOG.error(
                "get_aligners_by_station_locations_fixit: error={}".format(e)
            )
            return []

        self.LOG.info(
            "get_aligners_by_station_locations_fixit: alignerData={0}".format(
                len(alignerData)
            )
        )
        self.LOG.info("get_aligners_by_station_locations_fixit: END")
        return alignerData

    # purges all station submissionf for a given set of alignerIDs
    # input: Verification, AlignerIDs
    # output: StationIDs
    def purge_aligner_station_submissions(
        self, verification: Verification, alignerIDs: List[int]
    ) -> list:
        try:
            self.LOG.info(
                'purge_aligner_station_submissions: verification="{}" alignerIDs={}'.format(
                    verification, alignerIDs
                )
            )

            station_submissions = []

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.update_aligner_station_status,
                        (12, ",".join([str(_) for _ in alignerIDs])),
                    )
                    if len(sql.table) != 0:
                        station_submissions = sql.table
                    else:
                        raise Exception(
                            "No results found with the update_aligner_station_status query!"
                        )
            else:
                raise Exception("Invalid employeeID!")

        except Exception as e:
            self.LOG.error("purge_aligner_station_submissions: error={}".format(e))
            self.LOG.info("purge_aligner_station_submissions: END")
            return []  # other error

        self.LOG.info(
            "purge_aligner_station_submissions: station_submissions={}".format(
                len(station_submissions)
            )
        )
        self.LOG.info("purge_aligner_station_submissions: END")
        return station_submissions  # no error

    # submits a set of aligners in bulk
    # input: Verification, AlignerIDs, LocationID, machineID, gaugeID,
    # output: BatchID
    def station_aligners(
        self,
        verification: Verification,
        alignerIDs: List[int],
        locationID: int,
        machineID: int | None = None,
        gaugeID: int | None = None,
        batchID: int | None = None,
        weight_override: bool = False,
        following_instance: int | None = None,
        update_case: bool = True,
        update_fixit: bool = True,
    ) -> int:
        try:
            self.LOG.info(
                'station_aligners: verification="{}" alignerIDs={} locationID={} machineID={} gaugeID={} batchID={} weight_override={} following_instance={} update_case={} update_fixit={}'.format(
                    verification,
                    alignerIDs,
                    locationID,
                    machineID,
                    gaugeID,
                    batchID,
                    weight_override,
                    following_instance,
                    update_case,
                    update_fixit,
                )
            )

            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "station_aligners",
                index=0,
                length=100,
                limit=100,
                constant=0,
                label="Batching",
            )

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                aligners = []
                caseIDs = []
                cases = []
                fixitIDs = []
                fixits = []
                if update_case is True or update_fixit is True:
                    # get aligner info from an aligner
                    aligners = self.get_aligners_by_ids(alignerIDs)

                    # get caseIDs
                    caseIDs = []
                    for aligner in aligners:
                        if aligner["CaseID"] not in caseIDs:
                            caseIDs.append(aligner["CaseID"])

                    # get fixitIDs
                    fixits = []
                    for aligner in aligners:
                        if aligner["FixitCID"] not in fixits:
                            fixits.append(aligner["FixitCID"])

                aligner_cases = {}
                if update_case is True:
                    # get case info from aligners
                    with Case(self.sql_config) as cas:
                        cases = cas.get_cases_by_ids(caseIDs)

                    # match cases to aligners for submission purposes
                    for aligner in aligners:
                        for case in cases:
                            # consolidate cases from given aligners to acquire a list of cases
                            if aligner["CaseID"] == case["CaseID"]:
                                aligner_cases[aligner["AlignerID"]] = case

                aligner_fixits = {}
                if update_fixit is True:
                    # get case info from aligners
                    with Fixit(self.sql_config) as fix:
                        fixits = fix.get_fixits_by_ids(fixitIDs)

                    # match fixits to aligners for submission purposes
                    for aligner in aligners:
                        for fixit in fixits:
                            # only allow fixits that are active
                            if fixit["Status"] == Statuses.INPROGRESS.value:
                                # consolidate fixits from given aligners to acquire a list of fixits
                                if aligner["FixitCID"] == fixit["FixitID"]:
                                    aligner_fixits[aligner["AlignerID"]] = case

                # get batchID with aligners
                batchID = self.batch_aligners(
                    alignerIDs,
                    verification,
                    "station_aligners",
                    location=locationID,
                    gaugeID=gaugeID,
                    batchID=batchID,
                )
                if batchID == -1:
                    raise Exception(
                        "Batch submission of aligners {0} failed!".format(alignerIDs)
                    )

                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "station_aligners",
                    index=25,
                    length=100,
                    limit=100,
                    constant=0,
                    label="Initializing Submission",
                )

                # disable logging
                # self.LOG.disabled = True

                # checkout each aligner
                threads = []
                for alignerID in alignerIDs:
                    thread = ThreadWithReturnValue(
                        target=Aligner.station_aligner,
                        args=(
                            self,
                            verification,
                            alignerID,
                            locationID,
                            machineID,
                            weight_override,
                            following_instance,
                            update_case,
                            (
                                aligner_cases[alignerID]
                                if alignerID in aligner_cases.keys()
                                else None
                            ),
                            update_fixit,
                            (
                                aligner_fixits[alignerID]
                                if alignerID in aligner_fixits.keys()
                                else None
                            ),
                        ),
                    )
                    thread.handled = False
                    thread.alignerID = alignerID
                    threads.append(thread)
                    thread.start()

                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "station_aligners",
                    index=50,
                    length=100,
                    limit=100,
                    constant=0,
                    label="Submitting",
                )

                # rejoin threads
                timeout = time.time() + 200  # timeout after 200 seconds
                while len(threads) > 0:
                    threads = [t for t in threads if t.handled is False]

                    # timeout checker
                    if time.time() > timeout:
                        raise Exception("Threading timeout reached!")

                    # find a thread thats done
                    for thread in threads:
                        if thread.done() is False:
                            continue

                        alignerID = thread.join()
                        thread.handled = True
                        if alignerID == -1:
                            raise Exception(
                                "Aligner {0} submission failed!".format(
                                    thread.alignerID
                                )
                            )

                # enable logging
                # self.LOG.disabled = False

                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "station_aligners",
                    index=100,
                    length=100,
                    limit=100,
                    constant=0,
                    label="Complete",
                )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("station_aligners: error={}".format(e))
            self.LOG.info("station_aligners: END")
            return -1  # other error

        self.LOG.info("station_aligners: batchID={}".format(batchID))
        self.LOG.info("station_aligners: END")
        return batchID  # no error

    # modifies an aligner's station submission time
    # input: Verification, AlignerID, LocationID
    # output: AlignerID on success, -1 on error
    def station_aligner(
        self,
        verification: Verification,
        alignerID: int,
        locationID: int,
        machineID: int | None = None,
        weight_override: bool = False,
        following_instance: int | None = None,
        update_case: bool = False,
        case_info: dict | None = {},
        update_fixit: bool = False,
        fixit_info: dict | None = {},
    ) -> int:
        try:
            self.LOG.info(
                'station_aligner: verification="{}" alignerID={} locationID={} machineID={} weight_override={} following_instance={} update_case={} case_info={} update_fixit={} fixit_info={}'.format(
                    verification,
                    alignerID,
                    locationID,
                    machineID,
                    weight_override,
                    following_instance,
                    update_case,
                    case_info,
                    update_fixit,
                    fixit_info,
                )
            )

            # result
            entry = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # update aligner location
                    final_location = self.move_location_to_following(
                        verification,
                        alignerID,
                        instance=following_instance,
                        location=locationID,
                        weight_override=weight_override,
                        update_case=update_case,
                        case_info=case_info,
                        update_fixit=update_fixit,
                        fixit_info=fixit_info,
                    )

                    # Submit aligner at station
                    sql.execute(
                        self.insert_Station,
                        (
                            alignerID,
                            alignerID,
                            verification.get_verification(),
                            locationID,
                            machineID,
                            final_location,
                        ),
                    )

                    if len(sql.table) != 0:
                        entry = int(sql.table[0]["ID"])

                    else:
                        raise Exception(
                            "No results found with the insert_Station query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("station_aligner: error={}".format(e))
            self.LOG.info("station_aligner: END")
            return -1  # other error

        self.LOG.info("station_aligner: entry={}".format(entry))
        self.LOG.info("station_aligner: END")
        return entry  # no error

    # pulls an aligner's data from all stations
    # input: AlignerID
    # output: Aligner on success, [] on error
    def get_stations_by_aligner(self, alignerID: int) -> list:
        try:
            self.LOG.info("get_stations_by_aligner: alignerID={}".format(alignerID))

            station_aligners = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_station_by_aligner, (alignerID))
                if len(sql.table) != 0:
                    station_aligners = sql.table
                else:
                    raise Exception("No results found with the get_stations query!")

        except Exception as e:
            self.LOG.error("get_stations_by_aligner: error={}".format(e))
            self.LOG.info("get_stations_by_aligner: END")
            return []  # other error

        self.LOG.info(
            "get_stations_by_aligner: station_aligners={}".format(len(station_aligners))
        )
        self.LOG.info("get_stations_by_aligner: END")
        return station_aligners  # no error

    # retrieves count of aligners by date range
    # input: StartDate, EndDate
    # output: {"Quantity": alignerCount} for success, {} for error
    def get_alignersQTY_by_dates(
        self,
        startdate: str,
        enddate: str,
    ) -> dict:
        try:
            self.LOG.info(
                "get_alignersQTY_by_dates: startdate={0} enddate={1} ".format(
                    startdate, enddate
                )
            )

            alignerCount = {}
            if startdate is not None and enddate is not None:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(self.get_alignerQTY_by_Dates, (startdate, enddate))
                    if len(sql.table) != 0:
                        alignerCount = sql.table[0]
                    else:
                        raise Exception(
                            "No results found with the get_alignersQTY_by_Dates query!"
                        )

        except Exception as e:
            self.LOG.error("get_alignersQTY_by_Dates: error={}".format(e))
            self.LOG.info("get_alignersQTY_by_Dates: END")
            return {}  # other error

        self.LOG.info("get_alignersQTY_by_Dates: aligners={}".format(len(alignerCount)))
        self.LOG.info("get_alignersQTY_by_Dates: END")
        return alignerCount  # no error

    # retrieves Aligners in the stations table for the given location, daterange, offset, rows and optional case
    # input: LocationID, Case, Status, startdate, enddate, offset, rows
    # output: [Aligners] for success, [] for error
    def get_aligners_by_location_by_case(
        self,
        locationID: int,
        offset: int,
        rows: int,
        startdate: str,
        enddate: str,
        case: str = "",
    ) -> dict:
        try:
            self.LOG.info(
                "get_aligners_by_location_by_case: locationID={0} case={1} offset={2} rows={3} startdate={4} enddate={5} ".format(
                    locationID, case, offset, rows, startdate, enddate
                )
            )

            aligners = []
            if len(case) > 0 and locationID is not None:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.get_station_aligners_by_Case_Location,
                        (locationID, case, startdate, enddate, offset, rows),
                    )

                    if len(sql.table) != 0:
                        aligners = sql.table
                    else:
                        raise Exception(
                            "No results found with the get_station_aligners_by_Case_Location query!"
                        )

            elif locationID is not None:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.get_station_aligners_by_Location,
                        (locationID, startdate, enddate, offset, rows),
                    )

                    if len(sql.table) != 0:
                        aligners = sql.table
                    else:
                        raise Exception(
                            "No results found with the get_station_aligners_by_Location query!"
                        )
            else:
                raise Exception("Correct Parameters not given")

        except Exception as e:
            self.LOG.error("get_aligners_by_location_by_case: error={}".format(e))
            self.LOG.info("get_aligners_by_location_by_case: END")
            return {}  # other error

        self.LOG.info(
            "get_aligners_by_location_by_case: aligners={}".format(len(aligners))
        )
        self.LOG.info("get_aligners_by_location_by_case: END")
        return aligners  # no error

    # retrieves fixit aligners by date range
    # input: startdate, enddate
    # output: Aligner List for success, [] for error
    def get_aligners_by_date_range(
        self,
        startdate: str,
        enddate: str,
        statuses: list = [2, 4],
    ) -> list:
        try:
            self.LOG.info(
                "get_aligners_by_date_range: startdate={0} enddate={1} statuses={2}".format(
                    startdate, enddate, statuses
                )
            )

            aligners = []

            with SQL_Pull()(self.sql_config)() as sql:

                # get fixitID with info above
                sql.execute(
                    self.get_aligners_by_Date_range,
                    (",".join(map(str, statuses)), startdate, enddate),
                )

                if len(sql.table) != 0:
                    aligners = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligners_by_Dates query!"
                    )

        except Exception as e:
            self.LOG.error("get_aligners_by_date_range: error={}".format(e))
            self.LOG.info("get_aligners_by_date_range: END")
            return []  # other error

        self.LOG.info("get_aligners_by_date_range: aligners={}".format(len(aligners)))
        self.LOG.info("get_aligners_by_date_range: END")
        return aligners  # no error

    # Retrieves location history by date range, rows and offset
    # input: location, startdate, enddate, rows, offset
    # output: Aligner List for success, [] for error
    def get_location_history(
        self,
        location: int,
        startdate: str,
        enddate: str,
        offset: int,
        rows: int,
    ) -> list:
        try:
            self.LOG.info(
                "get_location_history: startdate={0} enddate={1} offset={2} rows={3} location={4}".format(
                    startdate, enddate, offset, rows, location
                )
            )

            aligners = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get aligners history with info above
                sql.execute(
                    self.get_location_history_by_date_range,
                    (location, startdate, enddate, offset, rows),
                )

                if len(sql.table) != 0:
                    aligners = sql.table
                else:
                    raise Exception(
                        "No results found with the get_location_history_by_date_range query"
                    )

        except Exception as e:
            self.LOG.error("get_location_history_by_date_range: error={}".format(e))
            self.LOG.info("get_location_history_by_date_range: END")
            return []  # other error

        self.LOG.info(
            "get_location_history_by_date_range: aligners={}".format(len(aligners))
        )
        self.LOG.info("get_location_history_by_date_range: END")
        return aligners  # no error

    # Retrieves location history by date range, rows and offset
    # input: location, startdate, enddate, rows, offset
    # output: Aligner List for success, [] for error
    def transfer_aligners_to_case(
        self,
        verification: Verification,
        alignerIDs_case: dict,
        gaugeID: int | None = None,
    ) -> list:
        try:
            self.LOG.info(
                "transfer_aligners_to_case: verification={0} alignerIDs_case={1} ".format(
                    verification, alignerIDs_case
                )
            )

            aligners = []

            # calculate aligners to be changed
            totaltochange = 0
            for key in alignerIDs_case.keys():
                totaltochange += len(alignerIDs_case[key])

            # update gauge
            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "transfer_aligners_to_case",
                index=0,
                length=totaltochange,
                constant=0,
                limit=100,
                label="Initializing",
            )

            # check verification
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # counter for gauge calculations
                counter = 0

                # loop through each provided case
                with SQL_Pull()(self.sql_config)() as sql:
                    for case in alignerIDs_case.keys():
                        for alignerID in alignerIDs_case[case]:
                            # get aligners history with info above
                            sql.execute(self.transfer_aligners, (case, alignerID))
                            if len(sql.table) != 0:
                                aligners.append(sql.table[0]["AlignerID"])
                            else:
                                raise Exception(
                                    "No results found with the transfer_aligners query using alignerID {} at {}/{} in the process!".format(
                                        alignerID, counter, totaltochange
                                    )
                                )

                            # log aligner
                            self.log_aligner(
                                alignerID,
                                "Transferred",
                                "Case Transferred",
                                verification,
                                42,
                            )

                            # update gauge
                            self.gauge.update_gauge(
                                gaugeID,
                                self.LOG,
                                "transfer_aligners_to_case",
                                index=counter + 1,
                                length=totaltochange,
                                limit=100,
                                label="Transferring {}".format(alignerID),
                            )
                            counter += 1

            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("transfer_aligners_to_case: error={}".format(e))
            self.LOG.info("transfer_aligners_to_case: END")
            return []  # other error

        self.LOG.info("transfer_aligners_to_case: aligners={}".format(len(aligners)))
        self.LOG.info("get_location_history_by_date_range: END")
        return aligners  # no error

    # get all aligner lot links
    # output: list of aligner lot links
    def get_all_aligner_lot_links(self) -> list:
        try:
            self.LOG.info("get_all_aligner_lot_links: Start")

            links = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_aligner_lot_links)
                if len(sql.table) != 0:
                    links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_aligner_lot_links query"
                    )

        except Exception as e:
            self.LOG.error("get_all_aligner_lot_links: error={}".format(e))
            self.LOG.info("get_all_aligner_lot_links: END")
            return []  # other error

        self.LOG.info("get_all_aligner_lot_links: AlignerLotLinks={}".format(links))
        self.LOG.info("get_all_aligner_lot_links: END")
        return links

    # get all aligner lot links by link ID
    # input: linkID
    # output: list of aligner lot links
    def get_aligner_lot_links_by_id(self, id: int) -> list:
        try:
            self.LOG.info("get_aligner_lot_links_by_id: Start")

            links = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_aligner_lot_links_by_link, (id,))
                if len(sql.table) != 0:
                    links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligner_lot_links_by_id query"
                    )

        except Exception as e:
            self.LOG.error("get_aligner_lot_links_by_id: error={}".format(e))
            self.LOG.info("get_aligner_lot_links_by_id: END")
            return []  # other error

        self.LOG.info("get_aligner_lot_links_by_id: AlignerLotLinks={}".format(links))
        self.LOG.info("get_aligner_lot_links_by_id: END")
        return links

    # get all aligner lot links by aligner ID
    # input: alignerID
    # output: list of aligner lot links
    def get_aligner_lot_links_by_aligner_id(self, alignerID: int) -> list:
        try:
            self.LOG.info("get_aligner_lot_links_by_aligner_id: Start")

            links = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_aligner_lot_links_by_aligner, (alignerID,))
                if len(sql.table) != 0:
                    links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligner_lot_links_by_aligner_id query"
                    )

        except Exception as e:
            self.LOG.error("get_aligner_lot_links_by_aligner_id: error={}".format(e))
            self.LOG.info("get_aligner_lot_links_by_aligner_id: END")
            return []  # other error

        self.LOG.info(
            "get_aligner_lot_links_by_aligner_id: AlignerLotLinks={}".format(links)
        )
        self.LOG.info("get_aligner_lot_links_by_aligner_id: END")
        return links

    # get all aligner lot links by lot ID
    # input: lotID
    # output: list of aligner lot links
    def get_aligner_lot_links_by_lot_id(self, lotID: int) -> list:
        try:
            self.LOG.info("get_aligner_lot_links_by_lot_id: Start")

            links = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_aligner_lot_links_by_lot, (lotID,))
                if len(sql.table) != 0:
                    links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_aligner_lot_links_by_lot_id query"
                    )

        except Exception as e:
            self.LOG.error("get_aligner_lot_links_by_lot_id: error={}".format(e))
            self.LOG.info("get_aligner_lot_links_by_lot_id: END")
            return []  # other error

        self.LOG.info(
            "get_aligner_lot_links_by_lot_id: AlignerLotLinks={}".format(links)
        )
        self.LOG.info("get_aligner_lot_links_by_lot_id: END")
        return links

    def create_lot_batch(
        self,
        verification: Verification,
        gaugeID: int | None = None,
    ) -> int:
        try:
            self.LOG.info("create_lot_batch: verification={}".format(verification))

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.insert_aligner_lot_batch,
                        (verification.get_verification(), gaugeID),
                    )

                    if len(sql.table) != 0:
                        batchID = int(sql.table[0]["ID"])
                    else:
                        raise Exception(
                            "No results found with the insert_aligner_lot_batch query!"
                        )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_lot_batch: error={}".format(e))
            return -1

        self.LOG.info("create_lot_batch: END")
        return batchID

    # create new aligner lot links
    # input: verification, alignerID, lotIDs as [1,2,3,4]
    def create_aligner_lot_links(
        self,
        verification: Verification,
        alignerID: int,
        lotIDs: list,
        lotbatchID: int | None = None,
    ) -> list:
        try:
            self.LOG.info(
                "create_aligner_lot_links: verification={} alignerID={} lotIDs={}".format(
                    verification, alignerID, lotIDs
                )
            )

            info = []

            # check verification
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # create a batch if none is provided
                if lotbatchID is None:
                    lotbatchID = self.create_lot_batch(verification)
                    if lotbatchID < 0:
                        raise Exception(
                            "No results found inserting the lot batch, canceling lot linking!"
                        )

                # link aligners, batch, and lot
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.insert_aligner_lot_links,
                        (
                            lotbatchID,
                            alignerID,
                            verification.get_verification(),
                            ",".join(map(str, lotIDs)),
                        ),
                    )
                    if len(sql.table) != 0:
                        info = sql.table

                        # log per lot
                        for lotID in lotIDs:
                            self.log_aligner(
                                alignerID,
                                "LotNumber: {0} LotBatchID: {1}".format(
                                    lotID, lotbatchID
                                ),
                                "Lot Updated",
                                verification,
                                7,
                            )
                    else:
                        raise Exception(
                            "No results found with the create_aligner_lot_links query"
                        )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_aligner_lot_links: error={}".format(e))
            self.LOG.info("create_aligner_lot_links: END")
            return []  # other error

        self.LOG.info("create_aligner_lot_links: AlignerLotLinks={}".format(info))
        self.LOG.info("create_aligner_lot_links: END")
        return info

    # update lotID or/and status of aligner lot link
    # input: verification, linkID, lotID, status
    def update_aligner_lot_links(
        self, verification: Verification, linkID: int, lotID: int, status: int
    ) -> object:
        try:
            self.LOG.info(
                "update_aligner_lot_links: verification={} linkID={} lotID={} status={}".format(
                    verification, linkID, lotID, status
                )
            )

            info = {}

            # check verification
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    if lotID is not None:
                        sql.execute(
                            self.update_aligner_lot_links_lotID, (lotID, linkID)
                        )
                        if len(sql.table) != 0:
                            info["linkID_lot"] = sql.table[0]["ID"]
                        else:
                            raise Exception(
                                "No results found with the update_aligner_lot_links_lot query"
                            )

                    if status is not None:
                        sql.execute(
                            self.update_aligner_lot_links_status, (status, linkID)
                        )
                        if len(sql.table) != 0:
                            info["linkID_status"] = sql.table[0]["ID"]
                        else:
                            raise Exception(
                                "No results found with the update_aligner_lot_links_status query"
                            )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_aligner_lot_links: error={}".format(e))
            self.LOG.info("update_aligner_lot_links: END")
            return -1  # other error

        self.LOG.info("update_aligner_lot_links: AlignerLotLinks={}".format(info))
        self.LOG.info("update_aligner_lot_links: END")
        return info

    # remove aligner lot link
    # input: verification, linkID
    # change status to 12 (inactive)
    def remove_aligner_lot_link(self, verification: Verification, linkID: int) -> int:
        try:
            self.LOG.info("remove_aligner_lot_link: Start")

            result = -1
            # check verification
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(self.update_aligner_lot_links_status, (12, linkID))
                    if len(sql.table) != 0:
                        result = 0
                    else:
                        raise Exception(
                            "No results found with the remove_aligner_lot_link query"
                        )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("remove_aligner_lot_link: error={}".format(e))
            self.LOG.info("remove_aligner_lot_link: END")
            return -1  # other error

        self.LOG.info("remove_aligner_lot_link: AlignerLotLinks={}".format(result))
        self.LOG.info("remove_aligner_lot_link: END")
        return result


# UNIT TESTING
def main():
    return


# import on the bottom for circular import
from .fixit_pull import Fixit
from .lot_pull import Lot

if __name__ == "__main__":
    main()
