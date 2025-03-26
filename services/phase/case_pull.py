#!/usr/bin/env python3.7

from os import link
from typing import List, Dict

from .sql_config import SQLConfig
from .employee_pull import Employee
from .file_pull import File
from .sql_pull import SQL_Pull
from .shade_regex import gen_steps
from .case_config import CaseConfig
from .gauge_pull import Gauge
from .location_pull import Location
from .verification_pull import Verification
from .constants import LogTypes, Locations

import math
import os
import requests
import json


class Case(CaseConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        CaseConfig.__init__(self, sql_config)

        # initialize gauge
        self.gauge = Gauge()

        # initialize files
        self.files = File()

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

    def create_case(
        self,
        customerID: str,
        patientFirst: str,
        patientLast: str,
        shade: str,
        rxNumber: str,
        dueDate: str,
        products: list,
        doctorName: str,
        workorderNotes: str,
        digitalScanner: str,
        webComments: str,
        remoteCaseNumber: int,
        shipDeliveryName: str,
        shipAddress1: str,
        shipAddress2: str,
        shipCity: str,
        shipState: str,
        shipZipCode: str,
        shipCountry: str,
        patientChart: str,
        verification: Verification,
    ) -> list:
        try:
            self.LOG.info(
                "create_case: customerID={} patientFirst={} patientLast={} shade={} rxNumber={} dueDate={} products={} doctorName={} workorderNotes={} digitalScanner={} webComments={} remoteCaseNumber={} shipDeliveryName={} shipAddress1={} shipAddress2={} shipCity={} shipState={} shipZipCode={} shipCountry={} verification={}".format(
                    customerID,
                    patientFirst,
                    patientLast,
                    shade,
                    rxNumber,
                    dueDate,
                    products,
                    doctorName,
                    workorderNotes,
                    digitalScanner,
                    webComments,
                    remoteCaseNumber,
                    shipDeliveryName,
                    shipAddress1,
                    shipAddress2,
                    shipCity,
                    shipState,
                    shipZipCode,
                    shipCountry,
                    verification,
                )
            )

            case = {}
            caseID = ""

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                values = {
                    "labID": "Phase",
                    "customerID": customerID,
                    "patientFirst": patientFirst,
                    "patientLast": patientLast,
                    "shade": shade,
                    "rxNumber": rxNumber,
                    "dueDate": dueDate,
                    "products": products,
                    "doctorName": doctorName,
                    "workorderNotes": workorderNotes,
                    "digitalScanner": digitalScanner,
                    "webComments": webComments,
                    "remoteCaseNumber": remoteCaseNumber,
                    "shipDeliveryName": shipDeliveryName,
                    "shipAddress1": shipAddress1,
                    "shipAddress2": shipAddress2,
                    "shipCity": shipCity,
                    "shipState": shipState,
                    "shipZipCode": shipZipCode,
                    "shipCountry": shipCountry,
                    "patientChart": patientChart,
                }
                headers = {
                    "Content-type": "application/json",
                    "Accept": "application/json",
                }

                session = requests.Session()

                response = session.post(
                    os.getenv("MAGIC_TOUCH_URL")
                    + "/Case/AddCase/token={}".format(os.getenv("MAGIC_TOUCH_TOKEN")),
                    data=json.dumps(values),
                    headers=headers,
                )
                if response.status_code != 200:
                    raise Exception("Failure to enter case info into {database}!")

                # get caseID
                info = response.json()
                caseID = info["id"]
                case = self.create_phase_case(caseID, verification)

            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_case: error={}".format(e))
            self.LOG.info("create_case: END")
            return {}, ""  # other error

        self.LOG.info("create_case: case={} caseID={}".format(case, caseID))
        self.LOG.info("create_case: END")
        return case, caseID  # no error

    def create_phase_case(
        self,
        caseID: str,
        verification: Verification,
        locationID: int = Locations.CAD_IMPORT.value,
    ) -> dict:
        try:
            self.LOG.info(
                "create_phase_case: caseID={} verification={} locationID={}".format(
                    caseID, verification, locationID
                )
            )

            case = {}

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # insert into sql server
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.insert_case,
                        (caseID, verification.get_verification(), locationID),
                    )

                    if len(sql.table) != 0:
                        case = sql.table[0]
                    else:
                        raise Exception("No results found with the insert_case query!")
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_phase_case: error={}".format(e))
            self.LOG.info("create_phase_case: END")
            return {}  # other error

        self.LOG.info("create_phase_case: case={}".format(case))
        self.LOG.info("create_phase_case: END")
        return case  # no error

    def get_active_case_duplicates(
        self, startdate: str, enddate: str, offset: int, rows: int
    ) -> list:
        try:
            self.LOG.info(
                "get_active_case_duplicates: startdate={} enddate={} offset={} rows={}".format(
                    startdate, enddate, offset, rows
                )
            )

            matches = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_duplicate_cases_by_shade_patientname,
                    (startdate, enddate, offset, rows),
                )

                if len(sql.table) != 0:
                    matches = sql.table
                else:
                    raise Exception(
                        "No results found with the get_duplicate_cases_by_shade_patientname query!"
                    )

        except Exception as e:
            self.LOG.error("get_active_case_duplicates: error={}".format(e))
            self.LOG.info("get_active_case_duplicates: END")
            return []  # other error

        self.LOG.info("get_active_case_duplicates: matches={}".format(matches))
        self.LOG.info("get_active_case_duplicates: END")
        return matches  # no error

    def get_cases_by_filter(
        self,
        inputs: dict,
        offset: int = 0,
        rows: int = 100,
        gaugeID: int | None = None,
        use_limiter: bool = True,
    ) -> list:
        try:
            self.LOG.info(
                "get_cases_by_filter: inputs={} offset={} rows={} gaugeID={}".format(
                    inputs, offset, rows, gaugeID
                )
            )

            # update gauge
            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "get_cases_by_filter",
                label="initializing",
                limit=0,
                index=0,
                length=1,
                constant=0,
            )

            # pull outer_restrictions, inner_restrictions and organizers
            inner_restrictions = []
            outer_restrictions = []
            organizers = []
            for i, key in enumerate(inputs.keys()):
                # define input from current key
                sub_inputs = inputs[key]

                # see if key provided exists in case filters
                if key not in self.case_filters.keys():
                    key = "default"
                    if "default" not in self.case_filters.keys():
                        raise Exception(
                            "No default filter could be found in the case_filters!"
                        )

                # append if there is an inner where
                if (
                    "INNER_WHERE" in self.case_filters[key].keys()
                    and "inner" in sub_inputs.keys()
                ):
                    # pull input
                    parts = []
                    for input in sub_inputs["inner"]:
                        # format only if list is > 0
                        if len(input) == 0:
                            parts.append(self.case_filters[key]["INNER_WHERE"])
                        # format for each list item given
                        else:
                            parts.append(
                                self.case_filters[key]["INNER_WHERE"].format(*input)
                            )
                    # append parts to outer_restrictions
                    inner_restrictions.append(
                        "(" + " or ".join(parts) + ")" if len(parts) > 0 else ""
                    )
                self.LOG.info(
                    "get_cases_by_filter: inner_restrictions={}".format(
                        inner_restrictions
                    )
                )

                # append if there is an outer where
                if (
                    "OUTER_WHERE" in self.case_filters[key].keys()
                    and "outer" in sub_inputs.keys()
                ):
                    # pull input
                    parts = []
                    for input in sub_inputs["outer"]:
                        # format only if list is > 0
                        if len(input) == 0:
                            parts.append(self.case_filters[key]["OUTER_WHERE"])
                        # format for each list item given
                        else:
                            parts.append(
                                self.case_filters[key]["OUTER_WHERE"].format(*input)
                            )
                    # append parts to outer_restrictions
                    outer_restrictions.append(
                        "(" + " or ".join(parts) + ")" if len(parts) > 0 else ""
                    )
                self.LOG.info(
                    "get_cases_by_filter: outer_restrictions={}".format(
                        outer_restrictions
                    )
                )

                # append if there is a order
                if "ORDER" in self.case_filters[key].keys():
                    order_term = self.case_filters[key]["ORDER"]
                    # only append single instance of a order by term
                    if order_term not in organizers:
                        organizers.append(self.case_filters[key]["ORDER"])
                self.LOG.info("get_cases_by_filter: organizers={}".format(organizers))

                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "get_cases_by_filter",
                    label="filtering {}".format(key),
                    index=i + 1,
                    length=len(inputs.keys()),
                    limit=80,
                )

            # pull outer_restriction, inner_restriction, and organizer string from lists
            inner_restriction = (
                "WHERE " + " and ".join(inner_restrictions)
                if len(inner_restrictions) > 0
                else ""
            )
            outer_restriction = (
                "WHERE " + " and ".join(outer_restrictions)
                if len(outer_restrictions) > 0
                else ""
            )
            organizer = (
                "ORDER BY " + ", ".join(organizers)
                if len(organizers) > 0
                else "ORDER BY CaseNumber DESC"
            )

            # update gauge
            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "get_cases_by_filter",
                label="building restrictions",
                limit=0,
                index=0,
                length=1,
                constant=90,
            )

            # get cases
            cases = []
            with SQL_Pull()(self.sql_config)() as sql:
                # generate custom query
                query = ""
                if use_limiter is True:
                    query = self.lookup_with_row_offset.format(
                        inner_restriction, outer_restriction, organizer
                    )

                    # log generation
                    self.LOG.info("get_cases_by_filter: query={}".format(query))

                    sql.execute(query, (offset, rows))
                else:
                    query = self.lookup_template.format(
                        inner_restriction, outer_restriction, organizer
                    )

                    # log generation
                    self.LOG.info("get_cases_by_filter: query={}".format(query))

                    sql.execute(query)

                # execute query
                if len(sql.table) != 0:
                    cases = sql.table
                else:
                    raise Exception("No results found with the lookup_query query!")

            # update gauge
            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "get_cases_by_filter",
                label="complete",
                limit=0,
                index=0,
                length=1,
                constant=100,
            )

        except Exception as e:
            self.LOG.error("get_cases_by_filter: error={}".format(e))
            self.LOG.info("get_cases_by_filter: END")
            return []  # other error

        self.LOG.info("get_cases_by_filter: cases={}".format(len(cases)))
        self.LOG.info("get_cases_by_filter: END")
        return cases  # no error

    def get_cases_by_filter_no_offset(
        self, inputs: dict, gaugeID: int | None = None
    ) -> list:
        try:
            self.LOG.info(
                "get_cases_by_filter: rows={} gaugeID={}".format(inputs, gaugeID)
            )

            cases = self.get_cases_by_filter(inputs, gaugeID=gaugeID, use_limiter=False)

        except Exception as e:
            self.LOG.error("get_cases_by_filter_no_offset: error={}".format(e))
            self.LOG.info("get_cases_by_filter_no_offset: END")
            return []  # other error

        self.LOG.info("get_cases_by_filter_no_offset: cases={}".format(len(cases)))
        self.LOG.info("get_cases_by_filter_no_offset: END")
        return cases  # no error

    def get_cases_in_range(
        self, date: str, date_range: int, offset: int, rows: int
    ) -> list:
        try:
            self.LOG.info(
                "get_cases_in_range: date={} date_range={} offset={} rows={}".format(
                    date, date_range, offset, rows
                )
            )

            cases = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_cases_by_range, (date, date_range, date, offset, rows)
                )

                if len(sql.table) != 0:
                    cases = sql.table
                else:
                    raise Exception(
                        "No results found with the get_cases_in_range query!"
                    )

        except Exception as e:
            self.LOG.error("get_cases_in_range: error={}".format(e))
            self.LOG.info("get_cases_in_range: END")
            return []  # other error

        self.LOG.info("get_cases_in_range: cases={}".format(cases))
        self.LOG.info("get_cases_in_range: END")
        return cases  # no error

    def get_cases_in_range_by_case(
        self, caseNumber: str, offset: int, rows: int
    ) -> list:
        try:
            self.LOG.info(
                "get_cases: caseNumber={} offset={} rows={}".format(
                    caseNumber, offset, rows
                )
            )

            cases = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_cases_by_range_by_case, (caseNumber, offset, rows))

                if len(sql.table) != 0:
                    cases = sql.table
                else:
                    raise Exception(
                        "No results found with the get_cases_in_range_by_case query!"
                    )

        except Exception as e:
            self.LOG.error("get_cases: error={}".format(e))
            self.LOG.info("get_cases: END")
            return []  # other error

        self.LOG.info("get_cases: cases={}".format(cases))
        self.LOG.info("get_cases: END")
        return cases  # no error

    # gets a list of cases associated with a caseid
    # input: CaseIDs
    # output: Cases on success
    def get_cases_by_ids(self, caseIDs: list) -> list:
        try:
            self.LOG.info("get_cases_by_ids: caseIDs={}".format(caseIDs))

            cases = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get caseIDs with info above
                sql.execute(self.ids_query, (",".join(map(str, caseIDs))))
                if len(sql.table) != 0:
                    cases = sql.table
                else:
                    raise Exception("No results found with the ids_query query!")

        except Exception as e:
            self.LOG.error("get_cases_by_ids: error={}".format(e))
            self.LOG.info("get_cases_by_ids: END")
            return []  # other error

        self.LOG.info("get_cases_by_ids: cases={}".format(len(cases)))
        self.LOG.info("get_cases_by_ids: END")
        return cases  # no error

    # gets a list of cases associated with a caseid
    # input: CaseID
    # output: Cases on success
    def get_cases_by_id(self, caseID: str) -> list:
        try:
            self.LOG.info("get_cases_by_id: caseID={}".format(caseID))

            cases = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get caseID with info above
                sql.execute(self.id_query, (caseID))
                if len(sql.table) != 0:
                    cases = sql.table
                else:
                    raise Exception("No results found with the id_query query!")

        except Exception as e:
            self.LOG.error("get_cases_by_id: error={}".format(e))
            self.LOG.info("get_cases_by_id: END")
            return []  # other error

        self.LOG.info("get_cases_by_id: cases={}".format(len(cases)))
        self.LOG.info("get_cases_by_id: END")
        return cases  # no error

    # gets all products associated with a given case
    # input: CaseNumber
    # output: Files on success, [] on error
    def get_products_by_case(self, caseNumber: str) -> list:
        try:
            self.LOG.info("get_products_by_case: caseNumber={}".format(caseNumber))

            products = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.product_query, (caseNumber))
                if len(sql.table) != 0:
                    products = sql.table
                else:
                    raise Exception("No results found with the product_query query!")

        except Exception as e:
            self.LOG.error("get_products_by_case: error={}".format(e))
            self.LOG.info("get_products_by_case: END")
            return []  # other error

        self.LOG.info("get_products_by_case: products={}".format(products))
        self.LOG.info("get_products_by_case: END")
        return products  # no error

    # gets all basic case info associated with a given case
    # input: CaseNumber
    # output: Files on success, [] on error
    def get_info_by_case(self, caseNumber: str) -> list:
        try:
            self.LOG.info("get_info_by_case: caseNumber={}".format(caseNumber))

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.case_query, (caseNumber))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception("No results found with the case_query query!")

        except Exception as e:
            self.LOG.error("get_info_by_case: error={}".format(e))
            self.LOG.info("get_info_by_case: END")
            return []  # other error

        self.LOG.info("get_info_by_case: info={}".format(info))
        self.LOG.info("get_info_by_case: END")
        return info  # no error

    # gets all basic case info associated with a given case
    # input: LocationsIncluded, LocationsExcluded
    # output: Cases on success, [] on error
    def get_cases_pending(
        self, included_locations: list, excluded_locations: list | None = None
    ) -> list:
        try:
            self.LOG.info(
                "get_cases_pending: included_locations={} excluded_locations={}".format(
                    included_locations, excluded_locations
                )
            )

            # get excluded locations via following locations of included locations
            if excluded_locations == [None]:
                excluded_locations = []
                for location in included_locations:
                    with Location() as loc:
                        excluded_locations.extend(
                            [
                                _["FollowingLocationID"]
                                for _ in loc.get_locations_following_location(location)
                            ]
                        )

            # make sure we are given included and excluded
            if included_locations is None or len(included_locations) == 0:
                included_locations = [-1]
            if len(excluded_locations) == 0:
                excluded_locations = [-1]

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_cases_pending_by_location.format(
                        ",".join(["?"] * len(included_locations)),
                        ",".join(["?"] * len(excluded_locations)),
                    ),
                    (*included_locations, *excluded_locations),
                )
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_cases_pending_by_location query!"
                    )

        except Exception as e:
            self.LOG.error("get_cases_pending: error={}".format(e))
            self.LOG.info("get_cases_pending: END")
            return []  # other error

        self.LOG.info("get_cases_pending: info={}".format(info))
        self.LOG.info("get_cases_pending: END")
        return info  # no error

    # Given a list of case files, uploads their bytes and returns there file ID from SQL
    # input: {"caseID": "as;lkjfa87dfas9df6397", "typeID": 2, "bytes": ..., "filename": "attachment_27862.pdf"}
    # output: {LinkID...}
    def upload_case_files(
        self, verification: Verification, case_files: str, gaugeID: int | None = None
    ) -> dict:
        try:
            self.LOG.info(
                "upload_case_files: verification={} case_files={} gaugeID={}".format(
                    verification, case_files, gaugeID
                )
            )

            results = {}

            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "uploading_files_and_creating_links",
                index=0,
                length=100,
                limit=100,
                constant=0,
                label="Initializing",
            )

            for i, case_file in enumerate(case_files):
                # get info
                caseID = case_file["caseID"]
                filetypeID = case_file["typeID"]
                num_bytes = case_file["bytes"]
                filename = case_file["filename"]

                # upload file
                if self.files.upload_to_blob(verification, filename, num_bytes) != 0:
                    raise Exception(
                        "No results found uploading the given file {} to the blobstorage medium defined!".format(
                            filename
                        )
                    )

                # link file with case
                results[caseID] = [
                    *results.get(caseID, []),
                    self.insert_file_to_case(
                        caseID, filetypeID, filename, verification
                    ),
                ]

                # update gauge
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "linking",
                    index=i + 1,
                    length=len(case_files),
                    limit=100,
                    label="linked {} with {}".format(caseID, filename),
                )

        except Exception as e:
            self.LOG.error("upload_case_files: error={}".format(e))
            self.LOG.info("upload_case_files: END")
            return {}  # other error

        self.LOG.info("upload_case_files: results={}".format(results))
        self.LOG.info("upload_case_files: END")
        return results  # no error

    # Given case info and filetypeID and path, inserts a file link into SQL
    # input: CaseNumber, FileTypeID, Path, Verification, Status
    # output: LinkID
    def insert_file_to_case(
        self,
        caseID: str,
        filetypeID: int,
        path: str,
        verification: Verification,
        status: int = 11,
    ) -> int:
        try:
            self.LOG.info(
                "insert_file_to_case: caseID={} filetypeID={} path={} verification={}".format(
                    caseID, filetypeID, path, verification
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
                        self.insert_case_file,
                        (
                            caseID,
                            files[0]["FileID"],
                            verification.get_verification(),
                            status,
                        ),
                    )
                    if len(sql.table) != 0:
                        linkID = int(sql.table[0]["ID"])

                    else:
                        raise Exception(
                            "No results found with the insert_aligner_file query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("insert_file_to_case: error={}".format(e))
            self.LOG.info("insert_file_to_case: END")
            return -1  # other error

        self.LOG.info("insert_file_to_case: linkID={}".format(linkID))
        self.LOG.info("insert_file_to_case: END")
        return linkID  # no error

    # # Update Case File Link Status
    # Input: Status, IDs
    def update_case_file_links_status(
        self, status: int, ids: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "update_case_file_links_status: status={} ids={} verification={}".format(
                    status, ids, verification
                )
            )

            result = []

            if (
                ids is not None
                and isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    id_list = ",".join(map(str, ids))
                    sql.execute(
                        self.update_case_file_link_status,
                        (status, id_list),
                    )
                    if len(sql.table) > 0:
                        result = sql.table
            else:
                raise Exception("update_case_file_links_status: Error: Missing Inputs")

        except Exception as e:
            self.LOG.error("update_case_file_links_status: error={}".format(e))
            return []

        self.LOG.info("update_case_file_links_status: result={}".format(result))
        self.LOG.info("update_case_file_links_status: END")
        return result

    def get_files_by_case(self, caseNumber: str, filetypeID: int | None = None) -> list:
        try:
            self.LOG.info(
                "get_files_by_case: caseNumber={} filetypeID={}".format(
                    caseNumber, filetypeID
                )
            )

            files = []
            with SQL_Pull()(self.sql_config)() as sql:
                if filetypeID is None:
                    sql.execute(self.get_active_case_files_by_all, (caseNumber))
                else:
                    sql.execute(
                        self.get_active_case_files_by_type, (filetypeID, caseNumber)
                    )
                if len(sql.table) != 0:
                    files = sql.table
                else:
                    raise Exception(
                        "No results found with the get_active_case_files_by_type query!"
                    )

        except Exception as e:
            self.LOG.error("get_files_by_case: error={}".format(e))
            self.LOG.info("get_files_by_case: END")
            return -1  # other error

        self.LOG.info("get_files_by_case: END")
        return files  # no error

    # gets all case flag options
    # input: N/A
    # output: CaseFlags on success, [] on error
    def get_case_flags(self) -> list:
        try:
            self.LOG.info("get_case_flags: START")

            case_flags = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_case_flags)
                if len(sql.table) != 0:
                    case_flags = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_case_flags query!"
                    )

        except Exception as e:
            self.LOG.error("get_case_flags: error={}".format(e))
            self.LOG.info("get_case_flags: END")
            return []  # other error

        self.LOG.info("get_case_flags: case_flags={}".format(len(case_flags)))
        self.LOG.info("get_case_flags: END")
        return case_flags  # no error

    # gets all case flags for the given case and status
    # input: case, status
    # output: CaseFlags on success, [] on error
    def get_case_flags_by_case(self, cases: list, statuses: list = [11]) -> list:
        try:
            self.LOG.info(f"get_case_flags_by_case: cases={cases} status={statuses}")

            case_flags = []
            with SQL_Pull()(self.sql_config)() as sql:

                sql.execute(
                    self.get_case_flags_for_given_case,
                    (",".join(map(str, statuses)), ",".join(map(str, cases))),
                )
                if len(sql.table) != 0:
                    case_flags = sql.table
                else:
                    raise Exception(
                        "No results found with the get_case_flags_for_given_case query!"
                    )

        except Exception as e:
            self.LOG.error("get_case_flags_for_given_case: error={}".format(e))
            self.LOG.info("get_case_flags_for_given_case: END")
            return []  # other error

        self.LOG.info(
            "get_case_flags_for_given_case: case_flags={}".format(len(case_flags))
        )
        self.LOG.info("get_case_flags_for_given_case: END")
        return case_flags  # no error

    # Creates a flag
    # input: FlagType, Color, Weight, Icon
    # output: CaseFlagID on success, -1 on error
    def create_case_flag(
        self,
        flagType: str,
        color: str,
        weight: float,
        icon: str,
        description: str,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                f"create_case_flag: flagType={flagType} color={color} weight={weight} icon={icon} description={description} verification={verification}"
            )

            flag_ID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_case_flag,
                        (flagType, color, weight, icon, description),
                    )
                    if len(sql.table) != 0:
                        flag_ID = int(sql.table[0]["ID"])

                    else:
                        raise Exception(
                            "No results found with the create_case_flag query!"
                        )
                else:
                    raise Exception("Invalid Verification!")

        except Exception as e:
            self.LOG.error("create_case_flag: error={}".format(e))
            self.LOG.info("create_case_flag: END")
            return -1  # other error

        self.LOG.info("create_case_flag: flag_ID={}".format(flag_ID))
        self.LOG.info("create_case_flag: END")
        return flag_ID  # no error

    # update flag
    # input: FlagType, Color, Weight, Icon, description, CaseFlagID, Status
    # output: CaseFlagID on success, -1 on error
    def update_case_flag(
        self,
        flagType: str,
        color: str,
        weight: float,
        icon: str,
        description: str,
        caseFlagID: int,
        status: int,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                f"update_case_flag: flagType={flagType} color={color} weight={weight} icon={icon} description={description} caseFlagID={caseFlagID} status={status} verification={verification}"
            )

            flag_ID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.edit_case_flag,
                        (
                            flagType,
                            color,
                            weight,
                            description,
                            icon,
                            status,
                            caseFlagID,
                        ),
                    )
                    if len(sql.table) != 0:
                        flag_ID = int(sql.table[0]["ID"])

                    else:
                        raise Exception(
                            "No results found with the update_case_flag query!"
                        )
                else:
                    raise Exception("Invalid Verification!")

        except Exception as e:
            self.LOG.error("update_case_flag: error={}".format(e))
            self.LOG.info("update_case_flag: END")
            return -1  # other error

        self.LOG.info("update_case_flag: flag_ID={}".format(flag_ID))
        self.LOG.info("update_case_flag: END")
        return flag_ID  # no error

    # gets case flag links
    # input: N/A
    # output: CaseFlags on success, [] on error
    def get_case_flag_links(self, statuses: list = [11, 12]) -> list:
        try:
            self.LOG.info(f"get_case_flag_links: statuses={statuses}")

            case_flag_links = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_case_flag_links_by_status, (",".join(map(str, statuses)))
                )
                if len(sql.table) != 0:
                    case_flag_links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_case_flag_links query!"
                    )

        except Exception as e:
            self.LOG.error("get_case_flag_links: error={}".format(e))
            self.LOG.info("get_case_flag_links: END")
            return []  # other error

        self.LOG.info("get_case_flag_links: case_flag_links={}".format(case_flag_links))
        self.LOG.info("get_case_flag_links: END")
        return case_flag_links  # no error

    # gets case flag link logs by caseNumber
    # input: CaseNumber
    # output: CaseFlagLinkLogs on success, [] on error
    def get_case_flag_link_logs_by_caseNumber(self, caseNumber) -> list:
        try:
            self.LOG.info(
                f"get_case_flag_link_logs_by_caseNumber: caseNumber={caseNumber}"
            )

            case_flag_link_logs = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_case_flag_link_logs_for_caseNumber, (caseNumber))
                if len(sql.table) != 0:
                    case_flag_link_logs = sql.table
                else:
                    raise Exception(
                        "No results found with the get_case_flag_link_logs_for_caseNumber query!"
                    )

        except Exception as e:
            self.LOG.error("get_case_flag_link_logs_by_caseNumber: error={}".format(e))
            self.LOG.info("get_case_flag_link_logs_by_caseNumber: END")
            return []  # other error

        self.LOG.info(
            "get_case_flag_link_logs_by_caseNumber: case_flags={}".format(
                case_flag_link_logs
            )
        )
        self.LOG.info("get_case_flag_link_logs_by_caseNumber: END")
        return case_flag_link_logs  # no error

    # Creates a link between the given caseID and flagID
    # input: verification, caseID, flagID
    # output: CaseFlagLinkID on success, -1 on error
    def create_case_flag_link(
        self, verification: Verification, caseNumber: str, flagID: int
    ) -> int:
        try:
            self.LOG.info(
                f"create_case_flag_link: verification={verification} caseNumber={caseNumber} flagID={flagID}"
            )

            flag_link_ID = -1

            # get caseID from caseNumber
            caseID = self.get_info_by_case(caseNumber)[0]["CaseID"]

            # Check if an active flag already exists for the given case
            current_flags = self.get_case_flags_by_case([caseNumber])
            matching_flag_found = (
                len(
                    list(
                        filter(lambda flag: flag.get("FlagID") == flagID, current_flags)
                    )
                )
                > 0
            )

            if matching_flag_found:
                raise Exception("Flag is already linked to case!")
            else:
                with SQL_Pull()(self.sql_config)() as sql:
                    if (
                        isinstance(verification, Verification)
                        and verification.get_verification() != -1
                    ):
                        sql.execute(
                            self.insert_case_flag_link,
                            (
                                flagID,
                                caseNumber,
                                caseID,
                                verification.get_verification(),
                            ),
                        )
                        if len(sql.table) != 0:
                            flag_link_ID = int(sql.table[0]["ID"])
                            # Generate flag link log using flag link ID created
                            self.log_flag_link(flag_link_ID, verification, 50, 0)

                        else:
                            raise Exception(
                                "No results found with the get_case_flag_links query!"
                            )
                    else:
                        raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_case_flag_link: error={}".format(e))
            self.LOG.info("create_case_flag_link: END")
            return -1  # other error

        self.LOG.info("create_case_flag_link: flag_link_ID={}".format(flag_link_ID))
        self.LOG.info("create_case_flag_link: END")
        return flag_link_ID  # no error

    # change status of case_flag
    # input: verification, caseflaglinkID, status
    # output: caseflaglinkID
    def update_case_flag_link(
        self, verification: Verification, linkID: int, status: int
    ) -> int:
        try:
            self.LOG.info(
                f"update_case_flag_link: verification={verification} linkID={linkID} status={status}"
            )

            flag_ID = -1
            # check verification
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # Generate Query based on which status is given
                queries = [
                    {
                        "query": "Status = ?, CheckedIn = GETDATE(), CheckedInVerificationID = ?",
                        "logTypeID": 50,
                    },
                    {
                        "query": "Status = ?, CheckedOut = GETDATE(), CheckedOutVerificationID = ?",
                        "logTypeID": 51,
                    },
                ]

                # Assign check in or out value to pass to query and logging function
                if status == 11:
                    check_out_or_in = 0
                elif status == 12:
                    check_out_or_in = 1
                else:
                    raise Exception("Incorrect status given")

                with SQL_Pull()(self.sql_config)() as sql:
                    result, _ = sql.execute(
                        self.change_case_flag_link.format(
                            queries[check_out_or_in]["query"]
                        ),
                        (status, verification.get_verification(), linkID),
                    )
                    if len(result) != 0:
                        flag_ID = result[0]["ID"]
                        self.log_flag_link(
                            flag_ID,
                            verification,
                            queries[check_out_or_in]["logTypeID"],
                            check_out_or_in,
                        )
                    else:
                        raise Exception(
                            "No results found with the update_case_flag_link query"
                        )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_case_flag_link: error={}".format(e))
            self.LOG.info("update_case_flag_link: END")
            return -1  # other error

        self.LOG.info("update_case_flag_link: case_flag_link={}".format(result))
        self.LOG.info("update_case_flag_link: END")
        return flag_ID

    # logs a change to a case_flag_link
    def log_flag_link(
        self,
        flag_link_ID: int,
        verification: Verification,
        logtype: int,
        check_in_or_out: int,
    ) -> int:
        try:
            self.LOG.info(
                "log_flag_link: flag_link_ID={} verification={} logtype={} check_in_or_out={}".format(
                    flag_link_ID, verification, logtype, check_in_or_out
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    change = [
                        f"Checked In: {flag_link_ID}",
                        f"Checked Out: {flag_link_ID}",
                    ]
                    description = ["Flag Link Checked In", "Flag Link Checked Out"]

                    self.LOG.info(f"test:{verification.get_verification()}")
                    # Format sql query with above variables depending on checked in or out
                    sql.execute(
                        self.insert_flag_link_log,
                        (
                            logtype,
                            change[check_in_or_out],
                            description[check_in_or_out],
                            verification.get_verification(),
                            flag_link_ID,
                            flag_link_ID,
                            flag_link_ID,
                            flag_link_ID,
                            flag_link_ID,
                            flag_link_ID,
                            flag_link_ID,
                            flag_link_ID,
                            flag_link_ID,
                        ),
                    )

                    if len(sql.table) != 0:
                        self.LOG.info("log_flag_link: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the insert_flag_link_log query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_flag_link: error={}".format(e))

        self.LOG.info("log_flag_link: END")
        return -1

    # gets case employee links
    # input: N/A
    # output: CaseEmployeeLinks on success, [] on error
    def get_case_employee_links(self, statuses: list = [11, 12]) -> list:
        try:
            self.LOG.info(f"get_case_employee_links: statuses={statuses}")

            case_employee_links = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_case_employee_links_by_status,
                    (",".join(map(str, statuses))),
                )
                if len(sql.table) != 0:
                    case_employee_links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_case_employee_links query!"
                    )

        except Exception as e:
            self.LOG.error("get_case_employee_links: error={}".format(e))
            self.LOG.info("get_case_employee_links: END")
            return []  # other error

        self.LOG.info(
            "get_case_employee_links: case_employee_links={}".format(
                case_employee_links
            )
        )
        self.LOG.info("get_case_employee_links: END")
        return case_employee_links  # no error

    # gets case employee link logs by case Number
    # input: caseNumber
    # output: CaseEmployeeLinkLogs on success, [] on error
    def get_case_employee_links_logs_by_case(self, caseNumber: int) -> list:
        try:
            self.LOG.info(
                f"get_case_employee_links_logs_by_case: caseNumber={caseNumber}"
            )

            case_employee_links = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_case_employee_link_logs_by_caseNumber, (caseNumber)
                )
                if len(sql.table) != 0:
                    case_employee_links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_case_employee_link_logs_by_caseNumber query!"
                    )

        except Exception as e:
            self.LOG.error("get_case_employee_links_logs_by_case: error={}".format(e))
            self.LOG.info("get_case_employee_links_logs_by_case: END")
            return []  # other error

        self.LOG.info(
            "get_case_employee_links_logs_by_case: case_employee_links={}".format(
                case_employee_links
            )
        )
        self.LOG.info("get_case_employee_links_logs_by_case: END")
        return case_employee_links  # no error

    # gets last 48 hours of case employee link logs by employeeID
    # input: employeeID
    # output: CaseEmployeeLinkLogs on success, [] on error
    def get_case_employee_links_logs_by_employee(self, employeeID: int) -> list:
        try:
            self.LOG.info(
                f"get_case_employee_links_logs_by_employee: employeeID={employeeID}"
            )

            case_employee_links = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_case_employee_link_logs_by_employeeID, (employeeID)
                )
                if len(sql.table) != 0:
                    case_employee_links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_case_employee_link_logs_by_employeeID query!"
                    )

        except Exception as e:
            self.LOG.error(
                "get_case_employee_links_logs_by_employee: error={}".format(e)
            )
            self.LOG.info("get_case_employee_links_logs_by_employee: END")
            return []  # other error

        self.LOG.info(
            "get_case_employee_links_logs_by_employee: case_employee_links={}".format(
                case_employee_links
            )
        )
        self.LOG.info("get_case_employee_links_logs_by_employee: END")
        return case_employee_links  # no error

    # Creates a link between the given caseID and employeeID if no active link already exists
    # input: employeeID, caseID
    # output: CaseEmployeeLinkID on success, -1 on error
    def create_case_employee_link(
        self, verification: Verification, caseNumber: str
    ) -> int:
        try:
            self.LOG.info(
                f"create_case_employee_link: verification={verification} caseNumber={caseNumber}"
            )

            employee_link = {}

            # get caseID
            caseID = self.get_info_by_case(caseNumber)[0]["CaseID"]

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # If an active case employee link already exists, raise exception
                    previous_cases = self.get_case_employee_links_by_case(
                        caseNumber, [11]
                    )
                    if len(previous_cases) != 0:
                        raise Exception(
                            f"An Employee is already linked to case {caseNumber}!"
                        )

                    sql.execute(
                        self.insert_case_employee_link,
                        (caseNumber, caseID, verification.get_verification()),
                    )
                    if len(sql.table) != 0:
                        employee_link["ID"] = int(sql.table[0]["ID"])
                        employee_link["VerificationID"] = int(
                            sql.table[0]["VerificationID"]
                        )
                        # Generate employee case link log using caseEmployeeLinkID created
                        self.log_case_employee_link(
                            employee_link["ID"], verification, 50
                        )

                    else:
                        raise Exception(
                            "No results found with the create_case_employee_links query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_case_employee_link: error={}".format(e))
            self.LOG.info("create_case_employee_link: END")
            return {}  # other error

        self.LOG.info(
            "create_case_employee_link: employee_link_ID={}".format(employee_link)
        )
        self.LOG.info("create_case_employee_link: END")
        return employee_link  # no error

    # Gets case employee links associated with the case given
    # Input: Case
    # Output: CaseEmployeeLinks
    def get_case_employee_links_by_case(
        self, caseNumber: int, statuses: list = [11, 12]
    ) -> list:
        try:
            self.LOG.info(
                f"get_case_employee_links_by_case: caseNumber={caseNumber} statuses={statuses}"
            )

            case_employee_links = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_case_employee_links_by_case_and_status,
                    (",".join(map(str, statuses)), caseNumber),
                )
                if len(sql.table) != 0:
                    case_employee_links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_case_employee_links query!"
                    )

        except Exception as e:
            self.LOG.error("get_case_employee_links_by_case: error={}".format(e))
            self.LOG.info("get_case_employee_links_by_case: END")
            return []  # other error

        self.LOG.info(
            "get_case_employee_links_by_case: case_employee_links={}".format(
                case_employee_links
            )
        )
        self.LOG.info("get_case_employee_links_by_case: END")
        return case_employee_links  # no error

    # Gets case employee links associated with the cases given
    # Input: Cases
    # Output: CaseEmployeeLinks
    def get_case_employee_links_by_cases(
        self, cases: list, statuses: list = [11]
    ) -> list:
        try:
            self.LOG.info(
                f"get_case_employee_links_by_case: case={cases} statuses={statuses}"
            )

            case_employee_links = []
            with SQL_Pull()(self.sql_config)() as sql:
                # Generate the number of sql executions to run. When list is larger than 300 sql will send back an error
                num_sql_executions = math.ceil(len(cases) / 300)

                for x in range(num_sql_executions):
                    # Execute sql with map converting cases[0:299] to a str, remove those cases from the initial list
                    sql.execute(
                        self.get_case_employee_links_by_cases_and_status,
                        (
                            ",".join(map(str, statuses)),
                            ",".join(map(str, cases[0:299])),
                        ),
                    )
                    del cases[0:299]

                    if len(sql.table) != 0:
                        case_employee_links = [*case_employee_links, *sql.table]

                if len(case_employee_links) == 0:
                    raise Exception(
                        "No results found with the get_case_employee_links_by_cases_and_status query!"
                    )

        except Exception as e:
            self.LOG.error("get_case_employee_links_by_cases: error={}".format(e))
            self.LOG.info("get_case_employee_links_by_cases: END")
            return []  # other error

        self.LOG.info(
            "get_case_employee_links_by_cases: case_employee_links={}".format(
                case_employee_links
            )
        )
        self.LOG.info("get_case_employee_links_by_cases: END")
        return case_employee_links  # no error

    # change status of case_employee_link
    # input: verification, caseflaglinkID, status
    # output: case_employee_link
    def update_case_employee_link(self, verification: Verification, linkID: int) -> int:
        try:
            self.LOG.info(
                f"update_case_employee_link: verification={verification} linkID={linkID}"
            )

            case_employee_link = -1
            # check verification
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # Update case_employee_link
                with SQL_Pull()(self.sql_config)() as sql:
                    result, _ = sql.execute(self.change_case_employee_link, (linkID))
                    # Log the change to the case_employee_link
                    if len(result) != 0:

                        case_employee_link = result[0]["ID"]
                        self.log_case_employee_link(
                            case_employee_link,
                            verification,
                            52,
                        )
                    else:
                        raise Exception(
                            "No results found with the update_case_employee_link query"
                        )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_case_employee_link: error={}".format(e))
            self.LOG.info("update_case_employee_link: END")
            return -1  # other error

        self.LOG.info("update_case_employee_link: case_flag_link={}".format(result))
        self.LOG.info("update_case_employee_link: END")
        return case_employee_link

    # logs a change to a case_employee_link
    def log_case_employee_link(
        self, case_employee_link_ID: int, verification: Verification, logtype: int
    ) -> int:
        try:
            self.LOG.info(
                "log_case_employee_link: case_employee_link_ID={} verification={} logtype={}".format(
                    case_employee_link_ID,
                    verification,
                    logtype,
                )
            )

            change = ""
            description = ""

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # Specify change and description based on logtype given
                    if logtype == 50:
                        change = "Checked In"
                        description = "Case Link Checked In"
                    if logtype == 52:
                        change = "Unassigned"
                        description = "Case Link Unassigned"

                    # Execute sql query with above variables
                    sql.execute(
                        self.insert_case_employee_link_log,
                        (
                            logtype,
                            change,
                            description,
                            verification.get_verification(),
                            case_employee_link_ID,
                            case_employee_link_ID,
                            case_employee_link_ID,
                            case_employee_link_ID,
                            case_employee_link_ID,
                        ),
                    )

                    if len(sql.table) != 0:
                        self.LOG.info("log_case_employee_link: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the insert_case_employee_link_log query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_case_employee_link: error={}".format(e))

        self.LOG.info("log_case_employee_link: END")
        return -1

    # gets a list of cases associated with a production_line
    # input: production_line, offset, rows
    # output: Cases on success
    def get_cases_by_production_line(
        self, production_line: int, offset: int, rows: int
    ) -> list:
        try:
            self.LOG.info(
                "get_cases_by_production_line: production_line={} offset={} rows={}".format(
                    production_line, offset, rows
                )
            )

            cases = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get cases with info above
                sql.execute(
                    self.fetch_cases_by_production_line, (production_line, offset, rows)
                )
                if len(sql.table) != 0:
                    cases = sql.table
                else:
                    raise Exception(
                        "No results found with the fetch_cases_by_production_line query!"
                    )

        except Exception as e:
            self.LOG.error("get_cases_by_production_line: error={}".format(e))
            self.LOG.info("get_cases_by_production_line: END")
            return []  # other error

        self.LOG.info("get_cases_by_production_line: cases={}".format(len(cases)))
        self.LOG.info("get_cases_by_production_line: END")
        return cases  # no error

    # get % and QTY of aligners associated with each production line
    # input: N/A
    # output: floats on success, [] on error
    def get_total_aligners_in_each_production_line(self) -> list:
        try:
            self.LOG.info("get_total_aligners_in_each_production_line: START")

            total_aligners = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get total aligners in each production line
                sql.execute(
                    self.get_total_aligners_in_production_lines,
                    (),
                )
                if len(sql.table) != 0:
                    total_aligners = sql.table
                    # Get list of quantities
                    qty_list = list(
                        map(lambda aligner: aligner["Quantity"], total_aligners)
                    )
                    # Sum list of quantities
                    qty_total = sum(qty_list)
                    # Set Percentage of each aligner object to the Aligner QTY / total qty
                    for aligner in total_aligners:
                        aligner["ActualPercentage"] = float(
                            round(aligner["Quantity"] / qty_total, 3)
                        )
                else:
                    raise Exception(
                        "No results found with the get_total_aligners_in_production_lines query!"
                    )

        except Exception as e:
            self.LOG.error(
                "get_total_aligners_in_each_production_line: error={}".format(e)
            )
            self.LOG.info("get_total_aligners_in_each_production_line: END")
            return []  # other error

        self.LOG.info(
            "get_total_aligners_in_each_production_line: total_aligners={}".format(
                total_aligners
            )
        )
        self.LOG.info("get_total_aligners_in_each_production_line: END")
        return total_aligners  # no error

    # Creates a Case ProductionLine Link
    # input: verification, caseNumber, productionLineID
    # output: CaseProductionLineLinkID on success, -1 on error
    def create_case_production_line_link(
        self, verification: Verification, caseNumber: int, lineID: int
    ) -> int:
        try:
            self.LOG.info(
                f"create_case_production_line_linkcreate_case_flag: verification={verification} caseNumber={caseNumber} lineID={lineID}"
            )

            production_line_link = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_production_line_link,
                        (caseNumber, lineID),
                    )
                    if len(sql.table) != 0:
                        production_line_link = int(sql.table[0]["ID"])

                    else:
                        raise Exception(
                            "No results found with the insert_production_line_link query!"
                        )
                else:
                    raise Exception("Invalid EmployeeID!")

        except Exception as e:
            self.LOG.error("create_case_production_line_link: error={}".format(e))
            self.LOG.info("create_case_production_line_link: END")
            return -1  # other error

        self.LOG.info(
            "create_case_production_line_link: flag_ID={}".format(production_line_link)
        )
        self.LOG.info("create_case_production_line_link: END")
        return production_line_link  # no error

    # Update Phase Case Status
    # Input: status, caseID, Verification
    def update_case_status(
        self, status: int, case_ID: str, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "update_case_status: status={} caseID={} verification={}".format(
                    status, case_ID, verification
                )
            )

            result = -1

            if (
                case_ID is not None
                and isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.update_phase_case_status,
                        (status, case_ID),
                    )
                    if len(sql.table) > 0:
                        result = sql.table
            else:
                raise Exception("update_case_status : Error: Missing Inputs")

        except Exception as e:
            self.LOG.error("update_case_status: error={}".format(e))
            return result

        self.LOG.info("update_case_file_links_status: result={}".format(result))
        self.LOG.info("update_case_file_links_status: END")
        return 0

    # Update Magic touch Case Status
    # Input: status, caseID, Verification
    def mt_case_status_update(
        self, status: str, case_ID: str, verification: Verification
    ) -> dict:
        try:
            self.LOG.info(
                "mt_case_status_update: status={} caseID={} verification={}".format(
                    status, case_ID, verification
                )
            )

            result = {}

            if (
                case_ID is not None
                and isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.update_mt_case_status,
                        (status, case_ID),
                    )
                    if len(sql.table) > 0:
                        result = sql.table[0]
            else:
                raise Exception("update_mt_case_status : Error: Missing Inputs")

        except Exception as e:
            self.LOG.error("update_mt_case_status: error={}".format(e))
            return result

        self.LOG.info("update_mt_case_status: result={}".format(result))
        self.LOG.info("update_mt_case_status: END")
        return result

    # updates the location assigned to a given case
    # input: Verification, CaseID, Location
    # output: Location on success, -1 on error
    def update_location(
        self, verification: Verification, caseID: int, location: int
    ) -> int:
        try:
            self.LOG.info(
                "update_location: verification={} caseID={} location={}".format(
                    verification, caseID, location
                )
            )
            # check if case is even real, if not then create instance
            phase_case = self.get_phase_cases_by_ids([caseID])
            if len(phase_case) == 0:
                result = self.create_phase_case(caseID, verification)
                if len(result) == 0:
                    raise Exception(
                        "A phase case creation for caseID '{}' was attempted but failed!".format(
                            caseID
                        )
                    )

            # update location
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_case_location, (location, caseID))

                    if len(sql.table) != 0:  # didn't receive a response
                        self.LOG.info("update_location: END")
                        self.log_case(
                            caseID,
                            "Location Updated!",
                            "Location Updated to '{}'".format(location),
                            verification,
                            LogTypes.CASE_LOCATION_UPDATED.value,
                        )
                        return location
                    else:
                        raise Exception(
                            "No results found with the update_case_location query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_location: error={}".format(e))

        self.LOG.info("update_location: END")
        return -1

    def get_phase_cases_by_ids(self, caseIDs: list) -> list:
        try:
            self.LOG.info("get_phase_cases_by_ids: caseIDs={}".format(caseIDs))

            cases = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get caseIDs with info above
                sql.execute(self.phase_case_query, (caseIDs))
                if len(sql.table) != 0:
                    cases = sql.table
                else:
                    raise Exception("No results found with the phase_case_query query!")

        except Exception as e:
            self.LOG.error("get_phase_cases_by_ids: error={}".format(e))
            self.LOG.info("get_phase_cases_by_ids: END")
            return []  # other error

        self.LOG.info("get_phase_cases_by_ids: cases={}".format(len(cases)))
        self.LOG.info("get_phase_cases_by_ids: END")
        return cases  # no error

    # logs an aligner change given a description, used in other functions if a
    # value of an aligner is updated or changed from its initial creation form
    # input: FixitID, Change, Description, Verification
    # output: 0 for success, -1 on error
    def log_case(
        self,
        caseID: str,
        change: str,
        description: str,
        verification: Verification,
        logtype: int,
    ) -> int:
        try:
            self.LOG.info(
                'log_case: caseID={} change="{}" description="{}" verification={} logtype={}'.format(
                    caseID, change, description, verification, logtype
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_case_log,
                        (
                            logtype,
                            change,
                            description,
                            verification.get_verification(),
                            caseID,
                            caseID,
                            caseID,
                            caseID,
                            caseID,
                            caseID,
                        ),
                    )

                    if len(sql.table) != 0:
                        self.LOG.info("log_case: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the insert_case_log query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_case: error={}".format(e))

        self.LOG.info("log_case: END")
        return -1

    # Remakes a Magic touch case and links the original case to the new one
    # input: verification, caseID, newCaseID, remake, remake_reason
    # output: successful_remake
    def remake_case(
        self,
        verification: Verification,
        caseID: str,
        newCaseID: str,
        remake: str,
        remake_reason: str,
        user_name: str,
    ) -> dict:
        try:
            self.LOG.info(
                "remake_case: caseID={} newCaseID={} remake={} remake_reason={}".format(
                    caseID, newCaseID, remake, remake_reason, user_name
                )
            )

            case_return = {}
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.remake_mt_case,
                        (caseID, newCaseID, remake, remake_reason, 0, user_name, 1),
                    )

                    if len(sql.table) != 0:
                        case_return["success"] = (
                            True if sql.table[0]["success"] == 0 else False
                        )
                    else:
                        raise Exception(
                            "No results found with the remake_mt_case query!"
                        )

        except Exception as e:
            self.LOG.error("remake_case: error={}".format(e))
            self.LOG.info("remake_case: END")
            return case_return  # other error

        self.LOG.info("remake_case: matches={}".format(case_return))
        self.LOG.info("remake_case: END")
        return case_return  # no error

    # Invoices a Magic touch case
    # input: verification,caseID, invoicedBy
    # output: successful_invoice
    def invoice_case(
        self, verification: Verification, caseID: str, firstName: str
    ) -> dict:
        try:
            self.LOG.info(
                "invoice_case: caseID={} firstName={}".format(caseID, firstName)
            )

            case_return = {}
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.invoice_mt_case,
                        (caseID, firstName, "Invoiced", 1, 1, None, 1),
                    )

                    if len(sql.table) != 0:
                        case_return["success"] = (
                            True if sql.table[0]["success"] == 0 else False
                        )
                    else:
                        raise Exception(
                            "No results found with the invoice_mt_case query!"
                        )

        except Exception as e:
            self.LOG.error("invoice_case: error={}".format(e))
            self.LOG.info("invoice_case: END")
            return case_return  # other error

        self.LOG.info("invoice_case: matches={}".format(case_return))
        self.LOG.info("invoice_case: END")
        return case_return  # no error

    # Un-Invoices a Magic touch case
    # input: verification, caseID, firstName, resetShipping
    # output: successful_uninvoice
    def uninvoice_case(
        self,
        verification: Verification,
        caseID: str,
        firstName: str,
        resetShipping: bool,
    ) -> dict:
        try:
            self.LOG.info(
                "un_invoice_case: caseID={} firstName={} resetShipping={}".format(
                    caseID, firstName, resetShipping
                )
            )

            case_return = {}
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.uninvoice_mt_case,
                        (caseID, firstName, resetShipping),
                    )

                    if len(sql.table) != 0:
                        case_return["success"] = (
                            True if sql.table[0]["success"] == 0 else False
                        )
                    else:
                        raise Exception(
                            "No results found with the uninvoice_mt_case query!"
                        )

        except Exception as e:
            self.LOG.error("uninvoice_case: error={}".format(e))
            self.LOG.info("uninvoice_case: END")
            return case_return  # other error

        self.LOG.info("uninvoice_case: matches={}".format(case_return))
        self.LOG.info("uninvoice_case: END")
        return case_return  # no error


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
