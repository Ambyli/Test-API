#!/usr/bin/env python3.7

import datetime
from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .bulletin_config import BulletinConfig
from .verification_pull import Verification
from .file_pull import File


class Bulletin(BulletinConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        BulletinConfig.__init__(self, sql_config)

        # Create a file object
        self.file = File()

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

    # # Get All Bulletin
    # Output: List of Bulletins
    def get_bulletins(self) -> list:
        try:
            self.LOG.info("get_bulletins")
            bulletin = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_bulletin)
                bulletin = sql.table
        except Exception as e:
            self.LOG.error("get_bulletins: error={}".format(e))
            self.LOG.info("get_bulletins: END")
            return []
        return bulletin

    # # Get Bulletin by ID
    # Input: Bulletin ID
    # Output: Bulletin Object
    def get_bulletin_by_id(self, id: int) -> object:
        try:
            self.LOG.info("get_bulletin_by_id: id={}".format(id))
            bulletin = {}

            if id is not None:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(self.get_bulletin_by_ID, (id,))
                    files = self.file.get_files_by_bulletin(id)
                    if len(sql.table) > 0:
                        bulletin = sql.table[0]
                        bulletin["FileLinks"] = files
                    else:
                        raise Exception(
                            "No results found with the get_bulletin_by_id query!"
                        )
            else:
                self.LOG.info("get_bulletin_by_id: Error: Missing Inputs")
                self.LOG.info("get_bulletin_by_id: END")
                return None
        except Exception as e:
            self.LOG.error("get_bulletin_by_id: error={}".format(e))
            self.LOG.info("get_bulletin_by_id: END")
            return None
        return bulletin

    # # Filter Bulletin
    # Input: tags "ID,ID,ID", searchKeyword "str", createdFrom "2022-01-19 00:00:00.000", createdTo "2022-01-19 00:00:00.000", sortOrder "DESC", offset int, rows int
    # Output: List of Bulletins
    def filter_bulletins(
        self,
        searchKeyword,
        tags: list,
        createdFrom,
        createdTo,
        sortOrder,
        empID,
        offset: int,
        rows: int,
    ) -> list:
        try:
            self.LOG.info(
                "filter_bulletins: searchKeyword={}, tags={}, createdFrom={} createdTo={} sortOrder={} empID={} offset={} rows={}".format(
                    searchKeyword,
                    tags,
                    createdFrom,
                    createdTo,
                    sortOrder,
                    empID,
                    offset,
                    rows,
                )
            )

            # define bulletin info
            bulletin_info = []

            if offset is not None and rows is not None and sortOrder is not None:
                if sortOrder == "DESC" or sortOrder == "ASC":
                    with SQL_Pull()(self.sql_config)() as sql:
                        tagsString = ""
                        if len(tags) == 0:
                            tagsString = None
                        else:
                            tagsString = ",".join(map(str, tags))
                        sql.execute(
                            self.filter_bulletin,
                            (
                                sortOrder,
                                tagsString,
                                tagsString,
                                searchKeyword,
                                searchKeyword,
                                createdFrom,
                                createdFrom,
                                createdTo,
                                createdTo,
                                empID,
                                empID,
                                int(offset),
                                int(offset),
                                int(rows),
                            ),
                        )
                        bulletin_info = sql.table
                        grouped_data = {}

                        for obj in sql.table:
                            obj_id = obj["ID"]
                            fileLinks = self.file.get_files_by_bulletin(obj_id)
                            if obj_id not in grouped_data:
                                grouped_data[obj_id] = {
                                    "ID": obj_id,
                                    "Title": obj["Title"],
                                    "Body": obj["Body"],
                                    "Created": obj["Created"],
                                    "ExpireDate": obj["ExpireDate"],
                                    "VerificationID": obj["VerificationID"],
                                    "FirstName": obj["FirstName"],
                                    "LastName": obj["LastName"],
                                    "Status": obj["Status"],
                                    "FileLinks": fileLinks,
                                }
                                if obj["TagID"] is not None:
                                    grouped_data[obj_id]["TagID"] = obj["TagID"]
                                    grouped_data[obj_id]["Tag"] = obj["Tag"]

                            else:
                                grouped_data[obj_id]["TagID"] = obj["TagID"]
                                grouped_data[obj_id]["Tag"] = obj["Tag"]

                        bulletin_info = list(grouped_data.values())
                else:
                    self.LOG.info("filter_bulletins: Error: Invalid Sort Input")
                    self.LOG.info("filter_bulletins: END")
            else:
                self.LOG.info("filter_bulletins: Error: Missing Inputs")
                self.LOG.info("filter_bulletins: END")
                return []

        except Exception as e:
            self.LOG.error("filter_bulletins: error={}".format(e))
            self.LOG.info("filter_bulletins: END")
            return []
        return bulletin_info

    # # Filter Unexpired Bulletins with Tags ORDER by expire short to long
    # Input: TagIDs, TagIDs, Order by Column only accept "Created" or "ExpireLength"
    # Output: List of Bulletin
    def filter_unexpired_bulletins(self, tags: str, orderColumn: str) -> list:
        try:
            self.LOG.info(
                "filter_unexpired_bulletins: tags={}, orderColumn={}".format(
                    tags, orderColumn
                )
            )

            # define bulletin info
            bulletin_info = []

            if orderColumn is not None:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.filter_unexpired_bulletin, (tags, tags, orderColumn)
                    )
                    bulletin_info = sql.table
                    grouped_data = {}

                    for obj in sql.table:
                        obj_id = obj["ID"]
                        fileLinks = self.file.get_files_by_bulletin(obj_id)
                        if obj_id not in grouped_data:
                            grouped_data[obj_id] = {
                                "ID": obj_id,
                                "Title": obj["Title"],
                                "Body": obj["Body"],
                                "Created": obj["Created"],
                                "ExpireDate": obj["ExpireDate"],
                                "VerificationID": obj["VerificationID"],
                                "FirstName": obj["FirstName"],
                                "LastName": obj["LastName"],
                                "Status": obj["Status"],
                                "FileLinks": fileLinks,
                            }
                            if obj["TagID"] is not None:
                                grouped_data[obj_id]["TagID"] = obj["TagID"]
                                grouped_data[obj_id]["Tag"] = obj["Tag"]

                        else:
                            grouped_data[obj_id]["TagID"] = obj["TagID"]
                            grouped_data[obj_id]["Tag"] = obj["Tag"]

                    bulletin_info = list(grouped_data.values())
            else:
                self.LOG.info("filter_unexpired_bulletins: Error: Missing Inputs")
                self.LOG.info("filter_unexpired_bulletins: END")
                return []

        except Exception as e:
            self.LOG.error("filter_unexpired_bulletins: error={}".format(e))
            self.LOG.info("filter_unexpired_bulletins: END")
            return []
        return bulletin_info

    # # Get Latest Bulletin at each TagID
    # Output: List of Bulletin
    def get_latest_bulletin_at_each_tag_group(self) -> list:
        try:
            self.LOG.info("get_latest_bulletin_at_each_tag_group: ")
            bulletin = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_latest_bulletin_at_each_tag)
                if len(sql.table) > 0:
                    for db in sql.table:
                        fileLinks = self.file.get_files_by_bulletin(db["ID"])
                        db["FileLinks"] = fileLinks
                        bulletin.append(db)

        except Exception as e:
            self.LOG.error("get_latest_bulletin_at_each_tag_group: error={}".format(e))
            self.LOG.info("get_latest_bulletin_at_each_tag_group: END")
            return []
        return bulletin

    # # Insert Bulletin
    # Input: Title, Body, Created, VerificationID, Status
    # Output: Bulletin ID
    def create_bulletin(
        self,
        title: str,
        body: str,
        tags: list,
        verification: Verification,
        expireDate: str,
        files: dict,
        status: int = 11,
    ) -> object:
        try:
            self.LOG.info(
                "create_bulletin: Title={}, Body={}, Tags={}, Verification={}, ExpireDate={}, Files={}, status={}".format(
                    title,
                    body,
                    tags,
                    verification,
                    expireDate,
                    files,
                    status,
                )
            )

            bulletin = {}

            # check created ID
            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
                and title is not None
                and body is not None
                and expireDate is not None
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.insert_bulletin,
                        (
                            title,
                            body,
                            verification.get_verification(),
                            status,
                            expireDate,
                        ),
                    )
                    if len(sql.table) > 0:
                        # get bulletinID

                        # if tags given
                        if tags is not None:
                            # get all tags
                            all_tags = self.get_all_tags()
                            # get all ID of exist tags
                            exist_tags = [t["ID"] for t in all_tags if t["Tag"] in tags]
                            # get all tag names not exist
                            new_tags = list(
                                filter(
                                    lambda x: x not in [t["Tag"] for t in all_tags],
                                    tags,
                                )
                            )

                            new_tags_id = []
                            if len(new_tags) > 0:
                                # create new tags
                                tags_result = self.create_tags(new_tags)
                                new_tags_id = [t["ID"] for t in tags_result]

                            all_link_tags = exist_tags + new_tags_id

                            if len(all_link_tags) > 0:
                                # create bulletin tag links
                                self.create_bulletin_tag_links(
                                    int(sql.table[0]["ID"]),
                                    int(status),
                                    [x for x in all_link_tags],
                                    verification,
                                )
                                tagInfo = self.get_bulletin_tag_links_by_bulletin_ID(
                                    int(sql.table[0]["ID"])
                                )

                                if files:
                                    self.LOG.info("files 0: {}".format(files))
                                    # get banner information
                                    bannerID = files["bannerID"]
                                    bannerPath = files["bannerPath"]
                                    bannerFileTypeID = files["bannerTypeID"]
                                    attachments = files["attachments"]
                                    # if banner ID not exist -> create File for banner path
                                    if bannerID is None:
                                        bannerID = self.file.create_new_files(
                                            verification,
                                            [
                                                {
                                                    "path": bannerPath,
                                                    "typeID": bannerFileTypeID,
                                                }
                                            ],
                                        )[0]["FileID"]

                                    # format banner info to match with requirement of create_new_bulletin_file_links
                                    bannerFile = {}
                                    bannerFile["FileID"] = bannerID
                                    bannerFile["typeID"] = bannerFileTypeID
                                    # create Bulletin File Link for banner
                                    self.create_new_bulletin_file_links(
                                        sql.table[0]["ID"], [bannerFile], verification
                                    )

                                    # create Files for attachments if exist
                                    if len(attachments) > 0:
                                        # create files and store IDs of new files in att with format [{"FileID": 1}, {"FileID": 2},...]
                                        att = self.file.create_new_files(
                                            verification, attachments
                                        )
                                        # attachments include the path and file type id of each path, so combine return a new list include FileID, fileTypeID, and path with format [{"FileID": 1, "typeID":1, "path": 'http'}, {...}]
                                        combine = [
                                            dict(a, **b)
                                            for a, b in zip(att, attachments)
                                        ]

                                        if len(combine) > 0:
                                            # create file links if attachment exist
                                            attFileLinks = (
                                                self.create_new_bulletin_file_links(
                                                    sql.table[0]["ID"],
                                                    combine,
                                                    verification,
                                                )
                                            )

                                            # return bulletin information with file links as object
                                            if len(attFileLinks) > 0:
                                                # get all files associate with this bulletin
                                                fileLinks = (
                                                    self.file.get_files_by_bulletin(
                                                        sql.table[0]["ID"]
                                                    )
                                                )
                                                self.LOG.info(
                                                    "files 1: {}".format(fileLinks)
                                                )
                                                result = {}
                                                result["ID"] = sql.table[0]["ID"]
                                                result["Title"] = title
                                                result["Body"] = body
                                                result["Status"] = 11
                                                result["Tags"] = tagInfo
                                                result["Files"] = fileLinks
                                                result[
                                                    "Created"
                                                ] = datetime.datetime.now().strftime(
                                                    "%Y-%m-%d %H:%M:%S"
                                                )
                                                result["ExpireDate"] = expireDate
                                                bulletin = result
                                    # if no attachment -> return bulletin information as object
                                    else:
                                        # banner is an attachment, need to get it out.
                                        fileLinks = self.file.get_files_by_bulletin(
                                            sql.table[0]["ID"]
                                        )
                                        self.LOG.info("files 2: {}".format(fileLinks))
                                        result = {}
                                        result["ID"] = sql.table[0]["ID"]
                                        result["Title"] = title
                                        result["Body"] = body
                                        result["Status"] = 11
                                        result["Tags"] = tagInfo
                                        result["Files"] = fileLinks
                                        result[
                                            "Created"
                                        ] = datetime.datetime.now().strftime(
                                            "%Y-%m-%d %H:%M:%S"
                                        )
                                        result["ExpireDate"] = expireDate
                                        bulletin = result

                    else:
                        raise Exception(
                            "No results found with the create_bulletin query!"
                        )
            else:
                raise Exception("Missing Inputs")

        except Exception as e:
            self.LOG.error("create_bulletin: error={}".format(e))
            self.LOG.info("create_bulletin: END")
            return {}

        self.LOG.info("create_bulletin: result={}".format(bulletin))
        self.LOG.info("create_bulletin: END")
        return bulletin

    # # Update Bulletin
    # Input: Title, Body, Status, Tags, ID
    # Output: Bulletin ID
    def update_bulletin_info(
        self,
        title: str,
        body: str,
        tags: list,
        expireDate: str,
        id: int,
        verification: Verification,
    ) -> object:
        try:
            self.LOG.info(
                "update_bulletin: Title={} Body={} Tags={} ExpireDate={} ID={} verification={}".format(
                    title, body, tags, expireDate, id, verification
                )
            )
            bulletin = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(self.update_bulletin, (title, body, expireDate, id))
                    if len(sql.table) > 0:
                        if tags and len(tags) > 0:
                            # Get all tags
                            all_tags = self.get_all_tags()
                            # Get all associate tags
                            all_associate_tags = (
                                self.get_bulletin_tag_links_by_bulletin_ID(id)
                            )
                            # filter all active associate tags
                            active_tags = [
                                t for t in all_associate_tags if t["Status"] == 11
                            ]
                            # filter all inactive associate tags
                            inactive_tags = [
                                t for t in all_associate_tags if t["Status"] == 12
                            ]

                            # filter incoming tags in inactive associate tags -> update this status to Active (11)
                            incoming_inactive = [
                                t for t in inactive_tags if t["Tag"] in tags
                            ]
                            # filter new tags
                            new_tags = [
                                t
                                for t in tags
                                if t not in [l["Tag"] for l in all_associate_tags]
                            ]
                            # filter brand new tags not exist in database -> create new tags and links
                            brand_new_tags = [
                                t
                                for t in new_tags
                                if t not in [l["Tag"] for l in all_tags]
                            ]
                            # filter new tags that exist in database but not associate with this bulletin -> create Link for this.
                            new_not_associate_tags = [
                                t for t in all_tags if t["Tag"] in new_tags
                            ]
                            # filter active tags not in in coming tags -> update this status to 12
                            delete_tag = [
                                t for t in active_tags if t["Tag"] not in tags
                            ]

                            # update this status to 11
                            if len(incoming_inactive) > 0:
                                ids = [t["ID"] for t in incoming_inactive]
                                self.update_bulletin_tag_link_status_info(
                                    11, ids, verification
                                )

                            # update this status to 12
                            if len(delete_tag) > 0:
                                ids = [t["ID"] for t in delete_tag]
                                self.update_bulletin_tag_link_status_info(
                                    12, ids, verification
                                )

                            # create link for exist tags but not associate with current bulletin
                            if len(new_not_associate_tags) > 0:
                                ids = [t["ID"] for t in new_not_associate_tags]
                                self.create_bulletin_tag_links(
                                    id, 11, ids, verification
                                )

                            # create new tags and links
                            if len(brand_new_tags) > 0:
                                new_tag_ids = self.create_tags(brand_new_tags)
                                ids = [t["ID"] for t in new_tag_ids]
                                self.create_bulletin_tag_links(
                                    id, 11, ids, verification
                                )

                        else:  # if tags not provided or len of tags = 0 -> update all associate tags status to inactive (12)
                            # get all associate tags
                            all_associate_tags = (
                                self.get_bulletin_tag_links_by_bulletin_ID(id)
                            )
                            ids = [t["ID"] for t in all_associate_tags]
                            self.update_bulletin_tag_link_status_info(
                                12, ids, verification
                            )

                        bulletin = self.get_bulletin_by_id(sql.table[0]["ID"])
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_bulletin: error={}".format(e))
            return -1

        self.LOG.info("update_bulletin: END")
        return bulletin

    # # Delete Bulletin
    # Input: Bulletin ID
    def delete_bulletin(self, id: int, verification: Verification) -> int:
        try:
            bulletinID = -1
            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    id is not None
                    and isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_bulletin_status,
                        (
                            12,
                            id,
                        ),
                    )
                    if len(sql.table) > 0:
                        bulletinID = sql.table[0]["ID"]
                    else:
                        self.LOG.info("delete_bulletin: Error")
                else:
                    self.LOG.info("delete_bulletin: Error: Missing Inputs")
        except Exception as e:
            self.LOG.error("delete_bulletin: error={}".format(e))
            return -1

        self.LOG.info("delete_bulletin: END")
        return bulletinID

    # # Get Tags
    # Output: List of Tags
    def get_all_tags(self) -> list:
        try:
            self.LOG.info("get_all_tags: Start")

            tag_info = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_tags)

                if len(sql.table) != 0:
                    tag_info = sql.table
        except Exception as e:
            self.LOG.error("get_all_tags: error={}".format(e))
            return []

        self.LOG.info("get_all_tags: END")
        return tag_info

    # # Get Tag by ID
    # Input: TagID
    # Output" Tag Object
    def get_tag_by_id(self, id: int) -> object:
        try:
            self.LOG.info("get_tag_by_id: TagID={}".format(id))
            tag_info = {}
            if id:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(self.get_tag_by_ID, (id,))

                    if len(sql.table) > 0:
                        tag_info = sql.table[0]
                    else:
                        raise Exception(
                            "No results found with the get_tag_by_id query!"
                        )
            else:
                self.LOG.info("get_tag_by_id: Error: Missing Inputs")
                return None
        except Exception as e:
            self.LOG.error("get_tag_by_id: error={}".format(e))
            return None
        self.LOG.info("get_tag_by_id: END")
        return tag_info

    # # Insert Tag
    # Input: Tags "ID,ID,ID"
    # Output: Bulletin ID
    def create_tags(self, tags: list) -> list:
        try:
            self.LOG.info("create_tag: Tags={}".format(",".join(tags)))

            tag_info = []

            if tags is not None:
                with SQL_Pull()(self.sql_config)() as sql:
                    all_tags = self.get_all_tags()
                    new_tags = [
                        t for t in tags if t not in [l["Tag"] for l in all_tags]
                    ]

                    if len(new_tags) > 0:
                        sql.execute(self.insert_tags, (",".join(new_tags),))
                        if len(sql.table) != 0:
                            tag_info = sql.table
                        else:
                            raise Exception(
                                "No results found with the create_tag query!"
                            )
                    else:
                        self.LOG.info("create_tag: All Tags Existing")
                        return ["All Tags Existing"]
            else:
                self.LOG.info("create_tag: Error: Missing Inputs")
                return []
        except Exception as e:
            self.LOG.error("create_tag: error={}".format(e))
            return []

        self.LOG.info("create_tag: END")
        return tag_info

    # # Update Tag
    # Input: Tags "ID,ID,ID"
    # Output: Bulletin ID
    def update_tag_info(self, tag: str, tagID: int) -> int:
        try:
            self.LOG.info("update_tag_info: Tag={}, TagID={}".format(tag, tagID))

            tag_info = -1

            if tag is not None and tagID is not None:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(self.update_tag, (tag, tagID))

                    if len(sql.table) > 0:
                        tag_info = sql.table[0]["ID"]
                    else:
                        raise Exception(
                            "No results found with the update_tag_info query!"
                        )
            else:
                self.LOG.info("update_tag_info: Error: Missing Inputs")
                return -1
        except Exception as e:
            self.LOG.error("update_tag_info: error={}".format(e))
            return -1

        self.LOG.info("update_tag_info: END")
        return tag_info

    # # Delete Tag
    # Input: Tags "ID,ID,ID"
    # Output: Bulletin ID
    def delete_tag_info(self, tagID: int) -> int:
        try:
            self.LOG.info("delete_tag_info: TagID={}".format(tagID))

            tag_info = -1

            if tagID is not None:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(self.delete_tag, (int(tagID),))
                    if len(sql.table) > 0:
                        tag_info = 0
                        all_tag_links = self.get_all_bulletin_tag_links()
                        tagID_in_links = [
                            t["ID"] for t in all_tag_links if t["TagID"] == tagID
                        ]
                        if len(tagID_in_links) > 0:
                            self.delete_bulletin_tag_links(",".join(tagID_in_links))
                            tag_info = 1

                    else:
                        raise Exception(
                            "No results found with the update_tag_info query!"
                        )
            else:
                self.LOG.info("delete_tag_info: Error: Missing Inputs")
                return -1
        except Exception as e:
            self.LOG.error("delete_tag_info: error={}".format(e))
            return -1

        self.LOG.info("delete_tag_info: END")
        return tag_info

    # # get all Links
    # Output: List of Links
    def get_all_bulletin_tag_links(self) -> list:
        try:
            links = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_bulletin_tag_link)
                if len(sql.table) > 0:
                    links = sql.table
                else:
                    raise Exception(
                        "No results found with the get_all_bulletin_tag_links query!"
                    )
        except Exception as e:
            self.LOG.error("get_all_bulletin_tag_links: error={}".format(e))
            return []
        self.LOG.info("get_all_bulletin_tag_links: END")
        return links

    # # get all Links by ID
    # Output: List of Links
    def get_bulletin_tag_link_by_Link_ID(self, id: int) -> object:
        try:
            links = {}
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_bulletin_tag_link_by_ID, (id,))
                if len(sql.table) > 0:
                    links = sql.table[0]
                else:
                    raise Exception(
                        "No results found with the get_bulletin_tag_link_by_Link_ID query!"
                    )
        except Exception as e:
            self.LOG.error("get_bulletin_tag_link_by_Link_ID: error={}".format(e))
            return None
        self.LOG.info("get_bulletin_tag_link_by_Link_ID: END")
        return links

    # # get Links by Bulletin ID
    # Input: Bulletin ID
    # Output: List of Links
    def get_bulletin_tag_links_by_bulletin_ID(self, bulletinID: int) -> list:
        try:
            self.LOG.info(
                "get_bulletin_tag_links_by_bulletinID: bulletinID={}".format(bulletinID)
            )
            result = []

            if bulletinID:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.get_bulletin_tag_links_by_bulletinID, (bulletinID,)
                    )
                    if len(sql.table) != 0:
                        result = sql.table

            else:
                self.LOG.info(
                    "get_bulletin_tag_links_by_bulletinID: Error: Missing Inputs"
                )
                return []
        except Exception as e:
            self.LOG.error("get_bulletin_tag_links_by_bulletinID: error={}".format(e))
            return []
        self.LOG.info("get_bulletin_tag_links_by_bulletinID: END")
        return result

    # # Insert Bulletin Tag Links
    # Input: Tags "ID,ID,ID"
    # Output: Bulletin ID
    def create_bulletin_tag_links(
        self, bulletinID: int, status: int, tags: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "create_bulletin_tag_links: bulletinID={} status={} tags={} verification={}".format(
                    bulletinID, status, tags, verification
                )
            )

            tag_info = []

            if bulletinID is not None and status is not None and tags is not None:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    with SQL_Pull()(self.sql_config)() as sql:
                        # filter out existing tag links
                        all_links_associate = (
                            self.get_bulletin_tag_links_by_bulletin_ID(bulletinID)
                        )
                        new_links = [
                            l
                            for l in tags
                            if l not in [t["TagID"] for t in all_links_associate]
                        ]

                        if len(new_links) > 0:
                            sql.execute(
                                self.insert_bulletin_tag_links,
                                (
                                    bulletinID,
                                    status,
                                    verification.get_verification(),
                                    str(",".join(map(str, new_links))),
                                ),
                            )
                            if len(sql.table) != 0:
                                tag_info = sql.table
                            else:
                                raise Exception(
                                    "No results found with the create_bulletin_tag_links query!"
                                )
                else:
                    raise Exception("Invalid validation!")
            else:
                self.LOG.info("create_bulletin_tag_links: Error: Missing Inputs")
                return []

        except Exception as e:
            self.LOG.error("create_bulletin_tag_links: error={}".format(e))
            return []

        self.LOG.info("create_bulletin_tag_links: END")
        return tag_info

    # # Update Bulletin
    # Input: Title, Body, Status, ID
    # Output: Bulletin ID
    def update_bulletin_tag_link_status_info(
        self, status: int, tagIDs: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "update_bulletin_tag_link_status: Status={}, TagID={} verification={}".format(
                    status, tagIDs, verification
                )
            )
            bulletinTagLinkID = []

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_bulletin_tag_link_status,
                        (status, ",".join(map(str, tagIDs))),
                    )
                    if len(sql.table) > 0:
                        bulletinTagLinkID = sql.table
                    else:
                        raise Exception(
                            "No results found with the update_bulletin_tag_link_status query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("update_bulletin_tag_link_status: error={}".format(e))
            return []

        self.LOG.info("update_bulletin_tag_link_status: END")
        return bulletinTagLinkID

    # # Delete bulletin tag links
    # Input: LinkIDs
    def delete_bulletin_tag_links(self, linkIDs: str) -> int:
        try:
            self.LOG.info("delete_bulletin_tag_links: linksID={}".format(linkIDs))
            result = -1
            if linkIDs:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(self.delete_bulletin_tag_link, (linkIDs,))
                    if len(sql.table) > 0:
                        result = 1
                    else:
                        raise Exception(
                            "No results found with the delete_bulletin_tag_links query!"
                        )
            else:
                self.LOG.info("delete_bulletin_tag_links: Error: Missing Inputs")
                return -1
        except Exception as e:
            self.LOG.error("delete_bulletin_tag_links: error={}".format(e))
            return -1
        self.LOG.info("delete_bulletin_tag_links: END")
        return result

    # # Get All Bulletin File Links
    def get_all_bulletin_file_links(self) -> list:
        try:
            self.LOG.info("get_all_bulletin_file_links")
            result = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_bulletin_file_links)
                result = sql.table

        except Exception as e:
            self.LOG.error("get_all_bulletin_file_links: error={}".format(e))
            return []
        self.LOG.info("get_all_bulletin_file_links: END")
        return result

    # # Get Bulletin File Links by Link ID
    def get_all_bulletin_file_links_by_link_id(self, id: int) -> list:
        try:
            self.LOG.info("get_bulletin_file_links_by_ID")
            result = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_bulletin_file_links_by_id, (id,))
                result = sql.table

        except Exception as e:
            self.LOG.error("get_bulletin_file_links_by_ID: error={}".format(e))
            return []
        self.LOG.info("get_bulletin_file_links_by_ID: END")
        return result

    # # Get Bulletin File Links by Bulletin ID
    def get_all_bulletin_file_links_by_bulletin_id(self, id: int) -> list:
        try:
            self.LOG.info("get_all_bulletin_file_links_by_bulletin_id")
            result = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_bulletin_file_links_by_bulletin, (id,))
                result = sql.table

        except Exception as e:
            self.LOG.error(
                "get_all_bulletin_file_links_by_bulletin_id: error={}".format(e)
            )
            return []
        self.LOG.info("get_all_bulletin_file_links_by_bulletin_id: END")
        return result

    # # Create Bulletin File Link
    # Input: BulletinID ,FileID , Verification
    def create_new_bulletin_file_links(
        self, bulletinID: int, files: list, verification: Verification
    ) -> list:
        try:
            self.LOG.info(
                "create_new_bulletin_file_link: BulletinID: {}, Files: {}, Verification: {}".format(
                    bulletinID, files, verification
                )
            )

            result = []

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
                and bulletinID
                and files
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    for file in files:
                        self.LOG.info(file)
                        sql.execute(
                            self.create_bulletin_file_links,
                            (
                                bulletinID,
                                file["FileID"],
                                file["typeID"],
                                verification.get_verification(),
                            ),
                        )
                        if len(sql.table) > 0:
                            result.append(sql.table[0])
            else:
                raise Exception("Missing Inputs")

        except Exception as e:
            self.LOG.error("create_new_bulletin_file_link: error={}".format(e))
            self.LOG.info("create_new_bulletin_file_link: END")
            return []

        self.LOG.info("create_new_bulletin_file_link: result={}".format(result))
        self.LOG.info("create_new_bulletin_file_link: END")
        return result

    # # Update Bulletin File Link Status
    # Input: Status, IDs
    def update_bulletin_file_links_status(
        self, status: int, ids: list, verification: Verification
    ) -> int:
        try:
            self.LOG.info(
                "update_bulletin_file_links_status: status={} ids={} verification={}".format(
                    status, ids, verification
                )
            )

            result = -1

            if ids is not None:
                with SQL_Pull()(self.sql_config)() as sql:
                    if (
                        isinstance(verification, Verification)
                        and verification.get_verification() != -1
                    ):
                        sql.execute(
                            self.update_bulletin_file_link_status,
                            (status, ",".join(map(str, ids))),
                        )
                        if len(sql.table) > 0:
                            result = 1
                    else:
                        raise Exception("Invalid verification!")
            else:
                self.LOG.info(
                    "update_bulletin_file_links_status: Error: Missing Inputs"
                )
                return -1

        except Exception as e:
            self.LOG.error("update_bulletin_file_links_status: error={}".format(e))
            return -1

        self.LOG.info("update_bulletin_file_links_status: END")
        return result


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
