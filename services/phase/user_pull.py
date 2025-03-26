#!/usr/bin/env python3.7

from http.client import HTTPConnection
from .user_config import UserConfig
import bcrypt

from .gauge_pull import Gauge
from .verification_pull import Verification
from .sql_config import SQLConfig
from .sql_pull import SQL_Pull


class User(UserConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        UserConfig.__init__(self, sql_config)

        # initialize gauge
        self.gauge = Gauge()

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    # Generates a User object.
    # input: EmployeeID, account, password, role, fname, lname, avatar, email
    # output: user on success, {} on error
    def create_user(
        self,
        verification: Verification,
        employeeID: int,
        account: str,
        password: str,
        role: int,
        fname: str,
        lname: str,
        avatar: str,
        email: str,
        team: int,
        status: int,
    ) -> dict:
        try:
            self.LOG.info(
                f"create_user verification={verification} employeeID={employeeID} account={account} role={role} fname={fname} lname={lname} avatar={avatar} email={email} team={team} status={status}"
            )

            if (
                isinstance(verification, Verification)
                and verification.get_verification() != -1
            ):
                with SQL_Pull()(self.sql_config)() as sql:
                    if employeeID is not None:
                        sql.execute(self.get_user_by_employeeID, (employeeID))
                        if len(sql.table) > 0:
                            raise Exception(f"EmployeeID already exists!")

                    # Check if account already exists
                    if account is not None:
                        sql.execute(self.get_user_by_account, (account, account))
                        if len(sql.table) > 0:
                            raise Exception("Account already exists!")

                    if password is not None:
                        # Hash password before submitting to SQL
                        salt = bcrypt.gensalt()
                        password = password.encode("utf-8")
                        hashed = bcrypt.hashpw(password, salt)
                    # Create an active user if all required data is given
                    if (
                        account
                        and verification
                        and role
                        and fname
                        and lname
                        and avatar
                        and hashed
                    ):
                        sql.execute(
                            self.insert_active_user,
                            (
                                account,
                                hashed,
                                employeeID,
                                role,
                                fname,
                                lname,
                                avatar,
                                email,
                                team,
                                status,
                                verification.get_verification(),
                            ),
                        )
                        if len(sql.table) != 0:
                            userID = sql.table[0]
                        else:
                            raise Exception(
                                "An Error occured with the Create User Query"
                            )
                    else:
                        sql.execute(self.insert_requested_user, (fname, lname, email))
                        if len(sql.table) != 0:
                            userID = sql.table[0]

                # output userID
                return userID

        except Exception as e:
            self.LOG.error("create_user: error={}".format(e))
            self.LOG.info("create_user: END")
            return {"Error": e}

    # Returns the User info if they can login, otherwise return {}
    # input: account, password
    # output: user on success, {} on error
    def login(self, account: str, password: str) -> dict:
        try:
            self.LOG.info(f"login account={account}")

            user = {}

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.login_via_account, (account, account))

                if len(sql.table) == 1:
                    # Compare hashed password stored in database with password given
                    hashedPass = (sql.table[0]["password"]).encode()
                    password = password.encode("utf-8")
                    if bcrypt.checkpw(password, hashedPass):
                        user = sql.table[0]
                    else:
                        raise Exception("Incorrect password!")
                else:
                    raise Exception("User does not exist!")

        except Exception as e:
            self.LOG.error("login: error={}".format(e))
            self.LOG.info("login: END")
            return {}

        self.LOG.info("login: user={}".format(str(user)))
        self.LOG.info("login: END")
        return user  # no error

    # Returns all users
    # input: N/A
    # output: users on success, else []
    def get_users(self) -> list:
        try:
            self.LOG.info(f"get_users")

            users = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_all_users)
                if len(sql.table) != 0:
                    users = sql.table
                else:
                    raise Exception("An error occured with the get_all_users query")

            return users

        except Exception as e:
            self.LOG.error("get_users: error={}".format(e))
            self.LOG.info("get_users: END")
            return {}

    # Returns user info for the given account
    # input: account, verification
    # output: user on success, else {}
    def get_user_info_by_account(self, account: str) -> dict:
        try:
            self.LOG.info(f"get_user_info account={account}")

            user = {}

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_user_by_account, (account, account))
                if len(sql.table) != 0:
                    user = sql.table[0]
                else:
                    raise Exception(
                        "An error occured with the get_user_by_account query"
                    )

            return user

        except Exception as e:
            self.LOG.error("get_user_info_by_account: error={}".format(e))
            self.LOG.info("get_user_info_by_account: END")
            return {}

    # Returns user info for the given verification
    # input: employeeID
    # output: user on success, else {}
    def get_user_info_by_employeeID(self, employeeID: int) -> dict:
        try:
            self.LOG.info(f"get_user_info_by_employeeID: employeeID={employeeID}")

            user = {}

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_user_by_employeeID, (employeeID))
                if len(sql.table) != 0:
                    user = sql.table[0]
                else:
                    raise Exception(
                        "An error occured with the get_user_by_verification query"
                    )

            return user

        except Exception as e:
            self.LOG.error("get_user_info_by_employeeID: error={}".format(e))
            self.LOG.info("get_user_info_by_employeeID: END")
            return {}

    # Resets a user's password
    # input:  admin_account, admin_password, user_to_reset
    # output: user on success, else {}
    def reset_password(
        self, admin_account: str, admin_password: str, user_to_reset: str
    ) -> dict:
        try:
            self.LOG.info(
                f"reset_password admin={admin_account} user_to_reset={user_to_reset}"
            )

            user = {}
            default_password = "Ph@se@2501!"

            # Hash password before submitting to SQL
            salt = bcrypt.gensalt()
            password = default_password.encode("utf-8")
            hashed = bcrypt.hashpw(password, salt)

            # Check admin_account + admin_password
            admin = self.login(admin_account, admin_password)
            if admin != {}:
                with SQL_Pull()(self.sql_config)() as sql:
                    # Retrieve active permissions for the given user role
                    permissions, _ = sql.execute(
                        self.get_active_permissions_by_roleID, str(admin["role"])
                    )

                    # Check if user role has admin page access, if so reset the user_to_reset's password
                    permission_pages = map(
                        lambda permission: permission["Page"], permissions
                    )
                    if "Admin" in permission_pages:
                        sql.execute(self.reset_user_password, (hashed, user_to_reset))

                        if len(sql.table) != 0:
                            user = sql.table[0]

                        else:
                            raise Exception(
                                "An error occured with the reset_user_password query"
                            )
                    else:
                        raise Exception(
                            "Required privilege not met to reset passwords!"
                        )

            return user

        except Exception as e:
            self.LOG.error("reset_password: error={}".format(e))
            self.LOG.info("reset_password: END")
            return {}

    # Changes a user's password
    # input:  prevPassword, newPassword, account, forgotPassword
    # output: user on success, else {}
    def change_password(
        self,
        prevPassword: str,
        newPassword: str,
        account: str,
        forgotPassword: bool = False,
    ) -> dict:
        try:
            self.LOG.info(
                f"change_password account={account} forgotPassword={forgotPassword}"
            )

            user = {}

            newPassword = newPassword.encode("utf-8")
            # Hash newPassword
            salt = bcrypt.gensalt()
            newPassword = bcrypt.hashpw(newPassword, salt)
            passwordMatches = False

            with SQL_Pull()(self.sql_config)() as sql:
                # Get user account information
                sql.execute(self.get_user_with_password, (account))

                if len(sql.table) != 0:
                    user_info = sql.table[0]
                else:
                    raise Exception(
                        "An error occured with the get_user_with_password query"
                    )
                # If the user did not forget their password encode previous password
                if not forgotPassword:
                    # encode passwords preparing for hashing
                    prevPassword = prevPassword.encode("utf-8")
                    passwordMatches = bcrypt.checkpw(
                        prevPassword, user_info["password"].encode()
                    )

                # if prevPassword matches OR if user forgot password, update the password with new value
                if forgotPassword or passwordMatches:
                    sql.execute(self.change_user_password, (newPassword, account))
                    if len(sql.table) != 0:
                        user = sql.table[0]
                    else:
                        raise Exception(
                            "An error occured with the change_user_password query"
                        )

                else:
                    raise Exception("Incorrect password!")

            return user

        except Exception as e:
            self.LOG.error("change_user_password: error={}".format(e))
            self.LOG.info("change_user_password: END")
            return {}

    # Deletes a user
    # input:admin_account, admin_password, account
    # output: user on success, else {}
    def delete_user_account(self, admin_account, admin_password, userID: int) -> dict:
        try:

            self.LOG.info(
                f"delete_user_account admin_account={admin_account} userID={userID}"
            )

            user = {}

            # Check admin_account + admin_password
            admin = self.login(admin_account, admin_password)
            if admin != {}:
                with SQL_Pull()(self.sql_config)() as sql:
                    # Retrieve active permissions for the given user role
                    permissions, _ = sql.execute(
                        self.get_active_permissions_by_roleID, str(admin["role"])
                    )

                    # Check if user role has admin page access, if so reset the user_to_reset's password
                    permission_pages = map(
                        lambda permission: permission["Page"], permissions
                    )

                    if "Admin" in permission_pages:
                        sql.execute(self.delete_user, (userID))

                        if len(sql.table) != 0:
                            user = sql.table[0]

                        else:
                            raise Exception(
                                "An error occured with the delete_user query"
                            )
                    else:
                        raise Exception("Required privilege not met to delete users!")

            return user

        except Exception as e:
            self.LOG.error("delete_user_account: error={}".format(e))
            self.LOG.info("delete_user_account: END")
            return {}

    # Changes a user's info
    # input:{userInfo}
    # output: user on success, else {}
    def change_users_info(self, user: dict) -> dict:
        try:
            self.LOG.info(f"change_users_info user={user}")

            updated_user = {}

            # Updates SQL entry with key values from user object given
            with SQL_Pull()(self.sql_config)() as sql:
                # If the user object does not contain a password update everything but their password
                if user.get("password") is None:
                    sql.execute(
                        self.update_existing_users_info,
                        (
                            user["account"],
                            user["employeeID"],
                            user["role"],
                            user["fname"],
                            user["lname"],
                            user["email"],
                            user["avatar"],
                            user["team"],
                            user["status"],
                            user["ID"],
                        ),
                    )

                # If the user has requested an account and given a password update every field
                else:
                    # Hash password before submitting to SQL
                    salt = bcrypt.gensalt()
                    password = user["password"].encode("utf-8")
                    hashed_password = bcrypt.hashpw(password, salt)

                    sql.execute(
                        self.update_requested_users_info,
                        (
                            user["account"],
                            hashed_password,
                            user["employeeID"],
                            user["role"],
                            user["fname"],
                            user["lname"],
                            user["email"],
                            user["avatar"],
                            user["team"],
                            user["status"],
                            user["ID"],
                        ),
                    )
                if len(sql.table) != 0:
                    updated_user = sql.table

                else:
                    raise Exception("An error occured with the change_users_info query")

            return updated_user

        except Exception as e:
            self.LOG.error("change_users_info: error={}".format(e))
            self.LOG.info("change_users_info: END")
            return {}

    # Returns all active roles
    # input: N/A
    # output: active roles on success, else []
    def get_roles(self) -> list:
        try:
            self.LOG.info(f"get_roles")

            roles = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_active_roles)
                if len(sql.table) != 0:
                    roles = sql.table
                else:
                    raise Exception("An error occured with the get_all_roles query")

            return roles

        except Exception as e:
            self.LOG.error("get_roles: error={}".format(e))
            self.LOG.info("get_roles: END")
            return []

    # Returns the role associated with the given RoleID
    # input: roleID
    # output: role on success, else {}
    def get_role_by_id(self, roleID: int) -> dict:
        try:
            self.LOG.info(f"get_role_by_id")

            role = {}

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_role, (roleID))
                if len(sql.table) != 0:
                    role = sql.table[0]
                else:
                    raise Exception("An error occured with the get_role query")

            return role

        except Exception as e:
            self.LOG.error("get_role_by_id: error={}".format(e))
            self.LOG.info("get_role_by_id: END")
            return {}

    # Creates a new role
    # input: verification, title, status
    # output: role on success, else {}
    def create_role(self, verification: Verification, title: str, status: int) -> dict:
        try:
            self.LOG.info(
                f"create_role: verification={verification} title={title} status={status}"
            )

            role = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_role,
                        (title, status),
                    )
                    if len(sql.table) != 0:
                        role = sql.table[0]
                    else:
                        raise Exception("An error occured with the insert_role query")

                else:
                    raise Exception("Invalid EmployeeID!")

            return role

        except Exception as e:
            self.LOG.error("create_role: error={}".format(e))
            self.LOG.info("create_role: END")
            return role

    # Edit Role
    # input: verification, ID, Title, status
    # output: role on success, else {}
    def edit_role(
        self, verification: Verification, roleID: int, title: str, status: int
    ) -> dict:
        try:
            self.LOG.info(
                f"edit_role: verification={verification} ID={roleID} title={title} status={status}"
            )

            role = -1

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # If title or status is None, get those params from given roleID
                    if title is None or status is None:
                        initial_role = self.get_role_by_id(roleID)
                        # update terms if needed
                        if title is None:
                            title = initial_role["Title"]
                        if status is None:
                            status = initial_role["Status"]

                    sql.execute(self.update_role, (title, status, roleID))

                    if len(sql.table) != 0:
                        role = sql.table[0]
                    else:
                        raise Exception("An error occured with the update_role query")

                else:
                    raise Exception("Invalid EmployeeID!")

            return role

        except Exception as e:
            self.LOG.error("edit_role: error={}".format(e))
            self.LOG.info("edit_role: END")
            return role

    # Deletes a role
    # input: admin_account, admin_password, roleID
    # output: deleted role on success, {} on error
    def delete_role(self, admin_account: str, admin_password: str, roleID: int) -> dict:
        try:
            self.LOG.info(f"delete_role admin_account={admin_account} roleID={roleID}")

            role = {}

            # Check admin_account + admin_password
            admin = self.login(admin_account, admin_password)
            if admin != {}:
                with SQL_Pull()(self.sql_config)() as sql:
                    # Retrieve active permissions for the given user role
                    permissions, _ = sql.execute(
                        self.get_active_permissions_by_roleID, str(admin["role"])
                    )

                    # Check if user role has admin page access, if so delete the role
                    permission_pages = map(
                        lambda permission: permission["Page"], permissions
                    )
                    if "Admin" in permission_pages:
                        sql.execute(self.delete_given_role, (roleID))

                    if len(sql.table) != 0:
                        role = sql.table[0]

                    else:
                        raise Exception(
                            "An error occured with the delete_given_role query"
                        )

            else:
                raise Exception(
                    "User does not have the required permissions to delete roles!"
                )

            return role

        except Exception as e:
            self.LOG.error("delete_role: error={}".format(e))
            self.LOG.info("delete_role: END")
            return {}

    # Returns all active RolePermissionLinks
    # input: N/A
    # output: active RolePermissionLinks on success, else []
    def get_role_permission_links(self) -> list:
        try:
            self.LOG.info(f"get_role_permission_links")

            role_permission_links = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_active_role_permission_links)
                if len(sql.table) != 0:
                    role_permission_links = sql.table
                else:
                    raise Exception(
                        "An error occured with the role_permission_links query"
                    )

            return role_permission_links

        except Exception as e:
            self.LOG.error("role_permission_links: error={}".format(e))
            self.LOG.info("role_permission_links: END")
            return {}

    # Updates a roles permission links
    # input: verification, roleID, permissionIDs, status
    # output: role on success, -1 on error
    def update_role_permission_links(
        self, verification: Verification, roleID: int, permissionIDs: list, status: int
    ) -> dict:
        try:
            self.LOG.info(
                f"update_role_permission_links: verification={verification} roleID={roleID} permissionIDs={permissionIDs} status={status}"
            )

            role_permission_link = {}

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    # Generates placeholder ? for pyodbc inserts
                    permissionID_placeholders = ",".join("?" * len(permissionIDs))
                    sql.execute(
                        self.edit_role_permission_links.format(
                            permissionID_placeholders
                        ),
                        (status, roleID, *permissionIDs),
                    )
                    if len(sql.table) != 0:
                        role_permission_link = sql.table[0]
                    else:
                        raise Exception(
                            "An error occured with the update_role_permission_link query"
                        )

                else:
                    raise Exception("Invalid EmployeeID!")

            return role_permission_link

        except Exception as e:
            self.LOG.error("update_role_permission_link: error={}".format(e))
            self.LOG.info("update_role_permission_link: END")
            return role_permission_link

    # Creates a new role permission link
    # input: verification, roleID, permissionID
    # output: role permission link on success, else {}
    def create_role_permission_link(
        self, verification: Verification, roleID: int, permissionID: int
    ) -> dict:
        try:
            self.LOG.info(
                f"create_role_permission_link: verification={verification} roleID={roleID} permissionID={permissionID}"
            )

            role_permission_link = {}

            with SQL_Pull()(self.sql_config)() as sql:
                if (
                    isinstance(verification, Verification)
                    and verification.get_verification() != -1
                ):
                    sql.execute(
                        self.insert_role_permission_link,
                        (roleID, permissionID, verification.get_verification()),
                    )
                    if len(sql.table) != 0:
                        role_permission_link = sql.table[0]
                    else:
                        raise Exception(
                            "An error occured with the insert_role_permission_link query"
                        )

                else:
                    raise Exception("Invalid EmployeeID!")

            return role_permission_link

        except Exception as e:
            self.LOG.error("create_role_permission_link: error={}".format(e))
            self.LOG.info("create_role_permission_link: END")
            return role_permission_link

    # Returns active permissions for the given RoleID
    # input: roleID
    # output: active RolePermissionLinks on success, else []
    def get_permissions_for_role(self, role: int) -> list:
        try:
            self.LOG.info(f"get_role_permission_links")

            permissions = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_active_permissions_by_roleID, (role))
                if len(sql.table) != 0:
                    permissions = sql.table
                else:
                    raise Exception(
                        "An error occured with the get_active_permissions_by_roleID query"
                    )

            return permissions

        except Exception as e:
            self.LOG.error("get_permissions_for_role: error={}".format(e))
            self.LOG.info("get_permissions_for_role: END")
            return []

    # Returns all active permissions
    # input: N/A
    # output: active permissions on success, else []
    def get_permissions(self) -> list:
        try:
            self.LOG.info(f"get_permissions")

            permissions = []

            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_active_permissions)
                if len(sql.table) != 0:
                    permissions = sql.table
                else:
                    raise Exception(
                        "An error occured with the get_active_permissions query"
                    )

            return permissions

        except Exception as e:
            self.LOG.error("get_permissions: error={}".format(e))
            self.LOG.info("get_permissions: END")
            return []


# Unit Testing
def main():
    return


if __name__ == "__main__":
    main()
