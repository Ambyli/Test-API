#!/usr/bin/env python3.7

from os import link
from typing import List, Dict

from .sql_config import SQLConfig
from .shade_regex import gen_steps
from .sql_pull import SQL_Pull
from .contact_config import ContactConfig
from .gauge_pull import Gauge
from .verification_pull import Verification


class Contact(ContactConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        ContactConfig.__init__(self, sql_config)

        # # initialize gauge
        # self.gauge = Gauge()

        # # Current working values
        # result = []
        # with SQL_Pull()(self.sql_config)() as sql:
        #     result, _ = sql.execute(self.get_status)
        #     for stat in result:
        #         self.statuses[stat["ID"]] = stat["StatusType"]

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # gets active contacts
    # input: N/A
    # output: Contactss on success, [] on error
    def get_active_contacts(self) -> list:
        try:
            self.LOG.info("get_active_contacts: BEGIN")

            contacts = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_contacts)
                if len(sql.table) != 0:
                    contacts = sql.table
                else:
                    raise Exception("No results found with the get_contacts query!")

        except Exception as e:
            self.LOG.error("get_active_contacts: error={}".format(e))
            self.LOG.info("get_active_contacts: END")
            return []  # other error

        self.LOG.info("get_active_contacts: contacts={}".format(len(contacts)))
        self.LOG.info("get_active_contacts: END")
        return contacts  # no error

    # Creates an contact
    def create_contact(
        self, verification, firstName, lastName, email, phoneNumber, company
    ) -> dict:
        try:
            self.LOG.info(
                f"create_contact: verification={verification} firstName={firstName} lastName={lastName} email={email} phoneNumber={phoneNumber} company={company}"
            )

            contact_ID = {}

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_contact,
                        (firstName, lastName, email, company, phoneNumber),
                    )
                    if len(sql.table) > 0:
                        contact_ID = sql.table[0]
                    else:
                        raise Exception(
                            "No results found with the insert_contact query!"
                        )
                else:
                    raise Exception("Invalid employee ID!")

        except Exception as e:
            self.LOG.error("create_contact: error={}".format(e))
            self.LOG.info("create_contact: END")
            return contact_ID

        self.LOG.info("create_contact: contact={}".format(contact_ID))
        self.LOG.info("create_contact: END")
        return contact_ID

    # Updates a contact
    def update_contact(
        self,
        verification,
        contact_id,
        first_name,
        last_name,
        email,
        phone_number,
        company,
        status,
    ) -> dict:
        try:
            self.LOG.info(
                f"update_contact: verification={verification} contact={contact_id} first_name={first_name} last_name={last_name} email={email} phone_number={phone_number} company={company} status={status}"
            )

            contact_updated = {}

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_selected_contact,
                        (
                            first_name,
                            last_name,
                            email,
                            phone_number,
                            company,
                            status,
                            contact_id,
                        ),
                    )
                    if len(sql.table) > 0:
                        contact_updated = sql.table[0]
                    else:
                        raise Exception(
                            "No results found with the update_contact query!"
                        )
                else:
                    raise Exception("Invalid employee ID!")

        except Exception as e:
            self.LOG.error("update_contact: error={}".format(e))
            self.LOG.info("update_contact: END")
            return contact_updated

        self.LOG.info("update_contact: updated={}".format(contact_updated))
        self.LOG.info("update_contact: END")
        return contact_updated

    # Creates an contact group
    def create_contact_group(self, verification, name, description) -> dict:
        try:
            self.LOG.info(
                f"create_contact_group: verification={verification} name={name} description={description}"
            )

            contact_group_ID = {}

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_contact_group,
                        (name, description),
                    )
                    if len(sql.table) > 0:
                        contact_group_ID = sql.table[0]
                    else:
                        raise Exception(
                            "No results found with the contact_group_ID query!"
                        )
                else:
                    raise Exception("Invalid employee ID!")

        except Exception as e:
            self.LOG.error("create_contact_group: error={}".format(e))
            self.LOG.info("create_contact_group: END")
            return contact_group_ID

        self.LOG.info("create_contact_group: contact={}".format(contact_group_ID))
        self.LOG.info("create_contact_group: END")
        return contact_group_ID

    # Updates a contact group
    def update_contact_group(
        self, verification, name, description, contact_group_ID, status
    ) -> dict:
        try:
            self.LOG.info(
                f"update_contact_group: verification={verification} contact_group_ID={contact_group_ID} name={name} description={description} status={status}"
            )

            contact_group_updated = {}

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_selected_contact_group,
                        (name, description, status, contact_group_ID),
                    )
                    if len(sql.table) > 0:
                        contact_group_updated = sql.table[0]
                    else:
                        raise Exception(
                            "No results found with the contact_group_ID query!"
                        )
                else:
                    raise Exception("Invalid employee ID!")

        except Exception as e:
            self.LOG.error("update_contact_group: error={}".format(e))
            self.LOG.info("update_contact_group: END")
            return contact_group_updated

        self.LOG.info("update_contact_group: contact={}".format(contact_group_updated))
        self.LOG.info("update_contact_group: END")
        return contact_group_updated

    # gets active contact_groups
    # input: N/A
    # output: Contat_groups on success, [] on error
    def get_active_contact_groups(self) -> list:
        try:
            self.LOG.info("get_active_contact_groups: BEGIN")

            contact_groups = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_contact_groups)
                if len(sql.table) != 0:
                    contact_groups = sql.table
                else:
                    raise Exception(
                        "No results found with the get_contact_groups query!"
                    )

        except Exception as e:
            self.LOG.error("get_active_contact_groups: error={}".format(e))
            self.LOG.info("get_active_contact_groups: END")
            return []  # other error

        self.LOG.info(
            "get_active_contact_groups: contacts={}".format(len(contact_groups))
        )
        self.LOG.info("get_active_contact_groups: END")
        return contact_groups  # no error

    # Creates an contact group contact link
    def create_contact_group_contact_link(
        self, verification, contact_group_ID, contact_ID
    ) -> dict:
        try:
            self.LOG.info(
                f"create_contact_group_contact_link: verification={verification} contact_group_ID={contact_group_ID} contact_ID={contact_ID}"
            )

            contact_group_contact_link_ID = {}

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_contact_group_contact_link,
                        (contact_group_ID, contact_ID),
                    )
                    if len(sql.table) > 0:
                        contact_group_contact_link_ID = sql.table[0]
                    else:
                        raise Exception(
                            "No results found with the insert_contact_group_contact_link query!"
                        )
                else:
                    raise Exception("Invalid employee ID!")

        except Exception as e:
            self.LOG.error("create_contact_group_contact_link: error={}".format(e))
            self.LOG.info("create_contact_group_contact_link: END")
            return contact_group_contact_link_ID

        self.LOG.info(
            "create_contact_group_contact_link: contact={}".format(
                contact_group_contact_link_ID
            )
        )
        self.LOG.info("create_contact_group_contact_link: END")
        return contact_group_contact_link_ID

    # Updates a contact group
    def update_contact_group(
        self, verification, name, description, contact_group_ID, status
    ) -> dict:
        try:
            self.LOG.info(
                f"update_contact_group: verification={verification} contact_group_ID={contact_group_ID} name={name} description={description} status={status}"
            )

            contact_group_updated = {}

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_selected_contact_group,
                        (name, description, status, contact_group_ID),
                    )
                    if len(sql.table) > 0:
                        contact_group_updated = sql.table[0]
                    else:
                        raise Exception(
                            "No results found with the contact_group_ID query!"
                        )
                else:
                    raise Exception("Invalid employee ID!")

        except Exception as e:
            self.LOG.error("update_contact_group: error={}".format(e))
            self.LOG.info("update_contact_group: END")
            return contact_group_updated

        self.LOG.info("update_contact_group: contact={}".format(contact_group_updated))
        self.LOG.info("update_contact_group: END")
        return contact_group_updated

    # gets active contact_groups
    # input: N/A
    # output: Contact_groups on success, [] on error
    def get_active_contact_groups(self) -> list:
        try:
            self.LOG.info("get_active_contact_groups: BEGIN")

            contact_groups = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_contact_groups)
                if len(sql.table) != 0:
                    contact_groups = sql.table
                else:
                    raise Exception(
                        "No results found with the get_contact_groups query!"
                    )

        except Exception as e:
            self.LOG.error("get_active_contact_groups: error={}".format(e))
            self.LOG.info("get_active_contact_groups: END")
            return []  # other error

        self.LOG.info(
            "get_active_contact_groups: contacts={}".format(len(contact_groups))
        )
        self.LOG.info("get_active_contact_groups: END")
        return contact_groups  # no error

    # gets active contact_group_contact_links
    # input: N/A
    # output: Contact_groups on success, [] on error
    def get_active_contact_group_links(self) -> list:
        try:
            self.LOG.info("get_active_contact_group_links: BEGIN")

            contact_groups = []
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_contact_group_contact_links)
                if len(sql.table) != 0:
                    contact_groups = sql.table
                else:
                    raise Exception(
                        "No results found with the get_contact_group_contact_links query!"
                    )

        except Exception as e:
            self.LOG.error("get_active_contact_group_links: error={}".format(e))
            self.LOG.info("get_active_contact_group_links: END")
            return []  # other error

        self.LOG.info(
            "get_active_contact_group_links: contacts={}".format(len(contact_groups))
        )
        self.LOG.info("get_active_contact_group_links: END")
        return contact_groups  # no error

    # updates contact group contact link
    # input: contact_group_contact_link_ID, contact_group_ID, contact_ID, status
    # output: {} on success, -1 on error
    def update_contact_group_contact_link(
        self,
        verification,
        contact_group_contact_link_ID,
        contact_group_ID,
        contact_ID,
        status,
    ) -> dict:
        try:
            self.LOG.info(
                f"update_contact_group_contact_link: {contact_group_contact_link_ID}, contact_group_ID={contact_group_ID} contact_ID={contact_ID} status={status} "
            )

            updated_contact_group_contact_link = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.update_selected_contact_group_contact_link,
                        (
                            contact_group_ID,
                            contact_ID,
                            status,
                            contact_group_contact_link_ID,
                        ),
                    )
                    if len(sql.table) != 0:
                        updated_contact_group_contact_link = sql.table[0]
                    else:
                        raise Exception(
                            "No results found with the updated_contact_group_contact_linkget_contact_groups query!"
                        )

        except Exception as e:
            self.LOG.error("update_contact_group_contact_link: error={}".format(e))
            self.LOG.info("update_contact_group_contact_link: END")
            return {}  # other error

        self.LOG.info(
            "update_contact_group_contact_link: contacts={}".format(
                updated_contact_group_contact_link
            )
        )
        self.LOG.info("update_contact_group_contact_link: END")
        return updated_contact_group_contact_link  # no error


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
