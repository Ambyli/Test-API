#!/usr/bin/env python3.7

import io
import re
from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .token_pull import Token
from .file_config import FileConfig
from .verification_pull import Verification
from azure.storage.blob import BlobServiceClient
from azure.storage.fileshare import ShareClient


class File(FileConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        FileConfig.__init__(self, sql_config)

        # Create a Token object
        self.tok = Token()

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

    def get_all_files(self) -> list:
        try:
            self.LOG.info("get_all_files")
            result = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_files)
                result = sql.table

        except Exception as e:
            self.LOG.error("get_all_files: error={}".format(e))
            return []
        self.LOG.info("get_all_files: END")
        return result

    # # Get File by ID
    # Input: ID
    def get_file_by_file_id(self, id: int) -> object:
        try:
            self.LOG.info("get_file_by_file_id")
            result = {}
            if id:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(self.get_file_by_id, (id,))
                    if len(sql.table) > 0:
                        result = sql.table[0]
            else:
                self.LOG.info("get_file_by_file_id: Error: Missing Inputs")
                return -1

        except Exception as e:
            self.LOG.error("get_file_by_file_id: error={}".format(e))
            return -1
        self.LOG.info("get_file_by_file_id: END")
        return result

    # # Get File by Bulletin ID
    # Input: ID
    def get_files_by_bulletin(self, id: int) -> list:
        try:
            self.LOG.info("get_file_by_bulletin: id={}".format(id))
            result = []
            if id:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(self.get_file_by_bulletin_id, (id,))
                    result = sql.table
            else:
                raise Exception("Missing Inputs")

        except Exception as e:
            self.LOG.error("get_file_by_bulletin: error={}".format(e))
            return []
        self.LOG.info("get_file_by_bulletin: END")
        return result

    # # Get File by Type
    # Input: ID
    def get_files_by_types(self, ids: list, offset: int, rows: int) -> list:
        try:
            self.LOG.info(
                "get_files_by_type: ids {}, offset {}, rows {}".format(
                    ids, offset, rows
                )
            )
            result = []
            if ids:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(
                        self.get_file_by_type_id,
                        (",".join(map(str, ids)), offset, rows),
                    )
                    result = sql.table
            else:
                self.LOG.info("get_files_by_type: Error: Missing Inputs")
                return []

        except Exception as e:
            self.LOG.error("get_files_by_type: error={}".format(e))
            return []
        self.LOG.info("get_files_by_type: END")
        return result

    # # Get File by Batch
    # Input: ID
    def get_files_by_storage_batch(self, id: int) -> list:
        try:
            self.LOG.info("get_files_by_storage_batch: id={}".format(id))
            result = []
            if id:
                with SQL_Pull()(self.sql_config)() as sql:
                    sql.execute(self.get_file_by_storage_batch_id, (id,))
                    result = sql.table
            else:
                self.LOG.info("get_files_by_storage_batch: Error: Missing Inputs")
                return []

        except Exception as e:
            self.LOG.error("get_files_by_storage_batch: error={}".format(e))
            return []
        self.LOG.info("get_files_by_storage_batch: END")
        return result

    # # Create new File
    # Input: List of file paths and fileTypeID with format [{path:'A', typeID:1}, {path:'B', typeID:2},...]
    # Output: [{fileID: 1}, {fileID: 2}, ...]
    def create_new_files(self, verification: Verification, files: list) -> list:
        try:
            self.LOG.info(
                "create_new_file: verification={} files={}".format(verification, files)
            )

            # define return value
            result = []

            # validate verification and len of files
            if (
                len(files) > 0
                and isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    # build multiple insert statements
                    values = []
                    for file in files:
                        item = (file["path"], file["typeID"])
                        if item not in values:
                            values.append(item)

                    values_string = ", ".join(
                        [
                            f"('{path}', {typeID}, GETDATE(), {verification.get_verification()})"
                            for path, typeID in values
                        ]
                    )

                    # insert all values
                    sql.execute(self.create_files + values_string)
                    if len(sql.table) > 0:
                        result = sql.table
            elif len(files) == 0:
                result = []
            else:
                raise Exception("Invalid verification or no files provided!")

        except Exception as e:
            self.LOG.error("create_new_file: error={}".format(e))
            return []

        self.LOG.info("create_new_file: END")
        return result

    def upload_to_blob(
        self,
        verification: Verification,
        filename: str,
        num_bytes: bytes,
        account_url="https://phaseapi.blob.core.windows.net/",
        container="cases",
        storage_key="PHASE_STORAGE_KEY_2",
        account_name="PHASE_STORAGE_NAME_2",
    ) -> bool:
        try:
            self.LOG.info("upload_to_blob: BEGIN")

            uploaded = False
            file_path = ""

            # Get Azure Token
            azure_token = self.tok.get_azure_blob_token(
                verification,
                storage_key=storage_key,
                account_name=account_name,
            )

            if azure_token == {}:
                raise Exception("There was an error retrieving an active token!")

            self.LOG.info("upload_to_blob: token={}".format(azure_token["Token"]))
            blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=azure_token["Token"],
            )

            # get client
            blob_client = blob_service_client.get_blob_client(
                container=container, blob=filename
            )
            # upload to blob
            file_uploaded = blob_client.upload_blob(num_bytes, blob_type="BlockBlob")

            # If the file successfully uploaded and has a request_id, set uploaded to true
            if file_uploaded.get("request_id", False):
                uploaded = True
                file_path = f"{account_url}/{container}/{filename}"

        except Exception as e:
            self.LOG.error("upload_to_blob: error={}".format(e))
            self.LOG.info("upload_to_blob: END")
            return uploaded, file_path  # other error

        self.LOG.info("upload_to_blob: END")
        return uploaded, file_path  # no error

    def download_from_blob(
        self,
        verification: Verification,
        filename: str,
        account_url="https://phaseapi.blob.core.windows.net/",
        container="cases",
        storage_key="PHASE_STORAGE_KEY_2",
        account_name="PHASE_STORAGE_NAME_2",
    ) -> bytes:
        try:
            self.LOG.info("download_from_blob: filename={}".format(filename))

            # define bytes
            num_bytes = None

            # create stream
            stream = io.BytesIO()

            # Get Azure Token
            azure_token = self.tok.get_azure_blob_token(
                verification,
                storage_key=storage_key,
                account_name=account_name,
            )
            if azure_token == {}:
                raise Exception("There was an error retrieving an active token!")

            blob_service_client = BlobServiceClient(
                account_url=account_url,
                credential=azure_token["Token"],
            )

            # get client
            blob_client = blob_service_client.get_blob_client(
                container=container, blob=filename
            )

            # download file into stream and get bytes
            blob_client.download_blob().readinto(stream)
            num_bytes = stream.getvalue()

        except Exception as e:
            self.LOG.error("download_from_blob: error={}".format(e))
            self.LOG.info("download_from_blob: END")
            return None, None  # other error

        self.LOG.info("download_from_blob: END")
        return num_bytes, filename  # no error

    def upload_to_file_share(
        self,
        verification: Verification,
        filename: str,
        num_bytes: bytes,
        account_url="https://phasestorage.file.core.windows.net/",
        folder_path="",
        share_name="prod-phasestorage",
        storage_key="PHASE_STORAGE_KEY_1",
        account_name="PHASE_STORAGE_NAME_1",
        base_dir="RemoteMain",
        create_folder=False,
    ) -> bool:
        try:
            self.LOG.info(
                f"upload_to_file_share: filename={filename} account_url={account_url} folder_path={folder_path} share_name={share_name} base_dir={base_dir} create_folder={create_folder}"
            )

            uploaded = False
            final_path = ""

            # Get Azure Token
            azure_token = self.tok.get_azure_fileshare_token(
                verification,
                storage_key=storage_key,
                account_name=account_name,
            )
            if azure_token == {}:
                raise Exception("There was an error retrieving an active token!")

            self.LOG.info("upload_to_file_share: token={}".format(azure_token["Token"]))

            # Connect to prod-phasestorage
            share = ShareClient(
                account_url=account_url,
                credential=azure_token["Token"],
                share_name=share_name,
            )

            # Create client to interact with the directory
            # This is needed to check if the Folder path exists + Create it if it doesn't
            directory_client = share.get_directory_client(base_dir)
            # If the directory_client doesn't contain the folder_path directory, create it
            avail_dirs = directory_client.list_directories_and_files()
            # Pull the list of directories from the directory_client
            dir_names = list(map(lambda dir: dir["name"], avail_dirs))

            if folder_path in dir_names:
                self.LOG.info(
                    f"upload_to_file_share: Directory {folder_path} already exists"
                )
                # Directory already exists, init directory client for that directory
                subdirectory_client = directory_client.get_subdirectory_client(
                    folder_path
                )
            elif create_folder:
                self.LOG.info(
                    f"upload_to_file_share: Directory {folder_path} doesn't exist, creating directory"
                )
                # Directory doesn't exist, create it and init directory client for that directory
                subdirectory_client = directory_client.create_subdirectory(folder_path)
            else:
                raise Exception("No Folder Exists and Create Folder is False")

            # Initiate the file client so we can upload the file to the subdir
            file_client = subdirectory_client.get_file_client(filename)
            file_uploaded = file_client.upload_file(num_bytes)

            # If the file successfully uploaded and has a request_id, set uploaded to true
            if file_uploaded.get("request_id", False):
                uploaded = True
                file_properties = file_client.get_file_properties()
                final_path = rf"\phasestorage.file.core.windows.net/{file_properties.get('share')}/{file_properties.get('path')}"

        except Exception as e:
            self.LOG.error("upload_to_file_share: error={}".format(e))
            self.LOG.info("upload_to_file_share: END")
            return uploaded, final_path  # other error

        self.LOG.info("upload_to_file_share: END")
        return uploaded, final_path  # no error

    def download_from_fileshare(
        self,
        verification: Verification,
        path,
        account_url="https://phasestorage.file.core.windows.net/",
        share_name="prod-phasestorage",
        storage_key="PHASE_STORAGE_KEY_1",
        account_name="PHASE_STORAGE_NAME_1",
    ) -> bytes:
        try:
            self.LOG.info(
                "download_from_fileshare: path={}, account_url={}, share_name={}".format(
                    path, account_url, share_name
                )
            )
            # remove \\ in path at front
            if len(path) > 2 and "\\\\" == path[:1]:
                path = path[1:]

            # make all delimiter type characters the same
            path = path.replace("\\", "/")

            # split path into parts
            split_path = path.split("/")

            # remove parts that are account_url and or share_name
            parts = []
            for part in split_path:
                if part in account_url or part in share_name:
                    continue
                parts.append(part)
            if len(parts) < 3:
                raise Exception(
                    "File path must have a main directory, sub directory, and filename!"
                )

            # create stream
            stream = io.BytesIO()

            # Get Azure Token
            azure_token = self.tok.get_azure_fileshare_token(
                verification,
                storage_key=storage_key,
                account_name=account_name,
            )

            if azure_token == {}:
                raise Exception("There was an error retrieving an active token!")

            # Connect to prod-phasestorage
            share = ShareClient(
                account_url=account_url,
                credential=azure_token["Token"],
                share_name=share_name,
            )

            # define directory, sub_directory, and filename
            directory = "/".join(
                parts[: len(parts) - 2]
            )  # everything but sub directory and filename
            sub_directory = parts[
                -2
            ]  # get sub directory, always the second part from the end
            file_name = parts[-1]  # get file name, always the first part from the end

            # Create client to interact with the directory
            directory_client = share.get_directory_client(directory)

            # Check if subdirectory exists
            subdir_client = directory_client.get_subdirectory_client(sub_directory)
            if not subdir_client.exists():
                raise Exception(f"No folder named {sub_directory} found")

            file_client = subdir_client.get_file_client(file_name=file_name)

            # # download file into stream and get bytes
            file_stream = file_client.download_file()

            file_stream.readinto(stream)

            file_data = stream.getvalue()

        except Exception as e:
            raise e
            self.LOG.error("download_from_fileshare: error={}".format(e))
            self.LOG.info("download_from_fileshare: END")
            return None, None  # other error

        self.LOG.info("download_from_fileshare: END")
        return file_data, file_name  # no error


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
