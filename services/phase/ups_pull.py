#!/usr/bin/env python3.7

from os import link, getenv
import token
from typing import List, Dict
from datetime import date
import logging
import uuid

from .sql_pull import SQL_Pull

# from .ups_config import UPSConfig
import requests
from .verification_pull import Verification
import requests
from .token_pull import Token


class UPS:
    # used for entering class instance with with
    def __init__(self):
        # Create a Token object
        self.tok = Token()

        self.LOG = logging.getLogger("phase")

    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # input: Verification, caseID, shipment_description, shipper, payment_information, shipTo, shipFrom, package_description, service, package_weight, dimensions
    # output: shipment on success, {} on error
    def create_shipment(
        self,
        verification,
        caseID,
        shipment_description,
        shipper,
        payment_information,
        shipTo,
        shipFrom,
        package_description,
        service,
        package_weight,
        dimensions,
    ) -> dict:
        """
        ``caseID``,

        ``shipment_description``,

        ``Shipper``: {
            "Name"
            "AttentionName"
            "TaxIdentificationNumber"
            "Phone": {
                "Number"
                "Extension"
            },
            "ShipperNumber"
            "FaxNumber"
            "Address": {
                "AddressLine"
                "City"
                "StateProvinceCode"
                "PostalCode"
                "CountryCode"
            }
        },

        ``account_number``,

        ``payment_information``: {
            "ShipmentCharge": [{
                "Type": "01",
                "BillShipper": {
                    "AccountNumber"
                }
            }]
        }

        ``shipTo``: {
            "Name",
            "AttentionName",
            "Phone": {
                "Number",
                "Extension"
            },
            "Address": {
                "AddressLine",
                "City",
                "StateProvinceCode",
                "PostalCode",
                "CountryCode",
            },
            "Residential",
            },
        }

        ``ShipFrom``: {
            "Name",
            "AttentionName",
            "Phone": {
                "Number",
                "Extension",
            },
            "Address": {
                "AddressLine",
                "City",
                "StateProvinceCode",
                "PostalCode",
                "CountryCode",
            },
        },

        ``package_description``,

        ``service``: {
            "Code",
            "Description",
        },

        ``package_weight``,

        ``dimensions``: {
            "UnitOfMeasurement": {
                "Code",
                "Description",
            },
            "Length",
            "Width",
            "Height"
        }
        """
        try:
            shipment_response = {}

            # Get an active UPS token
            token = self.tok.get_UPS_token(verification)
            if token == {}:
                raise Exception("There was an error retrieving an active token!")
            else:
                ups_token = token["Token"]

                # Request version for UPS Shipping
                version = "v2409"
                # URL for UPS Shipping
                url = getenv("UPS_URL") + "api/shipments/" + version + "/ship"

                query = {
                    "regionalrequestindicator": "string",
                    "maximumcandidatelistsize": "1",
                }

                # Service list we use
                # 01 = Next Day Air
                # 02 = 2nd Day Air
                # 03 = Ground
                # 11 = UPS Standard
                # 12 = 3 Day Select
                # 13 = Next Day Air Saver
                # 14 = UPS Next Day Air® Early

                payload = {
                    "ShipmentRequest": {
                        "Request": {
                            "SubVersion": "1801",
                            "RequestOption": "nonvalidate",
                            "TransactionReference": {"CustomerContext": caseID},
                        },
                        "Shipment": {
                            "Description": shipment_description,
                            "Shipper": shipper,
                            "ShipTo": shipTo,
                            "ShipFrom": shipFrom,
                            "PaymentInformation": payment_information,
                            "Service": service,
                            "Package": [
                                {
                                    "Description": package_description,
                                    "Packaging": {
                                        "Code": "02",
                                        "Description": "Customer Supplied",
                                    },
                                    "Dimensions": dimensions,
                                    "PackageWeight": {
                                        "UnitOfMeasurement": {
                                            "Code": "LBS",
                                            "Description": "Pounds",
                                        },
                                        "Weight": package_weight,
                                    },
                                }
                            ],
                        },
                        "LabelSpecification": {
                            "LabelImageFormat": {"Code": "GIF", "Description": "GIF"},
                            "HTTPUserAgent": "Mozilla/4.5",
                        },
                    }
                }

                # Authorization Headers
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + ups_token,
                }

                response = requests.post(
                    url, json=payload, headers=headers, params=query
                )

                data = response.json()
                # Extract response data from response
                shipment_response = data

        except Exception as e:
            self.LOG.error("create_shipment: error={}".format(e))
            self.LOG.info("Exception when create_shipment!")
            return shipment_response

        # output token
        self.LOG.info(
            "create_shipment: create_shipment={}".format(str(shipment_response))
        )
        self.LOG.info("create_shipment: END")
        return shipment_response

    # input: Verification, tracking
    # output: shipment on success, {} on error
    def get_shipment(self, verification, tracking) -> dict:
        try:
            shipment_response = {}

            # Get an active UPS token
            token = self.tok.get_UPS_token(verification)
            if token == {}:
                raise Exception("There was an error retrieving an active token!")
            else:
                ups_token = token["Token"]

                inquiry_number = tracking
                # Generate url for UPS Tracking endpoint
                url = getenv("UPS_URL") + "api/track/v1/details/" + inquiry_number

                # Default query parameters
                query = {
                    "locale": "en_US",
                    "returnSignature": "true",
                    "returnMilestones": "false",
                    "returnPOD": "true",
                }

                # Authorization Headers
                headers = {
                    "transId": str(uuid.uuid4()),
                    "transactionSrc": "testing",
                    "Authorization": "Bearer " + ups_token,
                }

                response = requests.get(url, headers=headers, params=query)

                data = response.json()

                shipment_response = data

        except Exception as e:
            self.LOG.error("get_shipment: error={}".format(e))
            self.LOG.info("Exception when get_shipment!")
            return shipment_response

        # output token
        self.LOG.info("get_shipment: get_shipment={}".format(str(shipment_response)))
        self.LOG.info("get_shipment: END")
        return shipment_response


# UNIT TESTING


def main():
    return


if __name__ == "__main__":
    main()
