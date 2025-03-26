#!/usr/bin/env python3.7
import re
import time
import jwt
from datetime import datetime, timedelta
from pytz import timezone
import requests
from pydoc import locate
import pytz
import os
import ast
from cryptography.fernet import Fernet
from azure.storage.fileshare import (
    generate_account_sas as generate_account_fileshare_sas,
    ResourceTypes as FileshareResourceTypes,
    AccountSasPermissions as FileshareAccountSasPermissions,
)
from azure.storage.blob import (
    generate_account_sas as generate_account_blob_sas,
    ResourceTypes as BlobResourceTypes,
    AccountSasPermissions as BlobAccountSasPermissions,
)
from .constants import Statuses

from dotenv import load_dotenv

load_dotenv()

from .employee_pull import Employee
from .verification_pull import Verification
from .token_config import TokenConfig
from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .endpoint_pull import Endpoints


class Token(TokenConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        TokenConfig.__init__(self, sql_config)

        self.employee = Employee()

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # Generates a Bearer Token for Carbon API using the environment file
    # input: EmployeeID
    # output: token on success, {} on error
    def create_carbon_api_token(self, verification: Verification) -> dict:
        try:
            self.LOG.info("create_carbon_api_token")

            # Set Client_ID and Client_Secret from environment
            client_id = os.getenv("CARBON_CLIENT_ID")
            client_secret = os.getenv("CARBON_CLIENT_SECRET")

            # generate jwt token that lasts 1 hour
            jwt_contents = {"iss": client_id, "exp": int(time.time() + 60 * 60)}

            # sign & encode token with client secret
            encoded_jwt = jwt.encode(jwt_contents, client_secret, algorithm="RS256")

            # Versions of pyjwt before v2.0.0 return bytes
            if isinstance(encoded_jwt, bytes):
                encoded_jwt = encoded_jwt.decode("utf-8")

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_token,
                        (
                            "Carbon",
                            encoded_jwt,
                            verification.get_verification(),
                            None,
                            None,
                            6,
                        ),
                    )  # 6 is the key for carbon
                    if len(sql.table) != 0:
                        token = sql.table[0]
                    else:
                        raise Exception(
                            "An Error occured with the Create Carbon Token Query"
                        )
                else:
                    raise Exception("Invalid employee ID")

            # output tokenID
            return token

        except Exception as e:
            self.LOG.error("create_carbon_api_token: error={}".format(e))
            self.LOG.info("Exception when creating carbon token!")
            return {}

    # Returns Active Bearer Tokens for Carbon. Generates a new token if no active token is found
    # input: EmployeeID
    # output: token on success, {} on error
    def get_carbon_tokens(self, verification: Verification) -> dict:
        try:
            self.LOG.info(f"get_carbon_tokens: verification={verification}")

            token = {}

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.get_token_without_account, (6)
                    )  # 6 is the type ID for carbon tokens

                    if len(sql.table) != 0:
                        # Initialize pytz utc time zone
                        utc = pytz.utc
                        # Initialize pytz EST/EDT time zone
                        eastern = timezone("US/Eastern")
                        # Create datetime from Created time
                        created_time = sql.table[0]["Created"]
                        # Convert Created_time to UTC
                        utc_time = eastern.localize(created_time).astimezone(utc)
                        # Get time -1 hour
                        time_minus_1_hour = datetime.now() - timedelta(hours=1)
                        utc_minus_1_hour = (time_minus_1_hour).astimezone(utc)

                        if utc_time > utc_minus_1_hour:
                            token = sql.table[0]
                        else:
                            self.LOG.info("Tokens are expired, generating new token")
                            token = self.create_carbon_api_token(verification)
                    else:
                        token = self.create_carbon_api_token(verification)

        except Exception as e:
            self.LOG.error("get_carbon_tokens: error={}".format(e))
            self.LOG.info("get_carbon_tokens: END")
            return {}

        self.LOG.info("get_carbon_tokens: tokens={}".format(len(token)))
        self.LOG.info("get_carbon_tokens: END")
        return token  # no error

    def create_azure_blob_token(
        self,
        verification: Verification,
        storage_key: str = "PHASE_STORAGE_KEY_1",
        account_name: str = "PHASE_STORAGE_NAME_1",
        service: bool = True,
        container: bool = True,
        object: bool = True,
        read: bool = True,
        write: bool = True,
        delete: bool = False,
        list: bool = True,
        add: bool = False,
        create: bool = True,
        update: bool = False,
        process: bool = False,
        delete_previous_version: bool = False,
        hours: int = 4,
    ) -> dict:
        try:
            self.LOG.info("create_azure_blob_token")

            token = []

            # Set storage_key from environment
            storage_key = os.getenv(storage_key)
            account_name = os.getenv(account_name)

            # generate SAS token that lasts 4 hours
            sas_token = generate_account_blob_sas(
                account_name=account_name,
                account_key=storage_key,
                resource_types=BlobResourceTypes(
                    service=service, container=container, object=object
                ),
                permission=BlobAccountSasPermissions(
                    read=read,
                    write=write,
                    delete=delete,
                    list=list,
                    add=add,
                    create=create,
                    update=update,
                    process=process,
                    delete_previous_version=delete_previous_version,
                ),
                expiry=datetime.utcnow() + timedelta(hours=hours),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_token,
                        (
                            "Azure",
                            sas_token,
                            verification.get_verification(),
                            storage_key,
                            account_name,
                            5,
                        ),  # 5 is the ID for the blob token
                    )
                    if len(sql.table) != 0:
                        token = sql.table[0]
                    else:
                        raise Exception(
                            "An Error occured with the insert_azure_token Query"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_azure_blob_token: error={}".format(e))
            self.LOG.info("Exception when creating carbon token!")
            return {}

        # output token
        self.LOG.info("create_azure_blob_token: tokens={}".format(str(token)))
        self.LOG.info("create_azure_blob_token: END")
        return token

    # Generates a SAS token for Azure API using the environment file
    # input: EmployeeID
    # output: token on success, {} on error
    def create_azure_fileshare_token(
        self,
        verification: Verification,
        storage_key: str = "PHASE_STORAGE_KEY_1",
        account_name: str = "PHASE_STORAGE_NAME_1",
        service: bool = True,
        container: bool = True,
        object: bool = True,
        read: bool = True,
        write: bool = True,
        delete: bool = False,
        list: bool = True,
        add: bool = False,
        create: bool = True,
        update: bool = False,
        process: bool = False,
        delete_previous_version: bool = False,
        hours: int = 4,
    ) -> dict:
        try:
            self.LOG.info("create_azure_fileshare_token: BEGIN")

            token = []

            # Set storage_key from environment
            storage_key = os.getenv(storage_key)
            account_name = os.getenv(account_name)

            # generate SAS token that lasts 4 hours
            sas_token = generate_account_fileshare_sas(
                account_name=account_name,
                account_key=storage_key,
                resource_types=FileshareResourceTypes(
                    service=service, container=container, object=object
                ),
                permission=FileshareAccountSasPermissions(
                    read=read,
                    write=write,
                    delete=delete,
                    list=list,
                    add=add,
                    create=create,
                    update=update,
                    process=process,
                    delete_previous_version=delete_previous_version,
                ),
                expiry=datetime.utcnow() + timedelta(hours=hours),
                start=datetime.utcnow() - timedelta(minutes=1),
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_token,
                        (
                            "Azure",
                            sas_token,
                            verification.get_verification(),
                            storage_key,
                            account_name,
                            4,
                        ),  # 4 is the ID for the account token
                    )
                    if len(sql.table) != 0:
                        token = sql.table[0]
                    else:
                        raise Exception(
                            "An Error occured with the insert_azure_token Query"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_azure_fileshare_token: error={}".format(e))
            self.LOG.info("Exception when creating azure token!")
            return {}

        # output token
        self.LOG.info("create_azure_fileshare_token: tokens={}".format(str(token)))
        self.LOG.info("create_azure_fileshare_token: END")
        return token

    # Returns Active Fileshare SAS Token for Azure. Generates a new token if no active token is found
    # input: EmployeeID
    # output: token on success, {} on error
    def get_azure_fileshare_token(
        self,
        verification: Verification,
        storage_key: str = "PHASE_STORAGE_KEY_1",
        account_name: str = "PHASE_STORAGE_NAME_1",
    ) -> dict:
        try:
            self.LOG.info(f"get_azure_fileshare_token: verification={verification}")

            token = {}

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.get_token,
                        (
                            os.getenv(storage_key),
                            os.getenv(account_name),
                            4,
                        ),  # 4 is the id for fileshare token type
                    )

                    if len(sql.table) != 0:
                        # Initialize pytz utc time zone
                        utc = pytz.utc
                        # Initialize pytz EST/EDT time zone
                        eastern = timezone("US/Eastern")
                        # Create datetime from Created time
                        created_time = sql.table[0]["Created"]
                        # Convert Created_time to UTC
                        utc_time = eastern.localize(created_time).astimezone(utc)
                        # Get time -4 hours
                        time_minus_4_hours = datetime.now() - timedelta(hours=4)
                        utc_minus_4_hours = (time_minus_4_hours).astimezone(utc)

                        # Check if Created date returned is within the last 4 hours
                        if utc_time > utc_minus_4_hours:
                            token = sql.table[0]
                        else:
                            self.LOG.info("Tokens are expired, generating new token")
                            token = self.create_azure_fileshare_token(
                                verification,
                                storage_key=storage_key,
                                account_name=account_name,
                            )
                    else:
                        token = self.create_azure_fileshare_token(
                            verification,
                            storage_key=storage_key,
                            account_name=account_name,
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("get_azure_fileshare_token: error={}".format(e))
            self.LOG.info("get_azure_fileshare_token: END")
            return {}

        self.LOG.info("get_azure_fileshare_token: token={}".format(str(token)))
        self.LOG.info("get_azure_fileshare_token: END")
        return token  # no error

    # Returns Active Blob SAS Token for Azure. Generates a new token if no active token is found
    # input: EmployeeID
    # output: token on success, {} on error
    def get_azure_blob_token(
        self,
        verification: Verification,
        storage_key: str = "PHASE_STORAGE_KEY_1",
        account_name: str = "PHASE_STORAGE_NAME_1",
    ) -> dict:
        try:
            self.LOG.info(f"get_azure_blob_token: employee={verification}")

            token = {}

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.get_token,
                        (
                            os.getenv(storage_key),
                            os.getenv(account_name),
                            5,
                        ),  # 5 is the id for fileshare token type
                    )

                    if len(sql.table) != 0:
                        # Initialize pytz utc time zone
                        utc = pytz.utc
                        # Initialize pytz EST/EDT time zone
                        eastern = timezone("US/Eastern")
                        # Create datetime from Created time
                        created_time = sql.table[0]["Created"]
                        # Convert Created_time to UTC
                        utc_time = eastern.localize(created_time).astimezone(utc)
                        # Get time -4 hours
                        time_minus_4_hours = datetime.now() - timedelta(hours=4)
                        utc_minus_4_hours = (time_minus_4_hours).astimezone(utc)

                        # Check if Created date returned is within the last 4 hours
                        if utc_time > utc_minus_4_hours:
                            token = sql.table[0]
                        else:
                            self.LOG.info("Tokens are expired, generating new token")
                            token = self.create_azure_blob_token(
                                verification,
                                storage_key=storage_key,
                                account_name=account_name,
                            )
                    else:
                        token = self.create_azure_blob_token(
                            verification,
                            storage_key=storage_key,
                            account_name=account_name,
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("get_azure_blob_token: error={}".format(e))
            self.LOG.info("get_azure_blob_token: END")
            return {}

        self.LOG.info("get_azure_blob_token: token={}".format(str(token)))
        self.LOG.info("get_azure_blob_token: END")
        return token  # no error

    def get_tokens_by_token(self, token: str) -> list:
        try:
            self.LOG.info(f"get_tokens_by_token: token={token}")

            info = []

            # NEED TO RESET USER IN CONFIG
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_tokens_info_by_token, (token))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception("An Error occured with get_tokens_info_by_token")
        except Exception as e:
            self.LOG.error("get_tokens_by_token: error={}".format(e))
            self.LOG.info("get_tokens_by_token: END")
            return []

        self.LOG.info("get_tokens_by_token: tokens={}".format(str(info)))
        self.LOG.info("get_tokens_by_token: END")
        return info  # no error

    # insert token
    # input: company, token, verification
    # success: token id
    # fail: -1
    def create_token(self, company: str, token: str, verification: Verification) -> int:
        try:
            self.LOG.info("create_token")

            info = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_token,
                        (
                            company,
                            token,
                            verification.get_verification(),
                            None,
                            None,
                            4,
                        ),  # 4 is the ID for the Account token
                    )
                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception("An Error occured with the insert token Query")
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_token: error={}".format(e))
            self.LOG.info("create_token: END")
            return -1

        # output token
        self.LOG.info("create_token: tokens={}".format(info))
        self.LOG.info("create_token: END")
        return info

    def update_token_statuses(
        self, tokenIDs: list, status: int, verification: Verification
    ) -> list:
        try:
            self.LOG.info(f"update_token_status: tokenIDs={tokenIDs} status={status}")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    tokenIDs_string = ",".join(tokenIDs)
                    sql.execute(
                        self.update_token_status_by_token_ids,
                        (status, tokenIDs_string),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception("An Error occured with update_token_status")
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_token_status: error={}".format(e))
            self.LOG.info("update_token_status: END")
            return []

        self.LOG.info("update_token_status: info={}".format(info))
        self.LOG.info("update_token_status: END")
        return info

    # Retrieve account connection information associated with token
    # input: TokenID
    # output: SQL
    def get_sql_account_by_token(self, tokenID: int) -> dict:
        try:
            self.LOG.info(f"get_sql_account_by_token: tokenID={tokenID}")

            info = {}

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_sql_info_by_token, (tokenID))
                if len(sql.table) != 0:
                    info = sql.table[0]
                else:
                    raise Exception("An Error occured with get_sql_info_by_token")
        except Exception as e:
            self.LOG.error("get_sql_account_by_token: error={}".format(e))
            self.LOG.info("get_sql_account_by_token: END")
            return {}

        self.LOG.info("get_sql_account_by_token: tokens={}".format(str(info)))
        self.LOG.info("get_sql_account_by_token: END")
        return info  # no error

    # asserts the typing for validation
    def __validate_typing(self, value: object, typing: str) -> object:
        try:
            self.LOG.info("validate_typing: value={} typing={}".format(value, typing))

            # define new value
            new_value = None

            # replaces string lists with bracketed string list for literal eval
            if (
                type(value) == str
                and typing == "list"
                and "[" not in value
                and "]" not in value
            ):
                value = "[{}]".format(value)
            # replaces bool values with string wrapped bool value for literal eval
            elif typing == "bool":
                value = str(value).capitalize()
            elif typing == "str" and value != "None":
                new_value = value
            if new_value is None:
                try:
                    # literal eval to remove nefarious input and to invoke specific types
                    new_value = ast.literal_eval(value)
                except (SyntaxError, ValueError) as e:
                    # default must be a string
                    new_value = value

            # convert to desired type
            if new_value is not None:
                new_value = locate(typing)(new_value)

        except Exception as e:
            self.LOG.error("validate_typing: error={}".format(e))
            self.LOG.info("validate_typing: END")
            return None

        self.LOG.info("validate_typing: new_value={}".format(new_value))
        self.LOG.info("validate_typing: END")
        return new_value  # no error

    # # verify token and endpoint permission
    # input: Token, EndpointID, Params
    # output: Result
    def token_verification(
        self,
        token: str | None,
        endpointID: int,
        params: dict | None = None,
        files: dict | None = None,
        bypass_credentials: bool = False,
        bypass_check: bool = False,
    ) -> tuple[dict, Verification, SQLConfig, int]:
        try:
            self.LOG.info(
                "token_verification: token={} endpointID={} params={} files={}".format(
                    token, endpointID, params, files
                )
            )

            # get injection pattern
            injection_pattern = os.getenv("INJECTION_PATTERN")

            # get default token if None provided
            if token is None:
                token = os.getenv("OWNER_DEFAULT_TOKEN")
                self.LOG.info(
                    "token_verification: token updated to default value '{}'".format(
                        token
                    )
                )

            # init info dictionary
            final_params = {}
            final_files = {}
            # define verification status
            verification = None
            # define sql object
            sql_config = SQLConfig
            # define status
            status = 500

            # get tokenID from token
            token_obj = self.get_tokens_by_token(token)
            if len(token_obj) == 0:
                raise Exception(
                    "The provided token '{}' fails to have a match within the token list!".format(
                        token
                    )
                )
            tokenID = token_obj[0]["ID"]

            # Get SQL User information
            sql_user = self.get_sql_account_by_token(tokenID)
            if len(sql_user) == 0:
                status = 403
                raise Exception(f"No Valid SQL User Associated with TokenID {tokenID}")

            # create new sql object from given token if bypass is not enabled
            if bypass_credentials is False:
                # define overload class for sql_config
                class OverrideSQLConfig:
                    # CONSTRUCTOR
                    # A OVERLOAD EXISTS WITHIN TOKEN_PULL.PY
                    def __init__(self) -> None:
                        # globals
                        self.server = os.getenv("SQL_SERVER")
                        self.database = os.getenv("SQL_DATABASE")
                        crypto_key = os.getenv("CRYPTO_KEY")
                        # Create Fernet object with stored crypto key
                        fernet = Fernet(crypto_key.encode("utf-8"))
                        # Decode decrypted sql password retrieved
                        self.password = fernet.decrypt(sql_user["Password"]).decode()
                        self.username = sql_user["Username"]
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
                        self,
                        server=None,
                        database=None,
                        username=None,
                        password=None,
                        driver=None,
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

                sql_config = OverrideSQLConfig

            # verify endpoint
            endpoint_params = []
            token_params = []
            with Endpoints() as end:
                # see if token has access to endpoint
                result = end.get_endpoint_by_token_and_endpoint(endpointID, tokenID)
                if len(result) == 0:
                    status = 403
                    raise Exception(
                        "Token '{}' does not have permission to access the given endpoint '{}'!".format(
                            token, endpointID
                        )
                    )

                # only do param verification if params is not None
                if params is not None:

                    # get endpoint params allocation from the token
                    token_params = end.get_endpoint_params_by_token_and_endpoint(
                        endpointID, tokenID
                    )

                    # get endpoint params from the endpoint
                    endpoint_params = end.get_params_by_endpoint_ID(endpointID)

                    # generate final_params
                    for endpoint_param in endpoint_params:
                        # find a matching param from the token
                        match = None
                        for i, token_param in enumerate(token_params):
                            if endpoint_param["ParamID"] == token_param["ParamID"]:
                                # what to do if the token_param status is inactiev
                                if token_param["Status"] == Statuses.INACTIVE.value:
                                    # if a value was not provided and not found in params then use default value from endpoint param
                                    if endpoint_param["DefaultValue"] is not None:
                                        final_params[endpoint_param["ParamID"]] = (
                                            self.__validate_typing(
                                                endpoint_param["DefaultValue"],
                                                token_param["PythonType"],
                                            )
                                        )
                                    # else set it to none
                                    else:
                                        final_params[endpoint_param["ParamID"]] = None

                                # if it is active then begin checking values
                                if token_param["Status"] == Statuses.ACTIVE.value:
                                    # if param is in files then ignore the usual checks and just set up final_files
                                    if (
                                        files is not None
                                        and endpoint_param["Name"] in files.keys()
                                    ):
                                        final_files[endpoint_param["ParamID"]] = files[
                                            endpoint_param["Name"]
                                        ]
                                    # if value overwite is not allowed then force usage of value
                                    elif token_param["Locked"] is True:
                                        final_params[endpoint_param["ParamID"]] = (
                                            self.__validate_typing(
                                                token_param["Value"],
                                                token_param["PythonType"],
                                            )
                                        )
                                    # if value can be overwritten and the param exists
                                    elif endpoint_param["Name"] in params.keys():
                                        final_params[endpoint_param["ParamID"]] = (
                                            self.__validate_typing(
                                                params[endpoint_param["Name"]],
                                                token_param["PythonType"],
                                            )
                                        )
                                    # if a value was provided by the token and not found in params
                                    elif token_param["Value"] is not None:
                                        final_params[endpoint_param["ParamID"]] = (
                                            self.__validate_typing(
                                                token_param["Value"],
                                                token_param["PythonType"],
                                            )
                                        )
                                    # if a value was not provided and not found in params then use default value from endpoint param
                                    elif endpoint_param["DefaultValue"] is not None:
                                        final_params[endpoint_param["ParamID"]] = (
                                            self.__validate_typing(
                                                endpoint_param["DefaultValue"],
                                                token_param["PythonType"],
                                            )
                                        )
                                    # else set it to none
                                    else:
                                        final_params[endpoint_param["ParamID"]] = None

                                # we found a match leave
                                match = i
                                break

                        # no matching setup for the given param ID
                        if match is None:
                            status = 403
                            raise Exception(
                                "The following endpoint '{}' has a parameter '{}' that fails to have a matching token endpoint param link!".format(
                                    endpoint_param["EndpointID"],
                                    endpoint_param["ParamID"],
                                )
                            )

                        # remove this token_param from the list
                        if match is not None:
                            token_params.pop(i)

                    # check to make sure we have all token_params popped, aka all were matched
                    if len(token_params) > 0:
                        status = 403
                        raise Exception(
                            "Some token params defined for the given token '{}' failed to have matching endpoints params! {}".format(
                                token, token_params
                            )
                        )

            # remove tuples and convert to list
            for paramID in final_params:
                if type(final_params[paramID]) == tuple:
                    final_params[paramID] = list(final_params[paramID])

            # check params for injections
            for paramID in final_params:
                match = re.search(injection_pattern, str(final_params[paramID]).lower())
                if match is not None:
                    raise Exception("Invalid input found, aborting verification!")

            # Import Verification
            verification = Verification()
            verification.import_verification_by_id(
                sql_user["OwnerVerificationID"], bypass_check=bypass_check
            )
            # check verification
            if verification.get_verification() == -1:
                status = 403
                raise Exception("Failed to Authorize user!")

            # If we made it here that means function worked properly, set status to 200
            status = 200

        except Exception as e:
            self.LOG.error("token_verification: error={}".format(e))
            self.LOG.info("token_verification: END")
            return {}, None, SQLConfig, status, {}

        self.LOG.info("token_verification: final_params={}".format(final_params))
        self.LOG.info("token_verification: final_files={}".format(final_files))
        self.LOG.info("token_verification: END")
        return final_params, verification, sql_config, status, final_files

    def get_token_endpoint_links(self) -> list:
        try:
            self.LOG.info("get_token_endpoint_links: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_token_endpoint_links)
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception("An Error occured with get_token_endpoint_links")

        except Exception as e:
            self.LOG.error("get_token_endpoint_links: error={}".format(e))
            self.LOG.info("get_token_endpoint_links: END")
            return []

        self.LOG.info("get_token_endpoint_links: info={}".format(len(info)))
        self.LOG.info("get_token_endpoint_links: END")
        return info

    def create_token_endpoint_links(
        self, tokenID: int, endpointIDs: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info("create_token_endpoint_links: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    endpointIDs_string = ",".join(endpointIDs)
                    sql.execute(
                        self.insert_token_endpoint_links,
                        (tokenID, endpointIDs_string),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "An Error occured with create_token_endpoint_links"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_token_endpoint_links: error={}".format(e))
            self.LOG.info("create_token_endpoint_links: END")
            return []

        self.LOG.info("create_token_endpoint_links: info={}".format(info))
        self.LOG.info("create_token_endpoint_links: END")
        return info

    def update_token_endpoint_link_statuses(
        self, linkIDs: list, status: int, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                f"update_token_endpoint_link_statuses: linkIDs={linkIDs} status={status}"
            )

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    linkIDs_string = ",".join((map(str, linkIDs)))
                    sql.execute(
                        self.update_token_endpoint_links_statuses_by_ids,
                        (status, linkIDs_string),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "An Error occured with update_token_endpoint_link_statuses"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_token_endpoint_link_statuses: error={}".format(e))
            self.LOG.info("update_token_endpoint_link_statuses: END")
            return []

        self.LOG.info("update_token_endpoint_link_statuses: info={}".format(info))
        self.LOG.info("update_token_endpoint_link_statuses: END")
        return info

    def get_token_endpoint_param_links(self, token: str) -> list:
        try:
            self.LOG.info("get_token_endpoint_param_links: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_token_endpoint_param_links_by_token,
                    (token,),
                )
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "An Error occured with get_token_endpoint_param_links"
                    )

        except Exception as e:
            self.LOG.error("get_token_endpoint_param_links: error={}".format(e))
            self.LOG.info("get_token_endpoint_param_links: END")
            return []

        self.LOG.info("get_token_endpoint_param_links: info={}".format(len(info)))
        self.LOG.info("get_token_endpoint_param_links: END")
        return info

    def create_token_endpoint_param_links(
        self,
        verification: Verification,
        endpointParamLinks: list,
    ) -> list:
        try:
            self.LOG.info("create_token_endpoint_param_links: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    tokenID = endpointParamLinks[0]["tokenID"]
                    endpointParamLinkIDs = [
                        str(item["endpointParamLinkID"]) for item in endpointParamLinks
                    ]
                    values = [
                        "None" if item["value"] is None else item["value"]
                        for item in endpointParamLinks
                    ]
                    lockeds = [
                        "1" if item["locked"] == True else "0"
                        for item in endpointParamLinks
                    ]

                    endpointParamLinkIDs_string = ",".join(endpointParamLinkIDs)
                    values_string = ",".join(values)
                    lockeds_string = ",".join(lockeds)
                    sql.execute(
                        self.insert_token_endpoint_param_links,
                        (
                            tokenID,
                            endpointParamLinkIDs_string,
                            values_string,
                            lockeds_string,
                            verification.get_verification(),
                        ),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "An Error occured with create_token_endpoint_param_links"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_token_endpoint_param_links: error={}".format(e))
            self.LOG.info("create_token_endpoint_param_links: END")
            return []

        self.LOG.info("create_token_endpoint_param_links: info={}".format(info))
        self.LOG.info("create_token_endpoint_param_links: END")
        return info

    def update_token_endpoint_param_link(
        self, id: int, value: str, locked: bool, verification: Verification
    ) -> list:
        try:
            self.LOG.info("update_token_endpoint_param_link: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_token_endpoint_param_links_by_ids,
                        (value, locked, id),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "An Error occured with update_token_endpoint_param_link"
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("update_token_endpoint_param_link: error={}".format(e))
            self.LOG.info("update_token_endpoint_param_link: END")
            return []

        self.LOG.info("update_token_endpoint_param_link: info={}".format(info))
        self.LOG.info("update_token_endpoint_param_link: END")
        return info

    def update_token_endpoint_param_link_statuses(
        self, linkIDs: list, status: int, verification: Verification
    ) -> list:
        try:
            self.LOG.info("update_token_endpoint_param_link_statuses: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    linkIDs_string = ",".join((map(str, linkIDs)))
                    sql.execute(
                        self.update_token_endpoint_param_links_statuses_by_ids,
                        (status, linkIDs_string),
                    )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "An Error occured with update_token_endpoint_param_link_statuses"
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error(
                "update_token_endpoint_param_link_statuses: error={}".format(e)
            )
            self.LOG.info("update_token_endpoint_param_link_statuses: END")
            return []

        self.LOG.info("update_token_endpoint_param_link_statuses: info={}".format(info))
        self.LOG.info("update_token_endpoint_param_link_statuses: END")
        return info

    # Generates a Bearer token for UPS API using the environment file
    # input: EmployeeID
    # output: token on success, {} on error
    def create_ups_token(
        self,
        verification: Verification,
    ) -> dict:
        try:
            self.LOG.info("create_ups_token: BEGIN")

            token = []

            url = os.getenv("UPS_URL") + "security/v1/oauth/token"

            # Payload for UPS token creation
            payload = {"grant_type": "client_credentials"}

            # Required headers for UPS token creation
            headers = {
                "Content-Type": "application/x-www-form-urlencoded",
                "x-merchant-id": os.getenv("UPS_MERCHANT_ID"),
            }

            # UPS Token Creation Response
            response = requests.post(
                url,
                data=payload,
                headers=headers,
                auth=(os.getenv("UPS_CLIENT_ID"), os.getenv("UPS_CLIENT_SECRET")),
            )

            self.LOG.info(response)
            data = response.json()

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_token,
                        (
                            "UPS",
                            data["access_token"],
                            verification.get_verification(),
                            None,
                            None,
                            7,
                        ),  # 7 is the ID for the UPS token type
                    )
                    if len(sql.table) != 0:
                        token = sql.table[0]
                    else:
                        raise Exception("An Error occured with the insert_token Query")
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_ups_token: error={}".format(e))
            self.LOG.info("Exception when creating ups token!")
            return {}

        # output token
        self.LOG.info("create_ups_token: tokens={}".format(str(token)))
        self.LOG.info("create_ups_token: END")
        return token

    # Returns Active UPS Token. Generates a new token if no active token is found
    # input: EmployeeID
    # output: token on success, {} on error
    def get_UPS_token(
        self,
        verification: Verification,
    ) -> dict:
        try:
            self.LOG.info(f"get_UPS_token: verification={verification}")

            token = {}

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.get_token,
                        (
                            None,
                            None,
                            7,
                        ),  # 7 is the id for UPS token type
                    )

                    if len(sql.table) != 0:
                        # Initialize pytz utc time zone
                        utc = pytz.utc
                        # Initialize pytz EST/EDT time zone
                        eastern = timezone("US/Eastern")
                        # Create datetime from Created time
                        created_time = sql.table[0]["Created"]
                        # Convert Created_time to UTC
                        utc_time = eastern.localize(created_time).astimezone(utc)
                        # Get time -3 hours
                        time_minus_3_hours = datetime.now() - timedelta(hours=3)
                        utc_minus_3_hours = (time_minus_3_hours).astimezone(utc)

                        # Check if Created date returned is within the last 3 hours
                        if utc_time > utc_minus_3_hours:
                            token = sql.table[0]
                        else:
                            self.LOG.info("Tokens are expired, generating new token")

                            token = self.create_ups_token(
                                verification,
                            )
                    else:
                        token = self.create_ups_token(
                            verification,
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("get_ups_token: error={}".format(e))
            self.LOG.info("get_ups_token: END")
            return {}

        self.LOG.info("get_ups_token: token={}".format(str(token)))
        self.LOG.info("get_ups_token: END")
        return token  # no error


# Unit Testing
def main():
    token = Token()

    token.get_carbon_tokens("100")

    return


if __name__ == "__main__":
    main()
