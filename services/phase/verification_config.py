from .config import Config
from .sql_config import SQLConfig


# Verification config
class VerificationConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        from .employee_pull import Employee

        # Create an employee object
        self.emp = Employee()

        # # Verfication functions
        self.insert_verification_batch = "INSERT INTO {database}.dbo.Verifications (Created, Status) OUTPUT Inserted.ID VALUES (GETDATE(), 11)"
        self.get_verification_batch_by_id = (
            "SELECT ID, Created, Status FROM {database}.dbo.Verifications WHERE ID = ?"
        )
        self.link_employee_verification_batch = "INSERT INTO {database}.dbo.VerificationEmployeeLinks (VerificationID, EmployeeID, Created, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), 11)"
        self.get_employees_by_verification_id = "SELECT EmployeeID, Created, Status FROM {database}.dbo.VerificationEmployeeLinks WHERE VerificationID = ? ORDER BY Created DESC"
