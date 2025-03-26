from .config import Config
from .sql_config import SQLConfig


# User Config
class UserConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # input: Account/Email, Password
        # output: User
        self.login_via_account = "SELECT ID, account, password, employeeID, role, fname, lname, avatar, email, team, status FROM {database}.dbo.UserAccounts where account = ? or email = ?"
        # input: Account, Password, EmployeeID, Role, Fname, Lname, avatar, email
        # output: User
        self.insert_active_user = "INSERT INTO {database}.dbo.UserAccounts (account, password, employeeID, role, fname, lname, avatar, email, team, status, VerificationID) OUTPUT Inserted.ID, Inserted.account, Inserted.employeeID, Inserted.role, Inserted.fname, Inserted.lname, Inserted.avatar, Inserted.email, Inserted.team, Inserted.status VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
        # input: Fname, Lname, email, Status
        # output: User
        self.insert_requested_user = "INSERT INTO {database}.dbo.UserAccounts (fname, lname, email, status) OUTPUT Inserted.ID, Inserted.fname, Inserted.lname, Inserted.email, Inserted.status VALUES (?, ?, ?, 12)"
        # input: Account
        # output: User
        self.get_user_by_account = "SELECT ID, account, employeeID, role, fname, lname, avatar, email, team, status from {database}.dbo.UserAccounts where account = ? or email = ?"
        # input: Account
        # output: User
        self.get_user_with_password = (
            "SELECT * from {database}.dbo.UserAccounts where account = ?"
        )
        # input: employeeID
        # output: User
        self.get_user_by_employeeID = "SELECT ID, account, employeeID, role, fname, lname, avatar, email, team, status from {database}.dbo.UserAccounts where employeeID = ?"
        # input: N/A
        # output: [users]
        self.get_all_users = "SELECT ID, account, employeeID, role, fname, lname, avatar, email, team, status, VerificationID FROM {database}.dbo.UserAccounts"
        # input: account, newPassword
        # output: user
        self.change_user_password = "UPDATE {database}.dbo.UserAccounts SET password = ? OUTPUT inserted.ID, inserted.account where account = ?"
        # input: account, password
        # output: user
        self.reset_user_password = "UPDATE {database}.dbo.UserAccounts SET password = ? OUTPUT inserted.ID, inserted.account where account = ?"
        # input: account, employeeID, role, fname, lname, email, avatar, team, Status
        # output: user
        self.update_existing_users_info = "UPDATE {database}.dbo.UserAccounts SET account = ?, employeeID = ?, role = ?, fname = ?, lname = ?, email = ?, avatar = ?, team = ?, status = ? OUTPUT inserted.ID, inserted.account, inserted.employeeID, inserted.role, inserted.fname, inserted.lname, inserted.email, inserted.avatar, inserted.team, inserted.status where ID = ?"
        # input: account, password, employeeID, role, fname, lname, email, avatar, team, Status
        # output: user
        self.update_requested_users_info = "UPDATE {database}.dbo.UserAccounts SET account = ?, password = ?, employeeID = ?,  role = ?, fname = ?, lname = ?, email = ?, avatar = ?, team = ?, status = ? OUTPUT inserted.ID, inserted.account, inserted.employeeID, inserted.role, inserted.fname, inserted.lname, inserted.email, inserted.avatar, inserted.team, inserted.status where ID = ?"
        # input: account, email
        # output: user
        self.delete_user = "DELETE FROM {database}.dbo.UserAccounts OUTPUT deleted.ID, deleted.account, deleted.email, deleted.employeeID, deleted.fname, deleted.lname WHERE ID = ?"
        # input: N/A
        # output: active roles
        self.get_active_roles = "SELECT * from {database}.dbo.Roles where Status = 11"
        # input: RoleID
        # output: role
        self.get_role = "SELECT * from {database}.dbo.Roles where ID = ?"
        # input: Title, Status
        # output: Role
        self.insert_role = "INSERT INTO {database}.dbo.Roles (Title, Status) OUTPUT Inserted.ID, Inserted.title, Inserted.Status VALUES (?, ?)"
        # input: Title, Status, RoleID
        # output: Role
        self.update_role = "UPDATE {database}.dbo.Roles SET Title = ?, Status = ? OUTPUT inserted.ID, inserted.Title, inserted.Status where ID = ?"
        # Input: RoleID
        # output: deleted role
        self.delete_given_role = "DELETE FROM {database}.dbo.Roles OUTPUT deleted.ID, deleted.Title WHERE ID = ?"
        # input: N/A
        # output: active role permission links
        self.get_active_role_permission_links = (
            "SELECT * from {database}.dbo.RolePermissionLinks where Status = 11"
        )
        # input: RoleID, PermissionID
        # output: Role permission link
        self.insert_role_permission_link = "INSERT INTO {database}.dbo.RolePermissionLinks (RoleID, PermissionID, Created, VerificationID, Status ) OUTPUT Inserted.ID, Inserted.RoleID, Inserted.PermissionID, Inserted.VerificationID, Inserted.Status VALUES (?, ?, GETDATE(), ?, 11)"
        # input: RoleID
        # output: list containing active permissions for the RoleID given
        self.get_active_permissions_by_roleID = "SELECT a.ID, a.RoleID, a.PermissionID, b.Name, b.Description, b.Page, a.Status FROM {database}.dbo.RolePermissionLinks as a LEFT JOIN {database}.dbo.Permissions as b ON a.PermissionID = b.ID WHERE a.RoleID = ? and a.Status = 11 ORDER BY a.ID ASC"
        # input: N/A
        # output: active permissions
        self.get_active_permissions = (
            "SELECT * from {database}.dbo.Permissions where Status = 11"
        )
        # input: Title, Status, RoleID
        # output: Role
        self.edit_role_permission_links = "UPDATE {{database}}.dbo.RolePermissionLinks SET Status = ? OUTPUT inserted.ID, inserted.RoleID, inserted.Status where RoleID = ? and PermissionID in ({0})"
