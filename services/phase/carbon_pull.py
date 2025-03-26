#!/usr/bin/env python3.7
import json
from pprint import pprint
import carbon3d
import ntpath
import datetime
import dateutil
from dateutil.tz import *
import datetime
import dateutil
import time
from azure.storage.fileshare import ShareClient, ContentSettings
from io import BytesIO
import os
from dotenv import load_dotenv
import requests

load_dotenv()


from .carbon_config import CarbonConfig
from .gauge_pull import Gauge
from .verification_pull import Verification
from .token_pull import Token
from .threading_return import ThreadWithReturnValue
from .sql_config import SQLConfig
from .sql_pull import SQL_Pull


class Carbon(CarbonConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        CarbonConfig.__init__(self, sql_config)
        # Create a Token object
        self.tok = Token()

        # initialize gauge
        self.gauge = Gauge()

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # Gets all Carbon Printers
    # input: verification
    # output: Printers on success, [] on error
    def get_printer_progress(self, verification: Verification) -> list:
        try:
            self.LOG.info(f"get_printer_progress: verification={verification}")

            # Initialize printer progress
            progress = []

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # Grabs the carbon api token
                token = self.tok.get_carbon_tokens(verification)
                if token == {}:
                    raise Exception("There was an error retrieving an active token!")
                else:
                    # Initial carbon config
                    config = carbon3d.Configuration(host="https://api.carbon3d.com/v1")

                    # Give token to config
                    config.access_token = token["Token"]

                    # initialize api_client
                    api_client = carbon3d.ApiClient(config)

                    # initialize Printersapi class with api_client
                    printers_api = carbon3d.PrintersApi(api_client)

                    # Grab printer api response for get_printers
                    printers_response = printers_api.get_printers(limit=50, offset=0)

                    # dictionary mapping printer ID to Phase Printer name
                    printers = self.Printers

                    # Create a list of dictionaries containing printer Phase name, current build and next build
                    for printer in vars(printers_response)["_printers"]:
                        progress.append(
                            {
                                "name": printers[vars(printer)["_serial"]],
                                "current": vars(
                                    vars(vars(printer)["_prints"])["_current"]
                                ),
                                "next": vars(vars(vars(printer)["_prints"])["_next"]),
                                "serial": vars(printer)["_serial"],
                            }
                        )
            else:
                raise Exception("Invalid employee ID!")

        except Exception as e:
            self.LOG.error("get_printer_progress: error={}".format(e))
            self.LOG.info("get_printer_progress: END")
            return progress

        self.LOG.info("get_printer_progress: progress={}".format(str(progress)))
        self.LOG.info("get_printer_progress: END")
        return progress  # no error

    # Gets Carbon Printer build associated with the buildID given, or retrieve latest builds if no buildID given
    # input: verification, buildID, offset, rows
    # output: Build(s) on success, [] on error
    def get_build(
        self,
        verification: Verification,
        offset: int | None = None,
        rows: int | None = None,
        buildID: str | None = None,
    ) -> list:
        try:
            self.LOG.info(
                f"get_build: verification={verification}, offset={offset} rows={rows} buildID={buildID}"
            )
            # initialize build object
            build = []

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                token = self.tok.get_carbon_tokens(verification)
                if token == {}:
                    raise Exception("There was an error retrieving an active token!")
                else:
                    # Initialize Carbon API for builds
                    config = carbon3d.Configuration(host="https://api.carbon3d.com/v1")
                    config.access_token = token["Token"]
                    api_client = carbon3d.ApiClient(config)
                    builds_api = carbon3d.BuildsApi(api_client)
                    build = {}

                    if buildID is not None:
                        # # Get build info for given buildID
                        build_payload = eval(str(builds_api.get_build(uuid=buildID)))[
                            "parts"
                        ]

                        for i in range(0, len(build_payload)):
                            # Grab model UUIDs from build payload
                            model_uuid = build_payload[i]["model_uuid"]
                            models_api = carbon3d.ModelsApi(api_client)
                            # Grab file names from build payload
                            filename = eval(str(models_api.get_model(model_uuid)))[
                                "filename"
                            ]

                            values = list(build_payload[i].values())
                            values.insert(0, filename)

                            # format list into dictionary
                            build[i] = tuple(
                                values
                            )  # append row i with the values from the dictionary

                    elif offset is not None and rows is not None:
                        if int(offset) > 0:
                            # Get cursor for offset value given
                            cursor = vars(builds_api.get_builds(limit=int(offset)))[
                                "_next_cursor"
                            ]

                            # Return n builds starting at cursor where n = rows
                            builds_response = vars(
                                builds_api.get_builds(limit=int(rows), cursor=cursor)
                            )

                        else:
                            # Return n builds where n = rows
                            builds_response = vars(
                                builds_api.get_builds(limit=int(rows))
                            )

                        for _build in builds_response["_builds"]:
                            build.append(vars(_build))

                    else:
                        raise Exception(
                            "Value must be given for buildID OR values must be given for offset and rows"
                        )

        except Exception as e:
            self.LOG.error("get_build: error={}".format(e))
            self.LOG.info("get_build: END")
            return build

        self.LOG.info("get_build: progress={}".format(str(build)))
        self.LOG.info("get_build: END")
        return build  # no error

    # Gets Carbon Printer queues
    # input: verification
    # output: Queues on success, [] on error
    def get_printer_queues(self, verification: Verification) -> list:
        try:
            self.LOG.info(f"get_printer_queues: verification={verification}")

            queues = []

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                token = self.tok.get_carbon_tokens(verification)
                if token == {}:
                    raise Exception("There was an error retrieving an active token!")
                else:
                    # Initialize Carbon API for queues
                    config = carbon3d.Configuration(host="https://api.carbon3d.com/v1")
                    config.access_token = token["Token"]
                    api_client = carbon3d.ApiClient(config)
                    queues_api = carbon3d.QueuesApi(api_client)
                    queues_response = vars(queues_api.get_printer_queues())

                    # Append each queue to queues array
                    for queue in queues_response["_printer_queues"]:
                        queues.append(vars(queue))
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("get_printer_queues: error={}".format(e))
            self.LOG.info("get_printer_queues: END")
            return queues

        self.LOG.info("get_printer_queues: queues={}".format(len(queues)))
        self.LOG.info("get_printer_queues: END")
        return queues  # no error

    # Gets Carbon Printer Print information associated with the given printUUIDs
    # input: verification, printsInfo {printIDs : [], serial : int}
    # output: Prints on success, {} on error
    def get_prints_by_ids(self, verification: Verification, printsInfo: dict) -> dict:
        try:
            self.LOG.info(f"get_prints_by_ids: verification={verification}")

            # initialize print object
            prints = {"name": "", "prints": []}

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # dictionary mapping printer ID to Phase Printer name
                printers = self.Printers

                token = self.tok.get_carbon_tokens(verification)
                if token == {}:
                    raise Exception("There was an error retrieving an active token!")
                else:
                    # Initialize Carbon API for prints
                    config = carbon3d.Configuration(host="https://api.carbon3d.com/v1")
                    config.access_token = token["Token"]
                    api_client = carbon3d.ApiClient(config)
                    prints_api = carbon3d.PrintsApi(api_client)

                    # Get prints by printIDs given
                    prints_response = vars(
                        prints_api.get_prints(
                            limit=100,
                            uuid=printsInfo["printIDs"],
                            status=["queued", "printing", "finished"],
                        )
                    )

                    for print in prints_response["_prints"]:
                        prints["prints"].append(vars(print))

                    # Check if printer serial is a part of Phase, if so assign printer name else assign Derby
                    if printsInfo["serial"] in printers:
                        prints["name"] = printers[printsInfo["serial"]]
                    else:
                        prints["name"] = "Derby"
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("get_prints_by_ids: error={}".format(e))
            self.LOG.info("get_prints_by_ids: END")
            return {}

        self.LOG.info("get_prints_by_ids: queues={}".format(len(prints)))
        self.LOG.info("get_prints_by_id: END")
        return prints  # no error

    # Gets Carbon Printer Print information
    # input: verification
    # output: Prints on success, [] on error
    def get_prints(self, verification: Verification) -> list:
        try:
            self.LOG.info(f"get_prints: verification={verification}")

            prints = []

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                token = self.tok.get_carbon_tokens(verification)
                if token == {}:
                    raise Exception("There was an error retrieving an active token!")
                else:
                    # Initialize Carbon API for prints
                    config = carbon3d.Configuration(host="https://api.carbon3d.com/v1")
                    config.access_token = token["Token"]
                    api_client = carbon3d.ApiClient(config)
                    prints_api = carbon3d.PrintsApi(api_client)

                    # Get most recent 100 prints
                    prints_response = vars(
                        prints_api.get_prints(
                            limit=100,
                        )
                    )
                    for print in prints_response["_prints"]:
                        prints.append(vars(print))
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("get_prints: error={}".format(e))
            self.LOG.info("get_prints: END")
            return []

        self.LOG.info("get_prints: queues={}".format(len(prints)))
        self.LOG.info("get_prints: END")
        return prints  # no error

    # Gets Carbon Printer Part information
    # input: verification, offset, rows
    # output: Parts on success, [] on error
    def get_parts(self, verification: Verification, offset: int, rows: int) -> list:
        try:
            self.LOG.info(
                f"get_parts: verification={verification} offset={offset} rows={rows}"
            )

            parts = []

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                token = self.tok.get_carbon_tokens(verification)
                if token == {}:
                    raise Exception("There was an error retrieving an active token!")
                else:
                    # Initialize Carbon API for parts
                    config = carbon3d.Configuration(host="https://api.carbon3d.com/v1")
                    config.access_token = token["Token"]
                    api_client = carbon3d.ApiClient(config)
                    parts_api = carbon3d.PartsApi(api_client)

                    if offset > 0:
                        # Get cursor for offset value given
                        cursor = vars(parts_api.get_parts(limit=offset))["_next_cursor"]

                        # Return n parts starting at cursor where n = rows
                        parts_response = vars(
                            parts_api.get_parts(limit=rows, cursor=cursor)
                        )

                    else:
                        # Return n parts n = rows
                        parts_response = vars(parts_api.get_parts(limit=rows))

                    # Return n parts starting at cursor where n = rows
                    for part in parts_response["_parts"]:
                        parts.append(vars(part))

            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("get_parts: error={}".format(e))
            self.LOG.info("get_parts: END")
            return []

        self.LOG.info("get_parts: queues={}".format(len(parts)))
        self.LOG.info("get_parts: END")
        return parts  # no error

    # Creates Carbon Printer Part
    # input: verification
    # output: Parts on success, [] on error
    def create_parts(
        self,
        aligners: list,
        carbon_token: dict,
        gaugeID: int | None = None,
        gaugeIndex: int | None = None,
    ) -> list:
        try:
            self.LOG.info(f"create_parts: aligners={len(aligners)}")

            # Initialize Carbon API for parts
            config = carbon3d.Configuration(host="https://api.carbon3d.com/v1")
            config.access_token = carbon_token["Token"]
            api_client = carbon3d.ApiClient(config)
            parts_api = carbon3d.PartsApi(api_client)

            for aligner in aligners:

                # Create part request for each aligner
                part_request = carbon3d.PartRequest(
                    part_number="ALIGNER-001",
                    model_uuid=aligner["ModelUUID"],
                    application_uuid=os.getenv("CARBON_APPLICATION_UUID"),
                )

                api_response = parts_api.create_part(part_request=part_request)

                aligner["PartUUID"] = vars(api_response)["_uuid"]

                gaugeIndex += 1
                self.gauge.update_gauge(
                    gaugeID,
                    self.LOG,
                    "carbon_aligners",
                    index=gaugeIndex,
                    limit=100,
                    constant=0,
                    label="Creating Part for {}".format(aligner["AlignerID"]),
                )

        except Exception as e:
            self.LOG.error("create_parts: error={}".format(e))
            self.LOG.info("create_parts: END")
            return [], -1

        self.LOG.info("create_parts: queues={}".format(len(aligners)))
        self.LOG.info("create_parts: END")
        return aligners, gaugeIndex  # no error

    # Gets Carbon Printer Part information
    # input: verification
    # output: Parts on success, [] on error
    def get_printed_parts(
        self,
        verification: Verification,
        offset: int | None = None,
        rows: int | None = None,
        printedPartIDs: list = [],
    ) -> list:
        try:
            self.LOG.info(
                f"get_printed_parts: verification={verification} offset={offset} rows={rows} printedPartIDs={len(printedPartIDs)}"
            )

            printed_parts = []

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                token = self.tok.get_carbon_tokens(verification)
                if token == {}:
                    raise Exception("There was an error retrieving an active token!")
                else:
                    # Initialize Carbon API for printed_parts
                    config = carbon3d.Configuration(host="https://api.carbon3d.com/v1")
                    config.access_token = token["Token"]
                    api_client = carbon3d.ApiClient(config)
                    printed_parts_api = carbon3d.PrintedPartsApi(api_client)

                    # Get most recent 200 printed parts if no printedPartIDs given, else get printed parts based on printedPartIDs given
                    if len(printedPartIDs) == 0:
                        if offset > 0:
                            # Get cursor for offset value given
                            cursor = vars(
                                printed_parts_api.get_printed_parts(limit=offset)
                            )["_next_cursor"]

                            # Return n parts starting at cursor where n = rows
                            printed_parts_response = vars(
                                printed_parts_api.get_printed_parts(
                                    limit=rows, cursor=cursor
                                )
                            )
                        else:
                            # Return n parts where n = rows
                            printed_parts_response = vars(
                                printed_parts_api.get_printed_parts(limit=rows)
                            )

                        for part in printed_parts_response["_parts"]:
                            printed_parts.append(vars(part))

                    else:
                        printed_parts_response = vars(
                            printed_parts_api.get_printed_parts(
                                limit=200, uuid=printedPartIDs
                            )
                        )
                        for part in printed_parts_response["_parts"]:
                            printed_parts.append(vars(part))

            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("get_printed_parts: error={}".format(e))
            self.LOG.info("get_printed_parts: END")
            return []

        self.LOG.info("get_printed_parts: queues={}".format(len(printed_parts)))
        self.LOG.info("get_printed_parts: END")
        return printed_parts  # no error

    # Uploads a model using the STL linked to each aligner
    # input: [Aligners], token
    # output: Parts on success, [] on error
    def upload_models(
        self,
        aligners: list,
        carbon_token: dict,
        azure_token: dict,
        gaugeID: int | None = None,
        gaugeIndex: int = 0,
    ) -> tuple:
        try:
            self.LOG.info(
                f"upload_models: aligners={len(aligners)} carbon_token={carbon_token} azure_token={azure_token}"
            )

            # define new aligners object
            new_aligners = []

            # Initialize Carbon API for models
            config = carbon3d.Configuration(host="https://api.carbon3d.com/v1")
            config.access_token = carbon_token["Token"]
            api_client = carbon3d.ApiClient(config)
            models_api = carbon3d.ModelsApi(api_client)

            # Connect to prod-phasestorage
            share = ShareClient(
                account_url="https://phasestorage.file.core.windows.net/",
                credential=azure_token["Token"],
                share_name="prod-phasestorage",
            )

            threads = []
            for aligner in aligners:
                # upload model in thread
                thread = ThreadWithReturnValue(
                    target=Carbon.upload_model,
                    args=(self, share, aligner["Path"], models_api),
                )
                thread.handled = False
                thread.aligner = aligner
                threads.append(thread)
                thread.start()
                self.LOG.info("THREAD CREATED")

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
                    if len(result) == 0:
                        raise Exception(
                            "Carbon upload failed for Aligner {}!".format(
                                thread.aligner["AlignerID"]
                            )
                        )
                    thread.aligner["ModelUUID"] = result["ModelUUID"]
                    thread.aligner["Filename"] = result["Filename"]

                    # append result to new aligners
                    new_aligners.append(thread.aligner)

                    # update gauge index
                    gaugeIndex += 1
                    self.gauge.update_gauge(
                        gaugeID,
                        self.LOG,
                        "carbon_aligners",
                        index=gaugeIndex,
                        limit=100,
                        constant=0,
                        label="Uploading Model for {}".format(
                            thread.aligner["AlignerID"]
                        ),
                    )

        except Exception as e:
            self.LOG.error("upload_models: error={}".format(e))
            self.LOG.info("upload_models: END")
            return [], -1

        self.LOG.info("upload_models: queues={}".format(len(new_aligners)))
        self.LOG.info("upload_models: END")
        return new_aligners, gaugeIndex  # no error

    def upload_model(
        self, client: ShareClient, path: str, models_api: carbon3d.ModelsApi
    ) -> tuple:
        try:
            self.LOG.info(
                f"upload_model: client={client} path={path} models_api={models_api}"
            )
            result = {}

            filename = ntpath.basename(path)

            # Truncates path, keeping everything after \prod-phasestorage\\
            truncated_path = path.split("prod-phasestorage\\")[1]

            # Init file client
            my_file = client.get_file_client(truncated_path)

            # Download file into StorageStream, create Byte stream, read downloaded storage stream into byte stream
            downloaded_stream = my_file.download_file()
            stream = BytesIO()
            downloaded_stream.readinto(stream)

            # Upload models to carbon API using byte stream as body
            models_response = models_api.upload_model(
                filename,
                application_uuid=os.getenv("CARBON_APPLICATION_UUID"),
                body=stream.getvalue(),
            )
            # Assign return values to aligners
            result = {
                "ModelUUID": vars(models_response)["_uuid"],
                "Filename": vars(models_response)["_filename"],
            }

        except Exception as e:
            self.LOG.error("upload_model: error={}".format(e))
            self.LOG.info("upload_model: END")
            return {}

        self.LOG.info(
            "upload_model: uuid={} filename={}".format(
                result["ModelUUID"], result["Filename"]
            )
        )
        self.LOG.info("upload_model: END")
        return result

    # Gets Carbon Printer Model information
    # input: verification
    # output: Models on success, [] on error
    def get_models(self, verification: Verification, modelUUIDs: list) -> list:
        try:
            self.LOG.info(f"get_models: verification={verification}")

            models = []

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                token = self.tok.get_carbon_tokens(verification)
                if token == {}:
                    raise Exception("There was an error retrieving an active token!")
                else:
                    # Initialize Model api for carbon
                    config = carbon3d.Configuration(host="https://api.carbon3d.com/v1")
                    config.access_token = token["Token"]
                    api_client = carbon3d.ApiClient(config)
                    models_api = carbon3d.ModelsApi(api_client)
                    # Convert all models in model response to dicts and add them to models
                    for modelUUID in modelUUIDs:
                        models_response = models_api.get_model(uuid=modelUUID)
                        models.append(vars(models_response))

            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("get_models: error={}".format(e))
            self.LOG.info("get_models: END")
            return []

        self.LOG.info("get_models: queues={}".format(len(models)))
        self.LOG.info("get_models: END")
        return models  # no error

    # Creates Carbon Printer Part Order
    # input: [aligners], {token: token}, flush
    # output: Part Orders on success, [] on error
    def create_part_order(
        self,
        aligners: list,
        token: dict,
        flush: bool = False,
        gaugeID: int | None = None,
        gaugeIndex: int | None = None,
    ) -> list:
        try:
            self.LOG.info(f"create_part_order: aligners={len(aligners)} flush={flush}")

            parts = []

            # Format due date
            due_date = datetime.datetime.now() + datetime.timedelta(days=0)
            formatted_due_date = due_date.astimezone(dateutil.tz.UTC).replace(
                microsecond=0
            )

            # Initialize Order api for carbon
            config = carbon3d.Configuration(host="https://api.carbon3d.com/v1")
            config.access_token = token["Token"]
            api_client = carbon3d.ApiClient(config)
            orders_api = carbon3d.PartOrdersApi(api_client)

            part_order_request_parts = []

            for aligner in aligners:
                # Generate list of all parts
                part_order_request_parts.append(
                    carbon3d.PartOrderRequestParts(aligner["PartUUID"])
                )

            # Create part order Request
            part_order_request = carbon3d.PartOrderRequest(
                part_order_number=os.getenv("CARBON_PART_ORDER_NUMBER"),
                parts=part_order_request_parts,
                due_date=formatted_due_date,
                flush=flush,
                build_sop_uuid=os.getenv("CARBON_BUILD_SOP_UUID"),
            )

            gaugeIndex += len(aligners)
            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "carbon_aligners",
                index=gaugeIndex,
                limit=100,
                constant=0,
                label="Creating Build",
            )

            # Create part order passing part order request
            api_response = orders_api.create_part_order(
                part_order_request=part_order_request
            )

            # Update aligners with applicable returned information
            for aligner in aligners:
                aligner["ApplicationID"] = vars(api_response)["_application_uuid"]
                aligner["PartOrderNumber"] = vars(api_response)["_part_order_number"]
                aligner["OrderUUID"] = vars(api_response)["_uuid"]
                for printed_part in vars(api_response)["_printed_parts"]:
                    if aligner["PartUUID"] == vars(printed_part)["_part_uuid"]:
                        aligner["PrintedPartUUID"] = vars(printed_part)["_uuid"]

        except Exception as e:
            self.LOG.error("create_part_order: error={}".format(e))
            self.LOG.info("create_part_order: END")
            return [], -1

        self.LOG.info(
            "create_part_order: queues={}".format(len(part_order_request_parts))
        )
        self.LOG.info("create_part_order: END")
        return aligners, gaugeIndex  # no error

    # Creates a carbon build
    # input: EmployeeID, [Aligners], flush, gaugeID, gaugeIndex
    # output: Parts on success, [] on error
    # SAMPLE INPUT:
    # "aligners": [
    # {
    #     "AlignerID": 284708,
    #     "ID": 12718655,
    #     "FileID": 3,
    #     "Path": "\\\\phasestorage.file.core.windows.net\\prod-phasestorage\\RemoteMain\\ALIGNERS\\Completed-Files\\58021\\58021L07-284708.stl",
    #     "Created": "2022-10-24 13:16:32.600000",
    #     "CreatedBy": "rhino",
    #     "Status": 11
    # }
    def create_build(
        self,
        verification: Verification,
        aligners: list,
        flush: bool,
        gaugeID: int | None = None,
        gaugeIndex: int | None = None,
    ) -> list:
        try:
            self.LOG.info(
                f"create_build: verification={verification}, aligners={aligners}"
            )

            # Get carbon token
            carbon_token = self.tok.get_carbon_tokens(verification)

            # Get Azure Token
            azure_token = self.tok.get_azure_fileshare_token(verification)

            if carbon_token == {}:
                raise Exception("There was an error retrieving an active carbon token!")
            if azure_token == {}:
                raise Exception("There was an error retrieving an active azure token!")

            # Upload models
            aligners, gaugeIndex = self.upload_models(
                aligners, carbon_token, azure_token, gaugeID, gaugeIndex
            )

            # Create Parts
            aligners, gaugeIndex = self.create_parts(
                aligners, carbon_token, gaugeID, gaugeIndex
            )

            # Create Orders
            aligners, gaugeIndex = self.create_part_order(
                aligners, carbon_token, flush, gaugeID, gaugeIndex
            )

        except Exception as e:
            self.LOG.error("create_build: error={}".format(e))
            self.LOG.info("create_build: END")
            return [], -1

        self.LOG.info("create_build: aligners={}".format(len(aligners)))
        self.LOG.info("create_build: END")
        return aligners, gaugeIndex  # no error

    # Gets Carbon Printer Build Attachment
    # input: uuid
    # output: Attachment on success, "" on error
    def get_attachment(self, verification: Verification, attachmentUUID: str) -> str:
        try:
            self.LOG.info(
                f"get_attachment: verification={verification} attachmentUUID={attachmentUUID}"
            )

            attachment_path = ""

            # Get Carbon Token
            carbon_token = self.tok.get_carbon_tokens(verification)
            # Get Azure Token
            azure_token = self.tok.get_azure_fileshare_token(verification)

            if carbon_token == {}:
                raise Exception("There was an error retrieving an active carbon token!")
            if azure_token == {}:
                raise Exception("There was an error retrieving an active azure token!")

            else:
                # Initialize Attachment api for carbon
                config = carbon3d.Configuration(host="https://api.carbon3d.com/v1")
                config.access_token = carbon_token["Token"]
                api_client = carbon3d.ApiClient(config)
                attachments_api = carbon3d.AttachmentsApi(api_client)
                # Get attachment associated with UUID given
                attachment_path = attachments_api.get_attachment(uuid=attachmentUUID)
                # Connect to prod-phasestorage shareClient
                share = ShareClient(
                    account_url="https://phasestorage.file.core.windows.net/",
                    credential=azure_token["Token"],
                    share_name="prod-phasestorage",
                )

                # Generate a unique file name for traveler in share client
                new_file_name = "traveler" + attachmentUUID + ".pdf"

                # Create the traveler file client
                traveler_file = share.get_file_client(
                    f"RemoteMain/ALIGNERS/Carbon/{new_file_name}"
                )

                # Create content_settings for the file so the pdf is displayed instead of downloaded
                content_settings = ContentSettings(
                    content_type="application/pdf",
                    cache_control="no-cache, no-store, must-revalidate",
                )

                # Read the carbon traveler pdf and upload it
                with open(attachment_path, "rb") as data:
                    traveler_file.upload_file(data, content_settings=content_settings)

                # Delete locally saved pdf
                os.remove(attachment_path)

                # Update the attachment_path with filepath in azure
                attachment_path = f"https://phasestorage.file.core.windows.net/prod-phasestorage/RemoteMain/Aligners/Carbon/{new_file_name}?{azure_token['Token']}"

        except Exception as e:
            self.LOG.error("get_attachment: error={}".format(e))
            self.LOG.info("get_attachment: END")
            return attachment_path

        self.LOG.info("get_attachment: queues={}".format(len(attachment_path)))
        self.LOG.info("get_attachment: END")
        return attachment_path  # no error

    # Gets Carbon Printer Build information by the platform_serial
    # input: verification, platform_serial
    # output: build on success, {} on error
    def get_build_by_platform(
        self, verification: Verification, platform_serial: str
    ) -> dict:
        try:
            self.LOG.info(
                f"get_build_by_platform: verification={verification} platform_serial={platform_serial}"
            )

            build = []

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                token = self.tok.get_carbon_tokens(verification)
                if token == {}:
                    raise Exception("There was an error retrieving an active token!")
                else:
                    # Initialize Carbon API for prints and builds
                    config = carbon3d.Configuration(host="https://api.carbon3d.com/v1")
                    config.access_token = token["Token"]
                    api_client = carbon3d.ApiClient(config)
                    prints_api = carbon3d.PrintsApi(api_client)
                    prints_orders_api = carbon3d.PrintOrdersApi(api_client)
                    builds_api = carbon3d.BuildsApi(api_client)

                    # Retrieve most recent print for platform_serial
                    prints_response = vars(
                        vars(
                            prints_api.get_prints(
                                platform_serial=[platform_serial],
                                limit=1,
                                sort=["finished_at,desc"],
                            )
                        )["_prints"][0]
                    )["_print_order_uuid"]

                    # Retrieve print order for given print
                    prints_order_response = vars(
                        prints_orders_api.get_print_order(uuid=prints_response)
                    )

                    if len(prints_order_response["_build_uuid"]) == 0:
                        raise Exception(
                            f"No buildUUID assigned to Plate {platform_serial}"
                        )

                    # Retreive build information for recent print order
                    build = vars(
                        builds_api.get_build(uuid=prints_order_response["_build_uuid"])
                    )

            else:
                raise Exception("Invalid validation!")

        except Exception as e:
            self.LOG.error("get_build_by_platform: error={}".format(e))
            self.LOG.info("get_build_by_platform: END")
            return build

        self.LOG.info("get_build_by_platform: prints={}".format(str(build)))
        self.LOG.info("get_build_by_platform: END")
        return build  # no error

    # Gets Carbon Plate History
    # input: plate_qty
    # output: [plates] on success, [] on error
    def get_history_of_carbon_plates(self, plate_qty: int) -> list:
        try:
            self.LOG.info(f"get_history_of_carbon_plates: plate_qty={plate_qty}")

            plates = []

            with SQL_Pull()(self.sql_config)() as sql:
                # get plate history
                sql.execute(self.get_carbon_plate_history, (plate_qty))
                # check table
                if len(sql.table) != 0:
                    plates = sql.table
                else:
                    raise Exception(
                        "No results found with the get_carbon_plate_history query!"
                    )

        except Exception as e:
            self.LOG.error("get_history_of_carbon_plates: error={}".format(e))
            self.LOG.info("get_history_of_carbon_plates: END")
            return plates  # other error

        self.LOG.info("get_history_of_carbon_plates: plate_logs={}".format(len(plates)))
        self.LOG.info("get_history_of_carbon_plates: END")
        return plates  # no error

    # Create Carbon Plate Log
    # input: carbon_plate, carbon_plate
    # output: CarbonPlateLogID on success, -1 on error
    def create_carbon_plate_log(
        self, carbon_plate: str, verification: Verification
    ) -> int:
        try:
            self.LOG.info(
                f"create_carbon_plate_log: carbon_plate={carbon_plate} CreatedBy={verification}"
            )

            plate_log_id = -1

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # insert plate log
                    sql.execute(
                        self.create_carbon_plate_history,
                        (carbon_plate, verification.get_verification()),
                    )
                    # check table
                    if len(sql.table) != 0:
                        plate_log_id = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "No results found with the create_carbon_plate_history query!"
                        )
            else:
                raise Exception("Invalid validation!")

        except Exception as e:
            self.LOG.error("create_carbon_plate_log: error={}".format(e))
            self.LOG.info("create_carbon_plate_logget_history_of_carbon_plates: END")
            return plate_log_id  # other error

        self.LOG.info("create_carbon_plate_log: PlateLogID={}".format(plate_log_id))
        self.LOG.info("create_carbon_plate_log: END")
        return plate_log_id  # no error

    # Generates Carbon Printer Usage Stats Report
    # input: startdate, enddate (YYYY/MM/DD format)
    # output: file on success, dict on error
    def generate_carbon_report(self, startdate: str, enddate: str) -> dict:
        try:
            self.LOG.info(
                f"generate_carbon_report: startdate={startdate} enddate={enddate}"
            )

            results = {}
            url = "https://phaseortho.print.carbon3d.com/prints/_search"

            payload = json.dumps(
                {
                    "query": {
                        "bool": {
                            "must": [
                                {
                                    "range": {
                                        "started_at": {
                                            "gt": startdate,
                                            "lte": enddate,
                                        }
                                    }
                                },
                                {"term": {"status": "finished"}},
                            ]
                        }
                    },
                    "size": 0,
                    "aggs": {
                        "count": {"value_count": {"field": "part_volume_ml"}},
                        "averageVolumeMl": {"avg": {"field": "part_volume_ml"}},
                        "printTimeSec": {"sum": {"field": "print_duration_s"}},
                        "volumeMl": {"sum": {"field": "part_volume_ml"}},
                        "topResins": {"terms": {"field": "resin_name", "size": 5}},
                        "timebucket": {
                            "date_histogram": {
                                "field": "started_at",
                                "fixed_interval": "1d",
                                "time_zone": "-05:00",
                            },
                            "aggs": {
                                "printerCount": {
                                    "cardinality": {
                                        "field": "printer_id",
                                        "precision_threshold": 40000,
                                    }
                                },
                                "partCount": {
                                    "sum": {
                                        "script": {
                                            "source": "params['_source']['parts'].size()"
                                        }
                                    }
                                },
                                "printTimeSec": {"sum": {"field": "print_duration_s"}},
                                "volumeMl": {"sum": {"field": "part_volume_ml"}},
                                "averageTimeMin": {
                                    "avg": {"field": "print_duration_s"}
                                },
                                "averageVolumeMl": {"avg": {"field": "part_volume_ml"}},
                                "averageVolumeMlPerPart": {
                                    "avg": {
                                        "script": {
                                            "source": "doc['part_volume_ml'].getValue() / Integer.max(params['_source']['parts'].size(), 1)"
                                        }
                                    }
                                },
                                "resin": {
                                    "terms": {"field": "resin_name", "size": 1000},
                                    "aggs": {
                                        "partCount": {
                                            "sum": {
                                                "script": {
                                                    "source": "params['_source']['parts'].size()"
                                                }
                                            }
                                        },
                                        "printTimeSec": {
                                            "sum": {"field": "print_duration_s"}
                                        },
                                        "volumeMl": {
                                            "sum": {"field": "part_volume_ml"}
                                        },
                                    },
                                },
                            },
                        },
                    },
                }
            )
            headers = {
                "Cookie": "user.id=eyJfcmFpbHMiOnsibWVzc2FnZSI6Ik1qZ3pOQT09IiwiZXhwIjpudWxsLCJwdXIiOiJjb29raWUudXNlci5pZCJ9fQ%3D%3D--d8121a690c69b198137416ab899295e3b666eb69; subdomain=phaseortho; _carbon3d_session=3c52dc46f1be21046d0e6023485a4d2d; _csrf_token=oXNLLmarixmHXWLcKS2ikX_8E8jeoA0hq71rzMBoE9c; user.expires_at=eyJfcmFpbHMiOnsibWVzc2FnZSI6IklqSXdNalF0TVRJdE1UWlVNRGs2TWpFNk5EZ3VORFkxTFRBNE9qQXdJZz09IiwiZXhwIjpudWxsLCJwdXIiOiJjb29raWUudXNlci5leHBpcmVzX2F0In19--20396684baefac28f6d4e459f3a1977bbb36a102; subdomain=phaseortho; _carbon3d_session=3c52dc46f1be21046d0e6023485a4d2d; _csrf_token=oXNLLmarixmHXWLcKS2ikX_8E8jeoA0hq71rzMBoE9c; user.expires_at=eyJfcmFpbHMiOnsibWVzc2FnZSI6IklqSXdNalF0TVRJdE1UWlVNVFE2TVRnNk1qVXVNREU1TFRBNE9qQXdJZz09IiwiZXhwIjpudWxsLCJwdXIiOiJjb29raWUudXNlci5leHBpcmVzX2F0In19--06f7814cd67d10593811bcdbd6a3b6af025a9082",
                "Origin": "https://phaseortho.print.carbon3d.com",
                "Content-Type": "application/json",
            }

            response = requests.request("POST", url, headers=headers, data=payload)

        except Exception as e:
            self.LOG.error("generate_carbon_report: error={}".format(e))
            self.LOG.info("generate_carbon_report: END")
            return response  # other error

        self.LOG.info("generate_carbon_report: carbon_report={}".format("generated"))
        self.LOG.info("generate_carbon_report: END")
        return response.json()  # no error


# Unit Testing
def main():
    return


if __name__ == "__main__":
    main()
