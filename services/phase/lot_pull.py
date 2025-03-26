#!/usr/bin/env python3.7

import datetime
from typing import List, Dict

from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .lot_config import LotConfig
from .verification_pull import Verification
from .gauge_pull import Gauge
from .lot_config import LotConfig
from .constants import LogTypes, Statuses


class Lot(LotConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        LotConfig.__init__(self, sql_config)

        # initialize gauge
        self.gauge = Gauge()

        # get locations and status
        result = []
        with SQL_Pull()(self.sql_config)() as sql:
            result, _ = sql.execute(self.get_status)
            for stat in result:
                self.statuses[stat["ID"]] = stat["StatusType"]
            result, _ = sql.execute(self.get_log_types)
            for log_type in result:
                self.log_types[log_type["ID"]] = log_type["LogType"]
            result, _ = sql.execute(self.get_materials)
            for loc in result:
                self.materials[loc["MaterialID"]] = loc["Type"]

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # gets materials
    def get_all_materials(self) -> list:
        try:
            self.LOG.info("get_all_materials: BEGIN")

            materials = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_materials)
                if len(sql.table) > 0:
                    materials = sql.table
                else:
                    raise Exception("No results found with the get_materials query!")

        except Exception as e:
            self.LOG.error("get_all_materials: error={}".format(e))
            self.LOG.info("get_all_materials: END")
            return []

        self.LOG.info("get_all_materials: materials={}".format(materials))
        self.LOG.info("get_all_materials: END")
        return materials

    # Creates a material
    def create_material(
        self, verification, brandID, material_type, description, sku
    ) -> dict:
        try:
            self.LOG.info(
                f"create_material: verification={verification} brandID={brandID} material_type={material_type} description={description} sku={sku}"
            )

            materialID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_material,
                        (
                            brandID,
                            material_type,
                            description,
                            sku,
                            verification.get_verification(),
                        ),
                    )
                    if len(sql.table) > 0:
                        materialID = sql.table[0]
                    else:
                        raise Exception(
                            "No results found with the insert_material query!"
                        )
                else:
                    raise Exception("Invalid employee ID!")

        except Exception as e:
            self.LOG.error("create_material: error={}".format(e))
            self.LOG.info("create_material: END")
            return materialID

        self.LOG.info("create_material: materials={}".format(materialID))
        self.LOG.info("create_material: END")
        return materialID

    # Sag test involves scanning a plastic sheet with a given density checker
    # camera. Results include the spot coverage in relation to the area of the
    # camera's range, spot average in relation to the average size of spots,
    # spot count in relation to the area of the camera's range. The therm
    # profile, is the profile used on the thermoformer for testing purposes.
    # This version of the test will create a yield and perform a yield SAG test.
    def create_plastic_sag_test(
        self,
        verification: Verification,
        plasticID: int,
        spot_coverage: int,
        spot_average: int,
        spot_count: int,
        therm_code: int,
        test_diameter: int,
        type_status: int,
        sheet_length_ft: float = 0.4583,
        machineID: int = -1,
    ) -> int:
        try:
            self.LOG.info(
                "create_plastic_sag_test: verification={} plasticID={} spot_coverage={} spot_average={} spot_count={} therm_code={} test_diameter={} sheet_length_ft={} type_status={}".format(
                    verification,
                    plasticID,
                    spot_coverage,
                    spot_average,
                    spot_count,
                    therm_code,
                    test_diameter,
                    sheet_length_ft,
                    type_status,
                )
            )

            # create yield to perform sag test
            entry = -1
            # 10 is the testing status
            yieldID = self.create_yield(plasticID, verification, sheet_length_ft, 1, 10)
            if yieldID != -1:
                entry = self.create_yield_sag_test(
                    verification,
                    yieldID,
                    spot_coverage,
                    spot_average,
                    spot_count,
                    therm_code,
                    test_diameter,
                    type_status,
                    machineID,
                )
                if entry < 0:
                    raise Exception(
                        "No results found creating the sag test for the given plastic {}!".format(
                            plasticID
                        )
                    )
            else:
                raise Exception("Yield creation for sag test failed!")

        except Exception as e:
            self.LOG.error("create_plastic_sag_test: error={}".format(e))
            self.LOG.info("create_plastic_sag_test: END")
            return -1

        self.LOG.info("create_plastic_sag_test: entry={}".format(entry))
        self.LOG.info("create_plastic_sag_test: END")
        return entry

    # gets all sags for a particular plastic
    def get_sag_by_plastic(self, plasticID: int) -> list:
        try:
            self.LOG.info("get_sag_by_plastic: plasticID={}".format(plasticID))

            sags = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_plastic_sag_by_plastic, (plasticID))
                if len(sql.table) > 0:
                    sags = sql.table
                else:
                    raise Exception(
                        "No results found with the get_plastic_sag_by_plastic query!"
                    )

        except Exception as e:
            self.LOG.error("get_sag_by_plastic: error={}".format(e))
            self.LOG.info("get_sag_by_plastic: END")
            return []

        self.LOG.info("get_sag_by_plastic: sags={}".format(sags))
        self.LOG.info("get_sag_by_plastic: END")
        return sags

    # gets plastics
    def get_plastics(self, statuses: list) -> list:
        try:
            self.LOG.info(f"get_plastics: {statuses}")

            plastics = []
            with SQL_Pull()(self.sql_config)() as sql:
                if statuses is not None:
                    filter_valid_status = ",".join(
                        map(lambda status: str(status), (statuses))
                    )
                    sql.execute(self.get_plastics_by_status, (filter_valid_status,))
                else:
                    sql.execute(self.get_all_plastics)
                if len(sql.table) > 0:
                    plastics = sql.table
                else:
                    raise Exception("No results found with the get_all_plastics query!")

        except Exception as e:
            self.LOG.error("get_plastics: error={}".format(e))
            self.LOG.info("get_plastics: END")
            return []

        self.LOG.info("get_plastics: plastics={}".format(plastics))
        self.LOG.info("get_plastics: END")
        return plastics

    def get_plastics_by_batch(self, batchID: int) -> list:
        try:
            self.LOG.info("get_plastics_by_batch: batchID={}".format(batchID))

            plastics = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_plastics_by_batch, (batchID))
                if len(sql.table) > 0:
                    plastics = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_plastics_by_batch query!"
                    )

        except Exception as e:
            self.LOG.error("get_plastics_by_batch: error={}".format(e))
            self.LOG.info("get_plastics_by_batch: END")
            return []

        self.LOG.info("get_plastics_by_batch: plastics={}".format(plastics))
        self.LOG.info("get_plastics_by_batch: END")
        return plastics

    # get plastic by given id
    def get_plastics_by_id(self, plasticID: int) -> list:
        try:
            self.LOG.info("get_plastics_by_id: plasticID={}".format(plasticID))

            plastics = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_plastics_by_ID, (plasticID, str(plasticID)))
                if len(sql.table) > 0:
                    plastics = sql.table
                else:
                    raise Exception(
                        "No results found with the get_plastics_by_ID query!"
                    )

        except Exception as e:
            self.LOG.error("get_plastics_by_id: error={}".format(e))
            self.LOG.info("get_plastics_by_id: END")
            return []

        self.LOG.info("get_plastics_by_id: plastics={}".format(plastics))
        self.LOG.info("get_plastics_by_id: END")
        return plastics

    # log a change for a plastic
    def log_plastic(
        self,
        plasticID: int,
        change: str,
        description: str,
        verification: Verification,
        logtype: int,
    ) -> int:
        try:
            self.LOG.info(
                'log_plastic: plasticID={} change="{}" description="{}" verification={} logtype={}'.format(
                    plasticID, change, description, verification, logtype
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_plastic_log,
                        (
                            plasticID,
                            logtype,
                            change,
                            description,
                            verification.get_verification(),
                            plasticID,
                            plasticID,
                            plasticID,
                            plasticID,
                            plasticID,
                            plasticID,
                            plasticID,
                            plasticID,
                            plasticID,
                            plasticID,
                            plasticID,
                        ),
                    )
                    if len(sql.table) != 0:
                        self.LOG.info("log_plastic: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the insert_plastic_log query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_plastic: error={}".format(e))

        self.LOG.info("log_plastic: END")
        return -1

    # create plastics in bulk
    def create_plastics(
        self,
        verification: Verification,
        info_dict: Dict[int, dict],
        gaugeID: int | None = None,
    ) -> int:
        try:
            self.LOG.info(
                'create_plastics: verification="{}" info_dict={}'.format(
                    verification, info_dict
                )
            )
            self.gauge.update_gauge(
                gaugeID,
                self.LOG,
                "create_plastics",
                index=0,
                length=len(info_dict),
                limit=100,
                label="Initializing",
            )

            batchID = -1

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # get batchID with aligners
                instances = list(info_dict.keys())

                # checkout each aligner
                plasticIDs = []
                for i in range(0, len(instances)):
                    plasticID = self.create_plastic(
                        info_dict[instances[i]]["description"],
                        verification,
                        info_dict[instances[i]]["lotNumber"],
                        info_dict[instances[i]]["secondaryID"],
                        info_dict[instances[i]]["expiration"],
                        info_dict[instances[i]]["amount"],
                        info_dict[instances[i]]["materialID"],
                        info_dict[instances[i]]["reference"],
                        info_dict[instances[i]]["number"],
                        info_dict[instances[i]]["plasticType"],
                        info_dict[instances[i]]["bakeIn"],
                        info_dict[instances[i]]["bakeTime"],
                    )
                    if plasticID < 0:
                        raise Exception(
                            "Instance {0} as a plastic submission failed!".format(
                                instances[i]
                            )
                        )
                    # get plasticID into result
                    plasticIDs.append(plasticID)
                    self.gauge.update_gauge(
                        gaugeID,
                        self.LOG,
                        "create_plastics",
                        index=i + 1,
                        length=len(instances),
                        limit=100,
                        label="Submitting plastic instance {}".format(instances[i]),
                    )

                batchID = self.batch_plastics(plasticIDs, verification)
                if batchID == -1:
                    raise Exception(
                        "Batch submission of aligners {0} failed!".format(plasticIDs)
                    )
            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_plastics: error={}".format(e))
            self.LOG.info("create_plastics: END")
            return -1  # other error

        self.LOG.info("create_plastics: batchID={}".format(batchID))
        self.LOG.info("create_plastics: END")
        return batchID  # no error

    # create a plastic
    def create_plastic(
        self,
        description: str,
        verification: Verification,
        lotNumber: str,
        secondaryID: str,
        expiration: str,
        amount: int,
        materialID: int,
        reference: str,
        number: int,
        plasticType: int,
        status: int = 10,
    ) -> int:
        try:
            self.LOG.info(
                'create_plastic: description="{}" verification={} lotNumber={} secondaryID={} expiration={} amount={} materialID={} reference={} number={} status={} plasticType={}'.format(
                    description,
                    verification,
                    lotNumber,
                    secondaryID,
                    expiration,
                    amount,
                    materialID,
                    reference,
                    number,
                    status,
                    plasticType,
                )
            )

            plasticID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_plastic,
                        (
                            description,
                            verification.get_verification(),
                            lotNumber,
                            materialID,
                            secondaryID,
                            expiration,
                            amount,
                            status,
                            reference,
                            number,
                            plasticType,
                        ),
                    )
                    if len(sql.table) != 0:
                        plasticID = int(sql.table[0]["plasticID"])

                        # log yield
                        self.log_plastic(
                            plasticID,
                            "New",
                            "plastic Created",
                            verification,
                            15,
                        )
                    else:
                        raise Exception(
                            "No results found with the insert_plastic query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_plastic: error={}".format(e))
            self.LOG.info("create_plastic: END")
            return -1  # other error

        self.LOG.info("create_plastic: plasticID={}".format(plasticID))
        self.LOG.info("create_plastic: END")
        return plasticID  # no error

    # update plastic
    def update_plastic_info(
        self,
        verification: Verification,
        plasticID: int,
        description,
        lotNumber: str,
        secondaryID,
        amount: int,
        reference: str,
        plasticNumber: int,
    ) -> int:
        try:
            self.LOG.info(
                "update_plastic: verification={}, plasticID={}, description={}, lotNumber={}, secondaryID={}, amount={}, reference={}, plasticNumber={}".format(
                    verification,
                    plasticID,
                    description,
                    lotNumber,
                    secondaryID,
                    amount,
                    reference,
                    plasticNumber,
                )
            )

            result = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_plastic,
                        (
                            description,
                            lotNumber,
                            secondaryID,
                            amount,
                            reference,
                            plasticNumber,
                            plasticID,
                        ),
                    )
                    if len(sql.table) != 0:
                        result = int(sql.table[0]["plasticID"])

                        # log plastic
                        self.log_plastic(
                            plasticID,
                            "Update",
                            "plastic Updated",
                            verification,
                            49,
                        )
                    else:
                        raise Exception(
                            "No results found with the update_plastic query!"
                        )
                else:
                    raise Exception("Invalid verification")

        except Exception as e:
            self.LOG.error("update_plastic: error={}".format(e))
            self.LOG.info("update_plastic: END")
            return -1  # other error

        self.LOG.info("update_plastic: plasticID={}".format(result))
        self.LOG.info("update_plastic: END")
        return result  # no error

    # updates the status of a plastic
    def update_status_of_plastic(
        self, verification: Verification, plasticID: int, status: int
    ) -> int:
        try:
            self.LOG.info(
                "update_status_of_plastic: verification={} plasticID={} status={}".format(
                    verification, plasticID, status
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
                    sql.execute(self.update_plastic_status, (status, plasticID))
                    if len(sql.table) != 0:
                        self.LOG.info("update_status_of_plastic: END")

                        # log yield
                        self.log_plastic(
                            plasticID,
                            "Status: {0}".format(label),
                            "Status Updated",
                            verification,
                            16,
                        )
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_plastic_status query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_status_of_plastic: error={}".format(e))

        self.LOG.info("update_status_of_plastic: END")
        return -1

    def update_amount_of_plastic(
        self, verification: Verification, plasticID: int, amount: float
    ) -> int:
        try:
            self.LOG.info(
                "update_amount_of_plastic: verification={} plasticID={} amount={}".format(
                    verification, plasticID, amount
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_plastic_amount, (max(amount, 0), plasticID))
                    if len(sql.table) != 0:
                        self.LOG.info("update_amount_of_plastic: END")

                        # log plastic
                        self.log_plastic(
                            plasticID,
                            "Amount: {0}".format(amount),
                            "Amount Updated",
                            verification,
                            17,
                        )

                        # success
                        self.LOG.info("update_amount_of_plastic: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_plastic_amount query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_amount_of_plastic: error={}".format(e))

        self.LOG.info("update_amount_of_plastic: END")
        return -1

    # places a plastic in repair
    def submit_plastic_for_repair(
        self, verification: Verification, plasticID: int, repairTime: str
    ) -> int:
        try:
            self.LOG.info(
                "submit_plastic_for_repair: verification={} plasticID={} repairTime={}".format(
                    verification, plasticID, repairTime
                )
            )

            repairID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_plastic_repair,
                        (plasticID, repairTime, verification.get_verification()),
                    )
                    if len(sql.table) != 0:
                        repairID = int(sql.table[0]["RepairID"])

                        # mark plastic for repair
                        self.update_status_of_plastic(verification, plasticID, 8)

                        # log plastic
                        self.log_plastic(
                            plasticID,
                            "Repair",
                            "plastic Sent for Repair",
                            verification,
                            18,
                        )
                    else:
                        raise Exception(
                            "No results found with the insert_plastic_repair query!"
                        )
                else:
                    raise Exception("Invalid verification")

        except Exception as e:
            self.LOG.error("submit_plastic_for_repair: error={}".format(e))
            self.LOG.info("submit_plastic_for_repair: END")
            return -1  # other error

        self.LOG.info("submit_plastic_for_repair: repairID={}".format(repairID))
        self.LOG.info("submit_plastic_for_repair: END")
        return repairID  # no error

    # gets repair status' of a given plastic
    def get_repair_status_for_plastic(self, plasticID: int):
        try:
            self.LOG.info(
                "get_repair_status_for_plastic: plasticID={}".format(plasticID)
            )

            repair = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_repair_by_plastic, (plasticID))
                if len(sql.table) != 0:
                    repair = sql.table
                else:
                    raise Exception(
                        "No results found with the get_repair_by_plastic query!"
                    )

        except Exception as e:
            self.LOG.error("get_repair_status_for_plastic: error={}".format(e))
            self.LOG.info("get_repair_status_for_plastic: END")
            return -1  # other error

        self.LOG.info("get_repair_status_for_plastic: repair={}".format(repair))
        self.LOG.info("get_repair_status_for_plastic: END")
        return repair  # no error

    # get plastics in repair
    def get_repair_plastics(self) -> list:
        try:
            self.LOG.info("get_repair_plastics: BEGIN")

            plastics = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_repair_plastics)
                if len(sql.table) > 0:
                    plastics = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_repair_plastics query!"
                    )

        except Exception as e:
            self.LOG.error("get_repair_plastics: error={}".format(e))
            self.LOG.info("get_repair_plastics: END")
            return []

        self.LOG.info("get_repair_plastics: plastics={}".format(plastics))
        self.LOG.info("get_repair_plastics: END")
        return plastics

    # logs a set of plastics as part of a batch
    def batch_plastics(self, plasticIDs: List[int], verification: Verification) -> int:
        try:
            self.LOG.info(
                "batch_plastics: plasticIDs={} verification={}".format(
                    plasticIDs, verification
                )
            )

            batchID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # insert batch
                    sql.execute(
                        self.insert_plastic_batch,
                        (len(plasticIDs), verification.get_verification()),
                    )
                    # get batch ID
                    if len(sql.table) != 0:
                        batchID = int(sql.table[0]["ID"])
                        # link each plasticID with new batchID
                        for plasticID in plasticIDs:
                            sql.execute(
                                self.insert_plastic_batch_link,
                                (plasticID, batchID, verification.get_verification()),
                            )
                            if len(sql.table) == 0:
                                raise Exception(
                                    "No results found with the insert_plastic_batch_link query!"
                                )
                    else:
                        raise Exception(
                            "No results found with the insert_plastic_batch query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("batch_plastics: error={}".format(e))
            self.LOG.info("batch_plastics: END")
            return -1

        self.LOG.info("batch_plastics: batchID={}".format(batchID))
        self.LOG.info("batch_plastics: END")
        return batchID

    def empty_plastic(self, verification: Verification, plasticID: int) -> int:
        try:
            self.LOG.info(
                "empty_plastic: verification={} plasticID={}".format(
                    verification, plasticID
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.checkout_plastic,
                        (verification.get_verification(), plasticID),
                    )
                    if len(sql.table) == 0:
                        raise Exception(
                            "No results found with the checkout_plastic query!"
                        )

                    # update that plastics status
                    self.update_status_of_plastic(verification, plasticID, 6)

                    # update yield log and bin log to reflect lot cancel
                    self.log_plastic(
                        plasticID,
                        "plastic Checkout {}".format(plasticID),
                        "Checkout",
                        verification,
                        19,
                    )

                    # success
                    self.LOG.info("empty_plastic: END")
                    return 0
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("empty_plastic: error={}".format(e))

        self.LOG.info("empty_plastic: END")
        return -1

    # Sag test involves scanning a plastic sheet with a given density checker
    # camera. Results include the spot coverage in relation to the area of the
    # camera's range, spot average in relation to the average size of spots,
    # spot count in relation to the area of the camera's range. The therm
    # profile, is the profile used on the thermoformer for testing purposes.
    def create_yield_sag_test(
        self,
        verification: Verification,
        yieldID: int,
        spot_coverage: int,
        spot_average: int,
        spot_count: int,
        therm_code: int,
        test_diameter: int,
        type_status: int,
        machineID: int = -1,
    ) -> int:
        try:
            self.LOG.info(
                "create_yield_sag_test: verification={} yieldID={} spot_coverage={} spot_average={} spot_count={} therm_code={} test_diameter={}, type_status={}".format(
                    verification,
                    yieldID,
                    spot_coverage,
                    spot_average,
                    spot_count,
                    therm_code,
                    test_diameter,
                    type_status,
                )
            )

            # subtract one unit from yield
            # get the quantity of the given yield
            # get yields plastic
            result = self.get_yields_by_id(yieldID)
            if len(result) == 0:
                raise Exception(
                    "No result for yield {} could be found within the database!".format(
                        yieldID
                    )
                )
            plasticID = result[0]["PlasticID"]
            # 2 is the column for quantity from query
            quantity = result[0]["Quantity"]

            # get the difference
            difference = quantity - 1

            # update the yield quantity with new difference
            result = self.update_quantity_of_yield(verification, yieldID, difference)
            if result == -1:
                raise Exception(
                    "Unable to update the quantity of yield {} to {}!".format(
                        yieldID, difference
                    )
                )

            # submit sag test results
            entry = -1
            with SQL_Pull()(self.sql_config)() as sql:
                # submit a yield sag test
                sql.execute(
                    self.insert_yield_sag,
                    (
                        yieldID,
                        spot_coverage,
                        spot_average,
                        spot_count,
                        verification.get_verification(),
                        therm_code,
                        test_diameter,
                        type_status,
                        machineID,
                    ),
                )
                if len(sql.table) > 0:
                    entry = sql.table[0]["ID"]
                    if entry < 0:
                        raise Exception(
                            "No results found creating the sag test for the given yield {}!".format(
                                yieldID
                            )
                        )

                    # submit a plastic sag test
                    sql.execute(
                        self.insert_plastic_sag,
                        (
                            plasticID,
                            spot_coverage,
                            spot_average,
                            spot_count,
                            verification.get_verification(),
                            therm_code,
                            test_diameter,
                            type_status,
                            machineID,
                        ),
                    )
                    if len(sql.table) > 0:
                        entry = sql.table[0]["ID"]
                        if entry < 0:
                            raise Exception(
                                "No results found creating the sag test for the given plastic {}!".format(
                                    plasticID
                                )
                            )
                    else:
                        raise Exception(
                            "No results found with the insert_plastic_sag query!"
                        )
                else:
                    raise Exception("No results found with the insert_yield_sag query!")

        except Exception as e:
            self.LOG.error("create_yield_sag_test: error={}".format(e))
            self.LOG.info("create_yield_sag_test: END")
            return -1

        self.LOG.info("create_yield_sag_test: entry={}".format(entry))
        self.LOG.info("create_yield_sag_test: END")
        return entry

    # gets all sags for a particular yield
    def get_sag_by_yield(self, yieldID: int) -> list:
        try:
            self.LOG.info("get_sag_by_yield: yieldID={}".format(yieldID))

            sags = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_yield_sag_by_yield, (yieldID))
                if len(sql.table) > 0:
                    sags = sql.table
                else:
                    raise Exception(
                        "No results found with the get_yield_sag_by_yield query!"
                    )

        except Exception as e:
            self.LOG.error("get_sag_by_yield: error={}".format(e))
            self.LOG.info("get_sag_by_yield: END")
            return []

        self.LOG.info("get_sag_by_yield: sags={}".format(sags))
        self.LOG.info("get_sag_by_yield: END")
        return sags

    # gets yields by status
    def get_yields(self, statuses) -> list:
        try:
            self.LOG.info(f"get_yields: statuses={statuses}")

            yields = []
            with SQL_Pull()(self.sql_config)() as sql:
                if statuses is not None:
                    sql.execute(
                        self.get_yields_by_status, (",".join(map(str, statuses)))
                    )
                else:
                    sql.execute(self.get_all_yields)
                if len(sql.table) > 0:
                    yields = sql.table
                else:
                    raise Exception("No results found with the get_all_yields query!")

        except Exception as e:
            self.LOG.error("get_yields: error={}".format(e))
            self.LOG.info("get_yields: END")
            return []

        self.LOG.info("get_yields: yields={}".format(yields))
        self.LOG.info("get_yields: END")
        return yields

    # gets all yields
    def get_yields_by_plasticid(self, plasticID: int) -> list:
        try:
            self.LOG.info("get_yields_by_plasticid: plasticID={}".format(plasticID))

            yields = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_yields_by_plastic, (plasticID))
                if len(sql.table) > 0:
                    yields = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_yields_by_plastic query!"
                    )

        except Exception as e:
            self.LOG.error("get_yields_by_plasticid: error={}".format(e))
            self.LOG.info("get_yields_by_plasticid: END")
            return []

        self.LOG.info("get_yields_by_plasticid: yields={}".format(yields))
        self.LOG.info("get_yields_by_plasticid: END")
        return yields

    # gets a yield by given id
    def get_yields_by_id(self, yieldID: int) -> list:
        try:
            self.LOG.info("get_yields_by_id: yieldID={}".format(yieldID))

            yields = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_yields_by_ID, (yieldID))
                if len(sql.table) > 0:
                    yields = sql.table
                else:
                    raise Exception("No results found with the get_yields_by_ID query!")

        except Exception as e:
            self.LOG.error("get_yields_by_id: error={}".format(e))
            self.LOG.info("get_yields_by_id: END")
            return []

        self.LOG.info("get_yields_by_id: yields={}".format(yields))
        self.LOG.info("get_yields_by_id: END")
        return yields

    # gets the yield quantity of a given yield id
    def get_quantity_of_yield(self, yieldID: int) -> list:
        try:
            self.LOG.info("get_quantity_of_yield: yieldID={}".format(yieldID))

            quantity = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_yield_quantity, (yieldID))
                if len(sql.table) > 0:
                    quantity = sql.table[0]
                else:
                    raise Exception(
                        "No results found with the get_yield_quantity query!"
                    )

        except Exception as e:
            self.LOG.error("get_quantity_of_yield: error={}".format(e))
            self.LOG.info("get_quantity_of_yield: END")
            return []

        self.LOG.info("get_quantity_of_yield: quantity={}".format(quantity))
        self.LOG.info("get_quantity_of_yield: END")
        return quantity

    # logs a change to a yield
    def log_yield(
        self,
        yieldID: int,
        change: str,
        description: str,
        verification: Verification,
        logtype: int,
    ) -> int:
        try:
            self.LOG.info(
                'log_yield: yieldID={} change="{}" description="{}" verification={} logtype={}'.format(
                    yieldID, change, description, verification, logtype
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_yield_log,
                        (
                            yieldID,
                            logtype,
                            change,
                            description,
                            verification.get_verification(),
                            yieldID,
                            yieldID,
                            yieldID,
                            yieldID,
                            yieldID,
                        ),
                    )
                    if len(sql.table) != 0:
                        self.LOG.info("log_yield: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the insert_yield_log query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_yield: error={}".format(e))

        self.LOG.info("log_yield: END")
        return -1

    def create_yield_waste_link(
        self, verification: Verification, yieldID: int, wasteRecordID: int
    ) -> int:
        try:
            self.LOG.info(
                "create_yield: verification={} yieldID={} wasteRecordID={}".format(
                    verification, yieldID, wasteRecordID
                )
            )

            linkID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_yield_waste_link,
                        (
                            yieldID,
                            wasteRecordID,
                            verification.get_verification(),
                        ),
                    )
                    if len(sql.table) != 0:
                        linkID = int(sql.table[0]["ID"])

                        # update yield status
                        self.log_yield(
                            yieldID,
                            "Link",
                            "Waste Linked",
                            verification,
                            LogTypes.YIELD_STATUS_UPDATED.value,
                        )
                    else:
                        raise Exception("No results found with the insert_yield query!")
                else:
                    raise Exception("Invalid verification")

        except Exception as e:
            self.LOG.error("create_yield: error={}".format(e))
            self.LOG.info("create_yield: END")
            return -1  # other error

        self.LOG.info("create_yield: linkID={}".format(linkID))
        self.LOG.info("create_yield: END")
        return linkID  # no error

    # creates a yield given a plastic and length/quantity from plastic
    def create_yield(
        self,
        plasticID: int,
        verification: Verification,
        length,
        total: int,
        status: int = 7,
        wasteRecordID: int | None = None,
    ) -> int:
        try:
            self.LOG.info(
                "create_yield: plasticID={} verification={} length={} total={} status={} wasteRecordID={}".format(
                    plasticID, verification, length, total, status, wasteRecordID
                )
            )

            yieldID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_yield,
                        (
                            plasticID,
                            verification.get_verification(),
                            length,
                            total,
                            total,
                            status,
                        ),
                    )
                    if len(sql.table) != 0:
                        yieldID = int(sql.table[0]["YieldID"])

                        # update yield status
                        self.log_yield(
                            yieldID, "New", "Yield Created", verification, 20
                        )
                    else:
                        raise Exception("No results found with the insert_yield query!")

                    # link waste if provided
                    if wasteRecordID is not None:
                        self.create_yield_waste_link(
                            verification, yieldID, wasteRecordID
                        )
                else:
                    raise Exception("Invalid verification")

        except Exception as e:
            self.LOG.error("create_yield: error={}".format(e))
            self.LOG.info("create_yield: END")
            return -1  # other error

        self.LOG.info("create_yield: yieldID={}".format(yieldID))
        self.LOG.info("create_yield: END")
        return yieldID  # no error

    # empties a lot and makes a lot's yield unavailable and bin now available
    def empty_yield(
        self,
        verification: Verification,
        yieldID: int,
        status: int = 6,
        clear_lots: bool = True,
    ) -> int:
        try:
            self.LOG.info(
                "empty_yield: verification={} yieldID={}".format(verification, yieldID)
            )

            # check if yield is already empty
            yield_info = self.get_yields_by_id(yieldID)
            if len(yield_info) == 0:
                raise Exception(
                    "Unable to retrieve yield info from provided yield {}!".format(
                        yieldID
                    )
                )
            # 10 is the column for status
            yield_status = yield_info[0]["Status"]
            # check if status has already been updated to provided status
            if yield_status == status:
                return 0

            # employee check
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # update status of yield and check it out
                if self.update_status_of_yield(verification, yieldID, status) == -1:
                    raise Exception(
                        "No results found updating the status of yield {}!".format(
                            yieldID
                        )
                    )

                # checkout yield
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.checkout_yield, (verification.get_verification(), yieldID)
                    )
                    if len(sql.table) == 0:
                        raise Exception(
                            "No results found with the checkout_yield query!"
                        )

                # update yield log and bin log to reflect lot cancel
                self.log_yield(
                    yieldID,
                    "Yield Checked Out",
                    "Checkout",
                    verification,
                    21,
                )

                # get any lots associated with yield
                if clear_lots is True:
                    lots = self.get_lots_from_yield(yieldID)
                    if len(lots) > 0:
                        # we have lots, empty each one that needs emptied
                        for lot in lots:
                            # check if dateout column is null and status column is marked as available with its id 7
                            if lot["DateOut"] is None:
                                # empty lot
                                self.empty_lot(verification, lot["LotID"])
                    else:
                        self.LOG.info(
                            "No lots were found associated with the yield {}!".format(
                                yieldID
                            )
                        )

                # success
                self.LOG.info("empty_yield: END")
                return 0

            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("empty_yield: error={}".format(e))

        self.LOG.info("empty_yield: END")
        return -1  # no error

    # updates the quantity of a yield
    def update_quantity_of_yield(
        self,
        verification: Verification,
        yieldID: int,
        quantity: int,
        clear_lots: bool = True,
    ) -> int:
        try:
            self.LOG.info(
                "update_quantity_of_yield: verification={} yieldID={} quantity={}".format(
                    verification, yieldID, quantity
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_yield_quantity, (max(quantity, 0), yieldID))
                    if len(sql.table) != 0:
                        self.LOG.info("update_quantity_of_yield: END")

                        # log yield
                        self.log_yield(
                            yieldID,
                            "Quantity: {0}".format(quantity),
                            "Quantity Updated",
                            verification,
                            21,
                        )

                        # if quantity is 0, empty any yields and lots associated with this
                        # yield ID
                        if quantity <= 0 and clear_lots is True:
                            self.empty_yield(verification, yieldID)

                        # success
                        self.LOG.info("update_quantity_of_yield: END")
                        return 0

                    else:
                        raise Exception(
                            "No results found with the update_yield_quantity query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_quantity_of_yield: error={}".format(e))

        self.LOG.info("update_quantity_of_yield: END")
        return -1

    # updates the status of a yield
    def update_status_of_yield(
        self, verification: Verification, yieldID: int, status: int
    ) -> int:
        try:
            self.LOG.info(
                "update_status_of_yield: verification={} yieldID={} status={}".format(
                    verification, yieldID, status
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
                    sql.execute(self.update_yield_status, (status, yieldID))
                    if len(sql.table) != 0:
                        self.LOG.info("update_status_of_yield: END")

                        # log yield
                        self.log_yield(
                            yieldID,
                            "Status: {0}".format(label),
                            "Status Updated",
                            verification,
                            23,
                        )
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_yield_status query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_status_of_yield: error={}".format(e))

        self.LOG.info("update_status_of_yield: END")
        return -1

    # submits a yield for repair
    def submit_yield_for_repair(
        self, verification: Verification, yieldID: int, repairTime: str
    ) -> int:
        try:
            self.LOG.info(
                "submit_yield_for_repair: verification={} yieldID={} repairTime={}".format(
                    verification, yieldID, repairTime
                )
            )

            repairID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_yield_repair,
                        (yieldID, repairTime, verification.get_verification()),
                    )
                    if len(sql.table) != 0:
                        repairID = int(sql.table[0]["RepairID"])

                        # change status to disabled
                        self.update_status_of_yield(verification, yieldID, 8)

                        # log yield
                        self.log_yield(
                            yieldID,
                            "Repair",
                            "Yield Sent for Repair",
                            verification,
                            24,
                        )
                    else:
                        raise Exception(
                            "No results found with the submit_yield_for_repair query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("submit_yield_for_repair: error={}".format(e))
            self.LOG.info("submit_yield_for_repair: END")
            return -1  # other error

        self.LOG.info("submit_yield_for_repair: repairID={}".format(repairID))
        self.LOG.info("submit_yield_for_repair: END")
        return repairID

    # gets repair status' of a given plastic
    def get_repair_status_for_yield(self, yieldID: int):
        try:
            self.LOG.info("get_repair_status_for_yield: yieldID={}".format(yieldID))

            repair = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_repair_by_yield, (yieldID))
                if len(sql.table) != 0:
                    repair = sql.table
                else:
                    raise Exception(
                        "No results found with the get_repair_by_yield query!"
                    )

        except Exception as e:
            self.LOG.error("get_repair_status_for_yield: error={}".format(e))
            self.LOG.info("get_repair_status_for_yield: END")
            return -1  # other error

        self.LOG.info("get_repair_status_for_yield: repair={}".format(repair))
        self.LOG.info("get_repair_status_for_yield: END")
        return repair  # no error

    # get yields in repair
    def get_repair_yields(self) -> list:
        try:
            self.LOG.info("get_repair_yields: BEGIN")

            yields = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_repair_yields)
                if len(sql.table) > 0:
                    yields = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_repair_yields query!"
                    )

        except Exception as e:
            self.LOG.error("get_repair_yields: error={}".format(e))
            self.LOG.info("get_repair_yields: END")
            return []

        self.LOG.info("get_repair_yields: yields={}".format(yields))
        self.LOG.info("get_repair_yields: END")
        return yields

    def get_bins(self, status=None) -> list:
        try:
            self.LOG.info(f"get_bins: status={status}")

            lots = []

            with SQL_Pull()(self.sql_config)() as sql:
                if status is not None:
                    sql.execute(self.get_bins_by_status, (status))
                else:
                    sql.execute(self.get_all_bins)
                if len(sql.table) != 0:
                    lots = sql.table
                else:
                    raise Exception("No results found with the get_all_bins query!")

        except Exception as e:
            self.LOG.error("get_bins: error={}".format(e))
            self.LOG.info("get_bins: END")
            return []  # other error

        self.LOG.info("get_bins: lots={}".format(lots))
        self.LOG.info("get_bins: END")
        return lots  # no error

    # get bin given an id
    def get_bins_by_id(self, binID: int) -> list:
        try:
            self.LOG.info("get_bins_by_id: binID={}".format(binID))

            bins = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_bins_by_ID, (binID))
                if len(sql.table) > 0:
                    bins = sql.table
                else:
                    raise Exception("No results found with the get_bins_by_ID query!")

        except Exception as e:
            self.LOG.error("get_bins_by_id: error={}".format(e))
            self.LOG.info("get_bins_by_id: END")
            return []

        self.LOG.info("get_bins_by_id: bins={}".format(bins))
        self.LOG.info("get_bins_by_id: END")
        return bins  # no error

    # log a change in a bin
    def log_bin(
        self,
        binID: int,
        change: str,
        description: str,
        verification: Verification,
        logtype: int,
    ) -> int:
        try:
            self.LOG.info(
                'log_bin: binID={} change="{}" description="{}" verification={} logtype={}'.format(
                    binID, change, description, verification, logtype
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_bin_log,
                        (
                            binID,
                            logtype,
                            change,
                            description,
                            verification.get_verification(),
                            binID,
                            binID,
                            binID,
                            binID,
                            binID,
                        ),
                    )
                    if len(sql.table) != 0:
                        self.LOG.info("log_bin: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the insert_bin_log query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_bin: error={}".format(e))

        self.LOG.info("log_bin: END")
        return -1

    # creates a bin
    def create_bin(
        self,
        verification: Verification,
        description: str,
        bin_type: str,
        status: int = 7,
    ) -> int:
        try:
            self.LOG.info(
                "create_bin: verification={} description={} bin_type={} status={}".format(
                    verification, description, bin_type, status
                )
            )

            binID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_bin,
                        (
                            description,
                            verification.get_verification(),
                            bin_type,
                            status,
                        ),
                    )
                    if len(sql.table) != 0:
                        binID = int(sql.table[0]["BinID"])

                        # update yield status
                        self.log_bin(binID, "New", "Bin Created", verification, 27)
                    else:
                        raise Exception("No results found with the insert_bin query!")
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_bin: error={}".format(e))
            self.LOG.info("create_bin: END")
            return -1  # other error

        self.LOG.info("create_bin: binID={}".format(binID))
        self.LOG.info("create_bin: END")
        return binID  # no error

    # updates the status of a bin
    def update_status_of_bin(
        self, verification: Verification, binID: int, status: int
    ) -> int:
        try:
            self.LOG.info(
                "update_status_of_bin: verification={} binID={} status={}".format(
                    verification, binID, status
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
                    sql.execute(self.update_bin_status, (status, binID))
                    if len(sql.table) != 0:
                        self.LOG.info("update_status_of_bin: END")

                        # log yield
                        self.log_bin(
                            binID,
                            "Status: {0}".format(label),
                            "Status Updated",
                            verification,
                            28,
                        )
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_bin_status query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_status_of_bin: error={}".format(e))

        self.LOG.info("update_status_of_bin: END")
        return -1

    # logs a change to a lot
    def log_lot(
        self,
        lotID: int,
        change: str,
        description: str,
        verification: Verification,
        logtype: int,
    ) -> int:
        try:
            self.LOG.info(
                'log_lot: lotID={} change="{}" description="{}" verification={} logtype={}'.format(
                    lotID, change, description, verification, logtype
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_lot_log,
                        (
                            lotID,
                            logtype,
                            change,
                            description,
                            verification.get_verification(),
                            lotID,
                            lotID,
                            lotID,
                        ),
                    )
                    if len(sql.table) != 0:
                        self.LOG.info("log_lot: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the insert_lot_log query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_lot: error={}".format(e))

        self.LOG.info("log_lot: END")
        return -1

    # given a bin and yield, makes a lot
    def create_lot(
        self,
        verification: Verification,
        binID,
        yieldID,
        description: str,
        production_line: int,
        status: int = 10,
    ) -> int:
        try:
            self.LOG.info(
                "create_lot: verification={} binID={} yieldID={} description={} status={}".format(
                    verification, binID, yieldID, description, status
                )
            )

            lotID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_lot,
                        (
                            yieldID,
                            binID,
                            description,
                            verification.get_verification(),
                            status,
                        ),
                    )
                    if len(sql.table) != 0:
                        lotID = int(sql.table[0]["LotID"])

                        # update status of bin and yield
                        if yieldID is not None:
                            self.update_status_of_yield(verification, yieldID, 9)

                        if binID is not None:
                            self.update_status_of_bin(verification, binID, 9)

                        if binID is not None and yieldID is not None:
                            # update yield log
                            self.log_yield(
                                yieldID,
                                "Bin Merged with Yield {}".format(binID),
                                "Lot created",
                                verification,
                                25,
                            )
                            # update bin log
                            self.log_bin(
                                binID,
                                "Yield Merged with Bin {}".format(yieldID),
                                "Lot created",
                                verification,
                                29,
                            )

                        # log lot
                        self.log_lot(lotID, "New", "Lot Created", verification, 31)
                    else:
                        raise Exception("No results found with the insert_lot query!")
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_lot: error={}".format(e))
            self.LOG.info("create_lot: END")
            return -1  # other error

        self.LOG.info("create_lot: lotID={}".format(lotID))
        self.LOG.info("create_lot: END")
        return lotID  # no error

    # empties a lot and makes a lot's yield unavailable and bin now available
    def empty_lot(self, verification: Verification, lotID: int) -> int:
        try:
            self.LOG.info(
                "empty_lot: verification={} lotID={}".format(verification, lotID)
            )

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                # update status of lot and check it out
                # 6 is the UNAVAILABLE status
                if self.update_status_of_lot(verification, lotID, status=6) == -1:
                    raise Exception(
                        "No results found updating the status of lot {}!".format(lotID)
                    )
                # checkout lot
                with SQL_Pull()(self.sql_config)() as sql:
                    self.LOG.info(
                        "empty_lot: verification='{}'".format(
                            verification.get_verification()
                        )
                    )
                    sql.execute(
                        self.checkout_lot, (verification.get_verification(), lotID)
                    )
                    if len(sql.table) == 0:
                        raise Exception("No results found with the checkout_lot query!")

                # get bin
                result = self.get_bin_from_lot(lotID)
                if result == -1:
                    raise Exception(
                        "No results found retrieving the bin from the given lot {}!".format(
                            lotID
                        )
                    )
                binID = result

                # get yield
                result = self.get_yield_from_lot(lotID)
                if result == -1:
                    raise Exception(
                        "No results found retrieving the yield from the given lot {}!".format(
                            lotID
                        )
                    )
                yieldID = result

                # update status of bin and yield
                result = self.get_quantity_of_yield(yieldID)
                if len(result) == 0:
                    raise Exception(
                        "No results found retrieving the quantity of yield ID {}!".format(
                            yieldID
                        )
                    )
                # 2 has the quantity column from the given yield
                quantity = result["Quantity"]
                if quantity > 0:
                    # yield still has material for a lot creation
                    # 7 is the status for AVAILABLE
                    if (
                        self.update_status_of_yield(verification, yieldID, status=7)
                        == -1
                    ):
                        raise Exception(
                            "No results found updating the status of yield {}!".format(
                                yieldID
                            )
                        )
                else:
                    # yield is empty anyway, mark as unavailable
                    self.empty_yield(verification, yieldID, clear_lots=False)

                # 7 is the status for AVAILABLE
                if self.update_status_of_bin(verification, binID, status=7) == -1:
                    raise Exception(
                        "No results found updating the status of bin {}!".format(binID)
                    )

                # update yield log and bin log to reflect lot cancel
                self.log_yield(
                    yieldID,
                    "Lot Ended {}".format(lotID),
                    "Lot ended",
                    verification,
                    26,
                )
                self.log_bin(
                    binID,
                    "Lot Ended {}".format(lotID),
                    "Lot ended",
                    verification,
                    30,
                )

                # log lot
                self.log_lot(
                    lotID,
                    "Lot Checked Out",
                    "Checkout",
                    verification,
                    33,
                )

                # success
                self.LOG.info("empty_lot: END")
                return 0

            else:
                raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("empty_lot: error={}".format(e))

        self.LOG.info("empty_lot: END")
        return -1  # no error

    # gets a bin from a lot id
    def get_bin_from_lot(self, lotID: int) -> int:
        try:
            self.LOG.info("get_bin_from_lot: lotID={}".format(lotID))

            binID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_lot_bin, (lotID))
                if len(sql.table) != 0:
                    binID = int(sql.table[0]["BinID"])
                else:
                    raise Exception("No results found with the get_lot_bin query!")

        except Exception as e:
            self.LOG.error("get_bin_from_lot: error={}".format(e))
            self.LOG.info("get_bin_from_lot: END")
            return -1  # other error

        self.LOG.info("get_bin_from_lot: binID={}".format(binID))
        self.LOG.info("get_bin_from_lot: END")
        return binID  # no error

    # gets a yield from a lot id
    def get_yield_from_lot(self, lotID: int) -> int:
        try:
            self.LOG.info("get_bin_from_lot: lotID={}".format(lotID))

            yieldID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_lot_yield, (lotID))
                if len(sql.table) != 0:
                    yieldID = int(sql.table[0]["YieldID"])
                else:
                    raise Exception("No results found with the get_lot_yield query!")

        except Exception as e:
            self.LOG.error("get_yield_from_lot: error={}".format(e))
            self.LOG.info("get_yield_from_lot: END")
            return -1  # other error

        self.LOG.info("get_yield_from_lot: yieldID={}".format(yieldID))
        self.LOG.info("get_yield_from_lot: END")
        return yieldID  # no error

    def get_lots_from_yield(
        self, yieldID: int, offset: int = 0, rows: int = 1000
    ) -> list:
        try:
            self.LOG.info(
                f"get_lots_from_yield: yieldID={yieldID} offset={offset} rows={rows}"
            )

            lots = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_lots_by_yield, (yieldID, offset, rows))
                if len(sql.table) != 0:
                    lots = sql.table
                else:
                    raise Exception(
                        "No results found with the get_lots_by_yield query!"
                    )

        except Exception as e:
            self.LOG.error("get_lots_from_yield: error={}".format(e))
            self.LOG.info("get_lots_from_yield: END")
            return []  # other error

        self.LOG.info("get_lots_from_yield: lots={}".format(lots))
        self.LOG.info("get_lots_from_yield: END")
        return lots  # no error

    def get_lots(self, offset: int, rows: int, statuses: list) -> list:
        try:
            self.LOG.info(f"get_lots: statuses={statuses} offset={offset} rows={rows}")

            lots = []

            with SQL_Pull()(self.sql_config)() as sql:
                if statuses is not None:
                    filter_valid_status = ",".join(
                        map(lambda status: str(status), (statuses))
                    )
                    sql.execute(
                        self.get_lots_by_status, (filter_valid_status, offset, rows)
                    )
                else:
                    sql.execute(self.get_all_lots, (offset, rows))
                if len(sql.table) != 0:
                    lots = sql.table
                else:
                    raise Exception("No results found with the get_all_lots query!")

        except Exception as e:
            self.LOG.error("get_lots: error={}".format(e))
            self.LOG.info("get_lots: END")
            return []  # other error

        self.LOG.info("get_lots: lots={}".format(lots))
        self.LOG.info("get_lots: END")
        return lots  # no error

    # get lots given an id
    def get_lots_by_id(self, lotID: int) -> list:
        try:
            self.LOG.info("get_lots_by_id: lotID={}".format(lotID))

            lots = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_lots_by_ID, (lotID))
                if len(sql.table) > 0:
                    lots = sql.table
                else:
                    raise Exception("No results found with the get_lots_by_ID query!")

        except Exception as e:
            self.LOG.error("get_lots_by_id: error={}".format(e))
            self.LOG.info("get_lots_by_id: END")
            return []

        self.LOG.info("get_lots_by_id: lots={}".format(lots))
        self.LOG.info("get_lots_by_id: END")
        return lots  # no error

    # gets lots by the given production line
    def get_lots_by_production_line(self, production_line: int) -> list:
        try:
            self.LOG.info(
                "get_lots_by_production_line: production_line={}".format(
                    production_line
                )
            )

            lots = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_lots_by_production_line, (production_line))
                if len(sql.table) > 0:
                    lots = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_lots_by_production_line query!"
                    )

        except Exception as e:
            self.LOG.error("get_lots_by_production_line: error={}".format(e))
            self.LOG.info("get_lots_by_production_line: END")
            return []

        self.LOG.info("get_lots_by_production_line: yields={}".format(lots))
        self.LOG.info("get_lots_by_production_line: END")
        return lots

    # updates production line of lot
    def update_lot_production_line(
        self, verification: str, lotID: int, production_line: int
    ) -> int:
        try:
            self.LOG.info(
                "update_lot_production_line: verification={} lotID={} production_line={}".format(
                    verification, lotID, production_line
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_production_line_of_lot, (production_line, lotID)
                    )
                    if len(sql.table) != 0:
                        self.LOG.info("update_lot_production_line: END")

                        # log yield
                        self.log_lot(
                            lotID,
                            "ProductionLine: {0}".format(production_line),
                            "Production Line Updated",
                            verification,
                            57,
                        )

                        # success
                        self.LOG.info("update_production_line_of_lot: END")
                        return 0

                    else:
                        raise Exception(
                            "No results found with the update_production_line_of_lot query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_lot_production_line: error={}".format(e))

        self.LOG.info("update_lot_production_line: END")
        return -1

    # get lots given an binID
    def get_lots_from_bin(self, binID: int, offset: int, rows: int) -> list:
        try:
            self.LOG.info(
                f"get_lots_from_bin: binID={binID} offset={offset} rows={rows}"
            )

            lots = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_lots_by_bin, (binID, offset, rows))
                if len(sql.table) > 0:
                    lots = sql.table
                else:
                    raise Exception("No results found with the get_lots_by_bin query!")

        except Exception as e:
            self.LOG.error("get_lots_from_bin: error={}".format(e))
            self.LOG.info("get_lots_from_bin: END")
            return []

        self.LOG.info("get_lots_from_bin: lots={}".format(lots))
        self.LOG.info("get_lots_from_bin: END")
        return lots  # no error

    # updates the status of a lot
    def update_status_of_lot(
        self, verification: Verification, lotID: int, status: int
    ) -> int:
        try:
            self.LOG.info(
                "update_status_of_lot: verification={} lotID={} status={}".format(
                    verification, lotID, status
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
                    sql.execute(self.update_lot_status, (status, lotID))
                    if len(sql.table) != 0:
                        self.LOG.info("update_status_of_lot: END")

                        # log yield
                        self.log_lot(
                            lotID,
                            "Status: {0}".format(label),
                            "Status Updated",
                            verification,
                            32,
                        )
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_lot_status query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_status_of_lot: error={}".format(e))

        self.LOG.info("update_status_of_lot: END")
        return -1

    # updates the bin of a lot
    def update_bin_of_lot(
        self, verification: Verification, lotID: int, binID: int
    ) -> int:
        try:
            self.LOG.info(
                "update_bin_of_lot: verification={} lotID={} binID={}".format(
                    verification, lotID, binID
                )
            )

            # check if bin exist
            result = self.get_bins_by_id(binID)
            if len(result) == 0:
                raise Exception(
                    "Unable to find a matching bin with given bin id {0}!".format(binID)
                )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_lot_bin, (binID, lotID))
                    if len(sql.table) != 0:
                        self.LOG.info("update_bin_of_lot: END")

                        # log lot
                        self.log_lot(
                            lotID,
                            "Lot Bin: {0}".format(binID),
                            "Lot Bin Updated",
                            verification,
                            46,
                        )
                        self.update_status_of_bin(verification, binID, 9)
                        # update bin log
                        self.log_bin(
                            binID,
                            "Update status of bin {}".format(binID),
                            "Lot Bin Updated",
                            verification,
                            28,
                        )
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_lot_bin query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_bin_of_lot: error={}".format(e))

        self.LOG.info("update_bin_of_lot: END")
        return -1

    # updates the yield of a lot
    def update_yield_of_lot(
        self, verification: Verification, lotID: int, yieldID: int
    ) -> int:
        try:
            self.LOG.info(
                "update_yield_of_lot: verification={} lotID={} yieldID={}".format(
                    verification, lotID, yieldID
                )
            )

            # check if yield exist
            result = self.get_yields_by_id(yieldID)
            if len(result) == 0:
                raise Exception(
                    "Unable to find a matching yield with given yield id {0}!".format(
                        yieldID
                    )
                )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_lot_yield, (yieldID, lotID))
                    if len(sql.table) != 0:
                        self.LOG.info("update_yield_of_lot: END")

                        # log lot
                        self.log_lot(
                            lotID,
                            "Lot Yield: {0}".format(yieldID),
                            "Lot Yield Updated",
                            verification,
                            47,
                        )
                        self.update_status_of_yield(verification, yieldID, 9)
                        # update yield log
                        self.log_yield(
                            yieldID,
                            "Update status of Yield {}".format(yieldID),
                            "Lot Yield Updated",
                            verification,
                            23,
                        )
                        return 0
                    else:
                        raise Exception(
                            "No results found with the update_lot_yield query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_yield_of_lot: error={}".format(e))

        self.LOG.info("update_yield_of_lot: END")
        return -1


