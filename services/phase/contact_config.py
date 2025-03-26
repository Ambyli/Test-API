from .config import Config
from .sql_config import SQLConfig


# contact config
class ContactConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # # Contact Functions
        # input: N/A
        # output: [[ ID, FirstName, LastName Email, Created, PhoneNumber, Company Status]]
        self.get_contacts = "SELECT ID, FirstName, LastName, Email, Created, Company, PhoneNumber, Status from {database}.dbo.Contacts WHERE Status = 11"
        # input: Contact
        # output: [ID]
        self.insert_contact = "INSERT INTO {database}.dbo.Contacts (FirstName, LastName, Email, Company, PhoneNumber, Created, Status) OUTPUT Inserted.ID VALUES (?, ?, ?, ?, ?, GETDATE(), 11)"
        # input: ContactID
        # output: [ID]
        self.update_selected_contact = "UPDATE {database}.dbo.Contacts SET FirstName = ?, LastName = ?, Email = ?, PhoneNumber = ?, Company = ?, Status = ? OUTPUT INSERTED.ID WHERE ID = ?"
        # input: N/A
        # output: [{ID, Name, Description, Created, Status}]
        self.get_contact_groups = "SELECT ID, Name, Description, Created, Status from {database}.dbo.ContactGroups where Status = 11"
        # input: Name, Description
        # output: ID
        self.insert_contact_group = "INSERT INTO {database}.dbo.ContactGroups (Name, Description, Created, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), 11)"
        # input: ContactGroupID
        # output: ID
        self.update_selected_contact_group = "UPDATE {database}.dbo.ContactGroups SET Name = ?, Description = ?, Status = ? OUTPUT INSERTED.ID WHERE ID = ?"
        # input: contact_group_ID, contact_ID
        # output: ID
        self.insert_contact_group_contact_link = "INSERT INTO {database}.dbo.ContactGroupContactLinks (ContactGroupID, ContactID, Created, Status) OUTPUT Inserted.ID VALUES (?, ?, GETDATE(), 11)"
        # input: contact_group_contact_link_ID
        # output: ID
        self.update_selected_contact_group_contact_link = "UPDATE {database}.dbo.ContactGroupContactLinks SET ContactGroupID = ?, ContactID = ?, Status = ? OUTPUT INSERTED.ID WHERE ID = ?"
        # input: N/A
        # output: [{ID,ContactGroupID, ContactID, Created, Status}]
        self.get_contact_group_contact_links = "SELECT ID, ContactGroupID, ContactID, Created, Status from {database}.dbo.ContactGroupContactLinks where Status = 11"
