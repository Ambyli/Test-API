#!/usr/bin/env python3.7

import tempfile
import os
from azure.storage.blob import BlobServiceClient

account_url = "https://phaseapi.blob.core.windows.net/?sv=2021-06-08&ss=bfqt&srt=sco&sp=rwdlacupiyx&se=2024-02-02T04:25:23Z&st=2022-11-08T20:25:23Z&spr=https&sig=PaVE19zlzq1AtMSNvOQaMOn%2FyHt%2F%2FsF7lIZxr8Pp7Yk%3D"
service = BlobServiceClient(account_url=account_url)


class Test:
    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    def test_env(self) -> int:
        try:
            self.LOG.info("test_env: BEGIN")

            self.LOG.info(f"test_env: environment={os.environ}")
            result = os.environ

        except Exception as e:
            self.LOG.error("test_env: error={}".format(e))
            self.LOG.info("test_env: END")
            return {}  # other error

        self.LOG.info("test_env: END")
        return result  # no error

    def download_from_blob(self) -> int:
        try:
            self.LOG.info("download_from_blob: file={}".format(file))

        except Exception as e:
            self.LOG.error("download_from_blob: error={}".format(e))
            self.LOG.info("download_from_blob: END")
            return -1  # other error

        self.LOG.info("create_file: END")
        return 0  # no error

    def create_file(self, file: str) -> int:
        try:
            self.LOG.info("create_file: file={}".format(file))

            """
            tempfilepath = tempfile.gettempdir()
            fp = tempfile.NamedTemporaryFile()
            fp.write(b"Hello World!")
            filesdirlistintemp = os.listdir(tempfilepath)

            self.LOG.info("create_file: files=[{}]".format(filesdirlistintemp))
            """

            with open(file, "w") as fp:
                fp.write("hello world")
                self.LOG.info("create_file: temp={}".format(os.path.realpath(fp.name)))

        except Exception as e:
            self.LOG.error("create_file: error={}".format(e))
            self.LOG.info("create_file: END")
            return -1  # other error

        self.LOG.info("create_file: END")
        return 0  # no error

    def edit_file(self, file: str, body: str) -> int:
        try:
            self.LOG.info("edit_file: file={}".format(file))

            with open(file, "w") as fp:
                fp.write(body)
                self.LOG.info("create_file: temp={}".format(os.path.realpath(fp.name)))

        except Exception as e:
            self.LOG.error("edit_file: error={}".format(e))
            self.LOG.info("edit_file: END")
            return -1  # other error

        self.LOG.info("edit_file: END")
        return 0  # no error


# UNIT TESTING


def main():
    return


if __name__ == "__main__":
    main()
