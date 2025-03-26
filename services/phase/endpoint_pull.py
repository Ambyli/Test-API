#!/usr/bin/env python3.7

from typing import List, Dict

from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .endpoint_config import EndpointConfig
from .verification_pull import Verification


class Endpoints(EndpointConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        EndpointConfig.__init__(self, sql_config)

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    def get_endpoints_by_token(self, tokenID: int) -> list:
        try:
            self.LOG.info("get_endpoints_by_token: tokenID={}".format(tokenID))

            info = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_token_endpoints_by_token, (tokenID,))

                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_token_endpoint_by_token query!"
                    )

        except Exception as e:
            self.LOG.error("get_endpoints_by_token: error={}".format(e))
            self.LOG.info("get_endpoints_by_token: END")
            return []  # other error

        self.LOG.info("get_endpoints_by_token: endpoints={}".format(len(info)))
        self.LOG.info("get_endpoints_by_token: END")
        return info

    def get_endpoint_by_token_and_endpoint(self, endpointID: int, tokenID: int) -> list:
        try:
            self.LOG.info(
                "get_endpoint_by_token_and_endpoint: endpointID={} tokenID={}".format(
                    endpointID, tokenID
                )
            )

            info = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_token_endpoint_by_token_and_endpoint,
                    (
                        endpointID,
                        tokenID,
                    ),
                )

                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_token_endpoint_by_token_and_endpoint query!"
                    )

        except Exception as e:
            self.LOG.error("get_endpoint_by_token_and_endpoint: error={}".format(e))
            self.LOG.info("get_endpoint_by_token_and_endpoint: END")
            return []  # other error

        self.LOG.info(
            "get_endpoint_by_token_and_endpoint: endpoints={}".format(len(info))
        )
        self.LOG.info("get_endpoint_by_token_and_endpoint: END")
        return info

    def get_endpoint_params_by_token_and_endpoint(
        self, endpointID: int, tokenID: int
    ) -> list:
        try:
            self.LOG.info(
                "get_endpoint_params_by_token_and_endpoint: endpointID={} tokenID={}".format(
                    endpointID, tokenID
                )
            )

            info = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.get_token_endpoint_params_by_token_and_endpoint,
                    (
                        tokenID,
                        endpointID,
                    ),
                )

                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_token_endpoint_params_by_token_and_endpoint query!"
                    )

        except Exception as e:
            self.LOG.error(
                "get_endpoint_params_by_token_and_endpoint: error={}".format(e)
            )
            self.LOG.info("get_endpoint_params_by_token_and_endpoint: END")
            return []  # other error

        self.LOG.info(
            "get_endpoint_params_by_token_and_endpoint: endpoints={}".format(len(info))
        )
        self.LOG.info("get_endpoint_params_by_token_and_endpoint: END")
        return info

    def get_all_endpoints(self) -> list:
        try:
            self.LOG.info("get_all_endpoints".format())

            info = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_endpoints)

                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_endpoints query!"
                    )

        except Exception as e:
            self.LOG.error("get_all_endpoints: error={}".format(e))
            self.LOG.info("get_all_endpoints: END")
            return []  # other error

        self.LOG.info("get_all_endpoints: endpoints={}".format(len(info)))
        self.LOG.info("get_all_endpoints: END")
        return info

    # get endpoint by id
    # input: endpoint id
    # output: endpoint on success, -1 on error
    def get_endpoint_by_id(self, endpointID: int) -> object:
        try:
            self.LOG.info("get_endpoint_by_id: BEGIN")

            info = -1
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_endpoint_by_endpoint_id, (endpointID,))
                if len(sql.table) != 0:
                    info = sql.table[0]
                else:
                    raise Exception(
                        "No results found with the get_endpoint_by_id query!"
                    )

        except Exception as e:
            self.LOG.error("get_endpoint_by_id: error={}".format(e))
            self.LOG.info("get_endpoint_by_id: END")
            return -1  # other error

        self.LOG.info("get_endpoint_by_id: vendors={}".format(info))
        self.LOG.info("get_endpoint_by_id: END")
        return info  # no error

    # get endpoint by name
    # input: endpoint id
    # output: endpoint on success, -1 on error
    def get_endpoint_by_name(self, endpointName: str) -> dict:
        try:
            self.LOG.info("get_endpoint_by_name: BEGIN")

            info = {}
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_endpoint_by_endpoint_name, (endpointName,))
                if len(sql.table) != 0:
                    info = sql.table[0]
                else:
                    raise Exception(
                        "No results found with the get_endpoint_by_name query!"
                    )

        except Exception as e:
            self.LOG.error("get_endpoint_by_name: error={}".format(e))
            self.LOG.info("get_endpoint_by_name: END")
            return {}  # other error

        self.LOG.info("get_endpoint_by_name: vendors={}".format(info))
        self.LOG.info("get_endpoint_by_name: END")
        return info  # no error

    # get endpoints by employeeID
    # input: endpoint id
    # output: endpoint on success, -1 on error
    def get_endpoints_by_employeeID(self, employeeID: int) -> list:
        try:
            self.LOG.info("get_endpoints_by_employeeID: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_endpoints_by_employee_id, (employeeID,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "An error occurred with the get_endpoints_by_employeeID query!"
                    )

        except Exception as e:
            self.LOG.error("get_endpoints_by_employeeID: error={}".format(e))
            self.LOG.info("get_endpoints_by_employeeID: END")
            return []  # other error

        self.LOG.info("get_endpoints_by_employeeID: vendors={}".format(len(info)))
        self.LOG.info("get_endpoints_by_employeeID: END")
        return info  # no error

    # get endpoints by token
    # input: endpoint id
    # output: endpoint on success, -1 on error
    def get_endpoints_by_token(self, token: str) -> list:
        try:
            self.LOG.info("get_endpoints_by_employeeID: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_endpoints_by_employee_token, (token,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "An error occurred with the get_endpoints_by_token query!"
                    )

        except Exception as e:
            self.LOG.error("get_endpoints_by_token: error={}".format(e))
            self.LOG.info("get_endpoints_by_token: END")
            return []  # other error

        self.LOG.info("get_endpoints_by_token: vendors={}".format(len(info)))
        self.LOG.info("get_endpoints_by_token: END")
        return info  # no error

    # create new endpoint
    # input:  endpoints or name, description, tokenCheck
    # output: ID on success
    def create_new_endpoint(
        self,
        endpoints: list,
        name: str,
        description: str,
        tokenCheck: bool,
        verification: Verification,
    ) -> list:
        try:
            self.LOG.info(
                "create_new_endpoint: endpoints={} name={} description={} tokenCheck={}".format(
                    endpoints, name, description, tokenCheck
                )
            )
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    if endpoints:
                        names = [item["name"] for item in endpoints]
                        descriptions = [item["description"] for item in endpoints]
                        tokenChecks = [
                            "1" if item["tokenCheck"] == True else "0"
                            for item in endpoints
                        ]

                        names_string = ",".join(names)
                        descriptions_string = ",".join(descriptions)
                        tokenChecks_string = ",".join(tokenChecks)

                        sql.execute(
                            self.insert_endpoints,
                            (names_string, descriptions_string, tokenChecks_string),
                        )

                    else:
                        sql.execute(
                            self.insert_endpoint,
                            (name, description, tokenCheck),
                        )

                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "Unable to create new endpoint {}!".format(info)
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("create_new_endpoint: error={}".format(e))
            self.LOG.info("create_new_endpoint: END")
            return []  # other error

        self.LOG.info("create_new_endpoint: entry={}".format(info))
        self.LOG.info("create_new_endpoint: END")
        return info  # no error

    # update endpoint
    # input: name, description, employeeID, id
    # output: ID on success
    def update_endpoint_info(
        self,
        name: str,
        description: str,
        tokenCheck: bool,
        endpointID: int,
        verification: Verification,
    ) -> int:
        try:
            self.LOG.info(
                "update_endpoint: name={} description={} tokenCheck={} endpointID={}".format(
                    name, description, tokenCheck, endpointID
                )
            )
            info = -1
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_endpoint,
                        (name, description, tokenCheck, endpointID),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception("Unable to update endpoint {}!".format(info))
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("update_endpoint: error={}".format(e))
            self.LOG.info("update_endpoint: END")
            return -1  # other error

        self.LOG.info("update_endpoint: entry={}".format(info))
        self.LOG.info("update_endpoint: END")
        return info  # no error

    # update endpoint
    # input: tokenCheck, id
    # output: ID on success
    def update_endpoint_token_check(
        self,
        tokenCheck: bool,
        endpointIDs: list,
        verification: Verification,
    ) -> list:
        try:
            self.LOG.info(
                "update_endpoint_info: tokenCheck={} endpointIDs={}".format(
                    tokenCheck, endpointIDs
                )
            )
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    endpointIDs_string = ",".join(map(str, endpointIDs))
                    sql.execute(
                        self.update_endpoint_token_check_by_ids,
                        (tokenCheck, endpointIDs_string),
                    )

                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "Unable to update endpoint tokenCheck {}!".format(info)
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("update_endpoint_info: error={}".format(e))
            self.LOG.info("update_endpoint_info: END")
            return []  # other error

        self.LOG.info("update_endpoint_info: entry={}".format(info))
        self.LOG.info("update_endpoint_info: END")
        return info  # no error

    # update endpoint status
    # input: status, dashboardID
    # output: ID on success
    def update_endpoints_status(
        self, status: int, endpointIDs: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "update_endpoint_status: status={} endpointIDs={}".format(
                    status, endpointIDs
                )
            )
            info = []
            if len(endpointIDs) > 0:
                with SQL_Pull()(self.sql_config)() as sql:
                    if (
                        isinstance(verification, Verification)
                        and verification.get_verification() != -1
                    ):
                        endpointIDs_string = ",".join(endpointIDs)
                        # update_status
                        sql.execute(
                            self.update_endpoint_status, (status, endpointIDs_string)
                        )

                        if len(sql.table) != 0:
                            info = sql.table
                        else:
                            raise Exception(
                                "Unable to update endpoints status {}!".format(info)
                            )
                    else:
                        raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_endpoint_status: error={}".format(e))
            self.LOG.info("update_endpoint_status: END")
            return []

        self.LOG.info("update_endpoint_status: entry={}".format(info))
        self.LOG.info("update_endpoint_status: END")
        return info  # no error

    # get endpoint params
    def get_endpoint_param_links(
        self,
    ) -> list:
        try:
            self.LOG.info("get_endpoint_param_links: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_endpoint_param_links)
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "An error occurred with the get_endpoint_param_links query!"
                    )

        except Exception as e:
            self.LOG.error("get_endpoint_param_links: error={}".format(e))
            self.LOG.info("get_endpoint_param_links: END")
            return []  # other error

        self.LOG.info("get_endpoint_param_links: endpoint_params={}".format(len(info)))
        self.LOG.info("get_endpoint_param_links: END")
        return info

    # insert endpoint param links
    # input: links for bulk inserted (list of dicts with keys paramID, endpointID, and defaultValue)
    # input: paramID, endpointID, and defaultValue for single inserted.
    def create_endpoint_param_links(
        self,
        links: list,
        paramID: int,
        endpointID: int,
        defaultValue,
        verification: Verification,
    ) -> list:
        try:
            self.LOG.info("create_endpoint_param_links: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    if links is not None:

                        # Extract names and pythonTypes into separate lists
                        paramIDs = [str(item["paramID"]) for item in links]
                        endpointIDs = [str(item["endpointID"]) for item in links]
                        defaultValues = [
                            "" if item["defaultValue"] is None else item["defaultValue"]
                            for item in links
                        ]

                        # Join names and pythonTypes using comma as separator
                        paramIDs_string = ";".join(paramIDs)
                        endpointIDs_string = ";".join(endpointIDs)
                        defaultValues_string = ";".join(defaultValues)
                        sql.execute(
                            self.insert_endpoint_param_links,
                            (paramIDs_string, endpointIDs_string, defaultValues_string),
                        )
                    if paramID is not None and endpointID is not None:
                        sql.execute(
                            self.insert_endpoint_param_link,
                            (paramID, endpointID, defaultValue),
                        )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "An error occurred with the create_endpoint_param_links query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_endpoint_param_links: error={}".format(e))
            self.LOG.info("create_endpoint_param_links: END")
            return []  # other error

        self.LOG.info("create_endpoint_param_links: endpoint_params={}".format(info))
        self.LOG.info("create_endpoint_param_links: END")
        return info

    # update endpoint param links
    # input: links for bulk update (list of dicts with keys defaultValue and linkID)
    # input: defaultValue, linkID for single update.
    def update_endpoint_param_links(
        self,
        links: list,
        defaultValue,
        linkID: int,
        verification: Verification,
    ) -> list:
        try:
            self.LOG.info("update_endpoint_param_links: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    if links is not None:

                        # Extract names and pythonTypes into separate lists
                        linkIDs = [str(item["linkID"]) for item in links]
                        defaultValues = [
                            "" if item["defaultValue"] is None else item["defaultValue"]
                            for item in links
                        ]

                        # Join linkIDs and defaultValues using comma as separator
                        linkIDs_string = ",".join(linkIDs)
                        defaultValues_string = ",".join(defaultValues)
                        sql.execute(
                            self.update_endpoint_param_link_default_values,
                            (linkIDs_string, defaultValues_string),
                        )
                    if linkID is not None:
                        sql.execute(
                            self.update_endpoint_param_link_default_value,
                            (defaultValue, linkID),
                        )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception(
                            "An error occurred with the update_endpoint_param_links query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_endpoint_param_links: error={}".format(e))
            self.LOG.info("update_endpoint_param_links: END")
            return []  # other error

        self.LOG.info("update_endpoint_param_links: endpoint_params={}".format(info))
        self.LOG.info("update_endpoint_param_links: END")
        return info

    # get endpoint params
    def update_endpoint_param_link_statuses(self, linkIDs: list, status: int) -> list:
        try:
            self.LOG.info(
                "update_endpoint_param_link_statuses : BEGIN {}".format(linkIDs)
            )

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                linkIDs_string = ",".join(map(str, linkIDs))
                sql.execute(
                    self.update_endpoint_param_link_statuses_by_link_ids,
                    (status, linkIDs_string),
                )
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "An error occurred with the update_endpoint_param_link_statuses query!"
                    )

        except Exception as e:
            self.LOG.error("update_endpoint_param_link_statuses: error={}".format(e))
            self.LOG.info("update_endpoint_param_link_statuses: END")
            return []  # other error

        self.LOG.info(
            "update_endpoint_param_link_statuses: endpoint_params={}".format(info)
        )
        self.LOG.info("update_endpoint_param_link_statuses: END")
        return info

    # get endpoint params
    def get_params(
        self,
    ) -> list:
        try:
            self.LOG.info("get_params: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_params)
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception("No results found with the get_params query!")

        except Exception as e:
            self.LOG.error("get_params: error={}".format(e))
            self.LOG.info("get_params: END")
            return []  # other error

        self.LOG.info("get_params: endpoint_params={}".format(len(info)))
        self.LOG.info("get_params: END")
        return info

    # get endpoint params by endpoint ID
    def get_params_by_endpoint_ID(self, endpointID: int) -> list:
        try:
            self.LOG.info("get_params_by_endpoint_ID: BEGIN")

            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_endpoint_params_by_endpoint_ID, (endpointID,))
                if len(sql.table) != 0:
                    info = sql.table
                else:
                    raise Exception(
                        "No results found with the get_params_by_endpoint_ID query!"
                    )

        except Exception as e:
            self.LOG.error("get_params_by_endpoint_ID: error={}".format(e))
            self.LOG.info("get_params_by_endpoint_ID: END")
            return []  # other error

        self.LOG.info("get_params_by_endpoint_ID: endpoint_params={}".format(len(info)))
        self.LOG.info("get_params_by_endpoint_ID: END")
        return info

    # # create new endpoint param
    # # input:  endpointID, name
    # # output: ID on success
    # def create_new_endpoint_params(
    #     self,
    #     endpointName: str,
    #     description: str,
    #     params: list,
    #     tokenCheck: bool,
    #     verification: Verification,
    # ) -> list:
    #     try:
    #         self.LOG.info(
    #             "create_new_endpoint_params: endpointName={} description={} params={} tokenCheck={} verification={}".format(
    #                 endpointName, description, params, tokenCheck, verification
    #             )
    #         )
    #         info = []
    #         with SQL_Pull()(self.sql_config)() as sql:
    #             if (
    #                 isinstance(verification, Verification)
    #                 and verification.get_verification() != -1
    #             ):

    #                 sql.execute(
    #                     self.insert_endpoint,
    #                     (endpointName, description, tokenCheck),
    #                 )
    #                 if len(sql.table) != 0:
    #                     endpointID = sql.table[0]["ID"]
    #                     params_string = ",".join(map(str, params))
    #                     sql.execute(
    #                         self.insert_endpoint_params,
    #                         (endpointID, params_string),
    #                     )

    #                     if len(sql.table) != 0:
    #                         info = [
    #                             {"endpointID": endpointID, "paramID": x["ID"]}
    #                             for x in sql.table
    #                         ]
    #                     else:
    #                         raise Exception(
    #                             "Unable to create new Params {}!".format(info)
    #                         )
    #                 else:
    #                     raise Exception(
    #                         "Unable to create new endpoint {}!".format(info)
    #                     )
    #             else:
    #                 raise Exception("Invalid verification!")
    #     except Exception as e:
    #         self.LOG.info("create_new_endpoint_params: error={}".format(e))
    #         self.LOG.info("create_new_endpoint_params: END")
    #         return []  # other error

    #     self.LOG.info("create_new_endpoint_params: entry={}".format(info))
    #     self.LOG.info("create_new_endpoint_params: END")
    #     return info  # no error

    # create new params
    # input:  params or param and name
    # output: IDs on success
    def create_new_params(
        self, params: list, param: str, type: str, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "create_new_params: params={} param={} type={}".format(
                    params, param, type
                )
            )
            info = []
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # if give list of params
                    if params is not None:
                        # Extract names and pythonTypes into separate lists
                        names = [item["name"] for item in params]
                        pythonTypes = [item["pythonType"] for item in params]

                        # Join names and pythonTypes using comma as separator
                        names_string = ",".join(names)
                        pythonTypes_string = ",".join(pythonTypes)
                        sql.execute(
                            self.insert_params,
                            (names_string, pythonTypes_string),
                        )
                    # if give single param
                    if param is not None and type is not None:
                        sql.execute(
                            self.insert_param,
                            (param, type),
                        )
                    if len(sql.table) != 0:
                        info = sql.table
                    else:
                        raise Exception("Unable to create new param {}!".format(info))
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("create_new_params: error={}".format(e))
            self.LOG.info("create_new_params: END")
            return []  # other error

        self.LOG.info("create_new_params: entry={}".format(info))
        self.LOG.info("create_new_params: END")
        return info  # no error

    # update endpoint param
    # input: name, paramID
    # output: ID on success
    def update_param_details(
        self, name: str, pythonType: str, paramID: int, verification: Verification
    ) -> int:
        try:
            self.LOG.info(
                "update_param_details: name={} pythonType={} paramID={}".format(
                    name, pythonType, paramID
                )
            )
            info = -1
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_param,
                        (name, pythonType, paramID),
                    )

                    if len(sql.table) != 0:
                        info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "Unable to update endpoint param {}!".format(info)
                        )
                else:
                    raise Exception("Invalid verification!")
        except Exception as e:
            self.LOG.error("create_new_endpoint_param: error={}".format(e))
            self.LOG.info("create_new_endpoint_param: END")
            return []  # other error

        self.LOG.info("create_new_endpoint_param: entry={}".format(info))
        self.LOG.info("create_new_endpoint_param: END")
        return info  # no error

    # update endpoint param
    # input: name, paramID
    # output: ID on success
    def update_param(self, name: str, paramID: int) -> int:
        try:
            self.LOG.info(
                "update_endpoint_param: name={} paramID={}".format(name, paramID)
            )
            info = -1
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(
                    self.update_endpoint_param,
                    (name, paramID),
                )

                if len(sql.table) != 0:
                    info = sql.table[0]["ID"]
                else:
                    raise Exception("Unable to update endpoint param {}!".format(info))
        except Exception as e:
            self.LOG.error("update_endpoint_param: error={}".format(e))
            self.LOG.info("update_endpoint_param: END")
            return -1  # other error

        self.LOG.info("update_param_details: entry={}".format(info))
        self.LOG.info("update_param_details: END")
        return info  # no error

    # update endpoint params status
    # input: status, paramIDs
    # output: IDs on success
    def update_params_status(
        self, status: int, paramIDs: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "update_endpoint_params_status: status={} paramIDs={}".format(
                    status, paramIDs
                )
            )
            info = []
            if len(paramIDs) > 0:
                with SQL_Pull()(self.sql_config)() as sql:
                    if (
                        isinstance(verification, Verification)
                        and verification.get_verification() != -1
                    ):
                        paramIDs_string = ",".join(map(str, paramIDs))
                        # update status
                        sql.execute(
                            self.update_endpoint_params_status,
                            (status, paramIDs_string),
                        )

                        if len(sql.table) != 0:
                            info = sql.table
                        else:
                            raise Exception(
                                "Unable to update endpoint params status {}!".format(
                                    info
                                )
                            )
                    else:
                        raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_endpoint_params_status: error={}".format(e))
            self.LOG.info("update_endpoint_params_status: END")
            return []

        self.LOG.info("update_endpoint_params_status: entry={}".format(info))
        self.LOG.info("update_endpoint_params_status: END")
        return info  # no error


# UNIT TESTING


def main():
    return


if __name__ == "__main__":
    main()