# UNIT TESTING
def main():
    plasticID = 1
    yieldID = 1
    binID = 1006
    lotID = 1427
    batchID = 1
    verification = Verification()
    verification.add_account("100")

    with Lot() as lot:
        lot.create_yield(476, verification, 200, 150)
        batchID = lot.create_plastics(
            verification,
            {
                0: {
                    "description": "TEST plastic",
                    "lotNumber": 0000000,
                    "secondaryID": 0000000,
                    "expiration": datetime.datetime.now() + datetime.timedelta(days=80),
                    "length": 500,
                    "materialID": 1,
                }
            },
        )
        plastics = lot.get_plastics_by_batch(batchID)
        for plastic in plastics:
            plasticID = plastic["plasticID"]
            print(plasticID)
            print(lot.get_plastics_by_id(plasticID))

        # get bins
        print("Getting bin...")
        bins = lot.get_bins()
        print(bins)
        # binID = lot.create_bin(verification, "TEST BIN", "FAKE")
        print(lot.get_bins_by_id(binID))

        # create yield from plastic
        print("Getting yield...")
        yieldID = lot.create_yield(plasticID, verification, 100, 50)
        print(yieldID)
        print(lot.get_yields())
        print(
            lot.submit_yield_for_repair(verification, yieldID, datetime.datetime.now())
        )
        print(lot.update_status_of_yield(verification, yieldID, 7))
        print(lot.get_yields_by_id(yieldID))
        print(lot.get_quantity_of_yield(yieldID))
        print(lot.update_quantity_of_yield(verification, yieldID, 49))
        print(lot.get_quantity_of_yield(yieldID))

        # create a lot
        print("Getting lot...")
        lotID = lot.create_lot(verification, binID, yieldID, "TEST")
        print(lotID)
        print(lot.get_lots())
        print(lot.update_status_of_lot(verification, lotID, 6))
        print(lot.update_status_of_lot(verification, lotID, 7))
        print(lot.get_lots_from_yield(yieldID))
        print(lot.get_yield_from_lot(lotID))
        print(lot.get_bin_from_lot(lotID))

        # empty lot
        print("Emptying lot...")
        print(lot.empty_yield(verification, yieldID))
        # changing quantity to 0 will auto empty it
        print(lot.update_quantity_of_yield(verification, yieldID, 0))
        print(lot.empty_lot(verification, lotID))

    return


if __name__ == "__main__":
    main()
