#!/usr/bin/env python3.7

import time

from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .lock_config import LockConfig
from .verification_pull import Verification


class Lock(LockConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        LockConfig.__init__(self, sql_config)

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    def is_lock_ready(
        self, verification: Verification, lockID: int, timeout_s: int = 5
    ) -> int:
        try:
            self.LOG.info(
                "is_lock_ready: verification={0} lockID={1} timeout_s={2}".format(
                    verification, lockID, timeout_s
                )
            )

            # get lock given
            lock = self.get_lock(lockID)
            if len(lock) == 0:
                raise Exception("Provided lock '{0}' is invalid!".format(lockID))

            # check lock queue
            timeout = time.time() + timeout_s
            while True:
                # update lock log
                self.log_lock(
                    lockID,
                    "Examining",
                    "Lock Examined",
                    verification,
                    37,
                )

                # examine queue
                queue = self.get_lock_queue(
                    lock[0]["LockType"]
                )  # queue should always have data unless table is empty
                if len(queue) == 0:
                    raise Exception(
                        "No locks in queue!"
                    )  # this should never execute unless query for get lock queue is broken

                # check if lock is top of queue
                if queue[0]["ID"] == lockID:
                    # update lock log
                    self.log_lock(
                        lockID,
                        "Ready",
                        "Lock is Ready",
                        verification,
                        38,
                    )

                    # leave loop
                    self.LOG.info("is_lock_ready: END")
                    return 0

                # check what index lock is at
                found = 0
                for i, item in enumerate(queue):
                    if item["ID"] == lockID:
                        found = i
                if found < len(queue):
                    # update lock log
                    self.log_lock(
                        lockID,
                        "Lock Found",
                        "{0} in top {1}".format(i + 1, len(queue)),
                        verification,
                        37,
                    )
                else:
                    # update lock log
                    self.log_lock(
                        lockID,
                        "Lock Not Found",
                        "> top {0}".format(len(queue)),
                        verification,
                        37,
                    )

                # loop till timeout is hit
                if time.time() > timeout:
                    raise Exception(
                        "Exceeded number of checks, lock '{0}' is not ready!".format(
                            lockID
                        )
                    )

        except Exception as e:
            self.LOG.error("is_lock_ready: {}".format(e))

        self.LOG.info("is_lock_ready: END")
        return -1

    def get_lock_queue(self, locktype: int) -> list:
        try:
            self.LOG.info("get_lock_queue: locktype={}".format(locktype))

            locks = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_lock_queue_by_type, (locktype))
                if len(sql.table) != 0:
                    locks = sql.table
                else:
                    raise Exception(
                        "No results found with the get_lock_queue_by_type query!"
                    )

        except Exception as e:
            self.LOG.error("get_lock_queue: error={}".format(e))
            self.LOG.info("get_lock_queue: END")
            return []  # other error

        self.LOG.info("get_lock_queue: locks={}".format(locks))
        self.LOG.info("get_lock_queue: END")
        return locks  # no error

    def log_lock(
        self,
        lockID: int,
        change: str,
        description: str,
        verification: Verification,
        logtype: int,
    ) -> int:
        try:
            self.LOG.info(
                'log_lock: lockID={} change="{}" description="{}" verification={} logtype={}'.format(
                    lockID, change, description, verification, logtype
                )
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_lock_log,
                        (
                            logtype,
                            change,
                            description,
                            verification.get_verification(),
                            lockID,
                            lockID,
                            lockID,
                            lockID,
                            lockID,
                            lockID,
                            lockID,
                            lockID,
                        ),
                    )

                    if len(sql.table) != 0:
                        self.LOG.info("log_lock: END")
                        return 0
                    else:
                        raise Exception(
                            "No results found with the insert_lock_log query!"
                        )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("log_lock: error={}".format(e))

        self.LOG.info("log_lock: END")
        return -1

    def get_lock(self, lockID: int) -> list:
        try:
            self.LOG.info("get_lock: lockID={}".format(lockID))

            lock = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_lock_by_id, (lockID))
                if len(sql.table) != 0:
                    lock = sql.table
                else:
                    raise Exception("No results found with the get_lock_by_id query!")

        except Exception as e:
            self.LOG.error("get_lock: error={}".format(e))
            self.LOG.info("get_lock: END")
            return []  # other error

        self.LOG.info("get_lock: lock={}".format(lock))
        self.LOG.info("get_lock: END")
        return lock  # no error

    def create_lock(
        self, verification: Verification, description: str, locktype: int
    ) -> int:
        try:
            self.LOG.info(
                "create_lock: verification={} description={} locktype={}".format(
                    verification, description, locktype
                )
            )

            # define Lock ID
            lockID = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_lock,
                        (
                            description,
                            locktype,
                            verification.get_verification(),
                        ),
                    )
                    if len(sql.table) > 0:
                        lockID = int(sql.table[0]["ID"])

                        # update lock log
                        self.log_lock(
                            lockID,
                            "New",
                            "Lock Created",
                            verification,
                            35,
                        )
                    else:
                        raise Exception("No results found with the insert_lock query!")
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("create_lock: error={}".format(e))
            return -1

        self.LOG.info("create_lock: lockID={0}".format(lockID))
        self.LOG.info("create_lock: END")
        return lockID

    # updates a Lock object and/or outputs text to a log
    # input: Text, Index, Length, Limit, Constant
    # output: 0 on success, -1 on failure
    def disable_lock(self, verification: Verification, lockID: int) -> int:
        try:
            self.LOG.info(
                "disable_lock: verification={0} lockID={1}".format(verification, lockID)
            )

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.disable_lock_by_id,
                        (verification.get_verification(), lockID),
                    )
                    if len(sql.table) == 0:
                        raise Exception(
                            "No results found with the disable_lock_by_id query!"
                        )

                    # update lock log
                    self.log_lock(
                        lockID,
                        "Disabled",
                        "Lock Disabled",
                        verification,
                        36,
                    )
                else:
                    raise Exception("Invalid verification!")

        except Exception as e:
            self.LOG.error("disable_lock: {}".format(e))
            return -1

        self.LOG.info("disable_lock: END")
        return 0


# UNIT TESTING


def main():
    return


if __name__ == "__main__":
    main()
