#!/usr/bin/env python3.10
import logging
from .sql_config import SQLConfig


# base config
class Config:
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        # Set up logger
        self.LOG = logging.getLogger("phase")
        # path = "{}/logs/aligner_pull.log".format(os.getcwd())
        # file_handler = logging.FileHandler(path)
        # console_handler = logging.StreamHandler()
        # formatter = logging.Formatter(
        #     "%(asctime)s %(levelname)s %(process)d %(filename)s:%(lineno)d %(message)s"
        # )
        # file_handler.setFormatter(formatter)
        # console_handler.setFormatter(formatter)
        # self.LOG.addHandler(file_handler)
        # self.LOG.addHandler(console_handler)
        self.LOG.setLevel(logging.INFO)

        # define sql object
        self.sql_config = sql_config

        # value IDs for various items
        self.statuses = {}
        self.locations = {}
        self.file_types = {}
        self.reasons = {}
        self.roles = {}
        self.log_types = {}
        self.materials = {}
        self.severity_types = {}

        # # Generic functions
        self.health_check = """
            SET NOCOUNT ON
            /* Deallocate open cursors*/
            IF CURSOR_STATUS('global', 'curso1') >= -1
            BEGIN
                DEALLOCATE curso1
            END

            /* Define First cursor, a list of tables */
            DECLARE @TableName VARCHAR(MAX)
            DECLARE @PrimaryKey VARCHAR(MAX)
            DECLARE @DynamicQuery NVARCHAR(MAX)
            SET @DynamicQuery = ''
            DECLARE curso1 CURSOR FAST_FORWARD 
            FOR 
            SELECT [name] FROM {0}.sys.tables ORDER BY [name] ASC OFFSET(0) ROWS FETCH NEXT 500 ROWS ONLY

            /* Open curso1 */
            OPEN curso1
            FETCH NEXT FROM curso1 INTO @TableName

            WHILE (@@FETCH_STATUS <> -1)
            BEGIN
                /* run a simple select from each table */
                IF (@@FETCH_STATUS <> -2)
                BEGIN
                    SET @PrimaryKey = (SELECT C.COLUMN_NAME FROM {0}.INFORMATION_SCHEMA.TABLE_CONSTRAINTS T JOIN {0}.INFORMATION_SCHEMA.CONSTRAINT_COLUMN_USAGE C ON C.CONSTRAINT_NAME=T.CONSTRAINT_NAME WHERE C.TABLE_NAME = @TableName and T.CONSTRAINT_TYPE = 'PRIMARY KEY')

                    SET @DynamicQuery = @DynamicQuery + 'SELECT TOP 1 ' + CAST(@PrimaryKey as VARCHAR(MAX)) + ' FROM {database}.dbo.' + @TableName + ' ORDER BY ' + CAST(@PrimaryKey as VARCHAR(MAX)) + ' DESC;'
                END
                
                /* Go to next table */
                FETCH NEXT FROM curso1 INTO @TableName
            END
            CLOSE curso1
            DEALLOCATE curso1

            SELECT value as Query FROM STRING_SPLIT(@DynamicQuery, ';')
        """
        # input: N/A
        # output: [[StatusType]]
        self.get_status = "SELECT StatusType, ID FROM {database}.dbo.Status"
        # input: N/A
        # output: [[Location]]
        self.get_locations_by_locationID = "SELECT Location, ID, Color, Parent, Description, Status, Weight FROM {database}.dbo.Locations WHERE ID = ?"
        # input: N/A
        # output: [[Location]]
        self.get_locations = "SELECT Location, ID, Color, Parent, Description, Status, Weight FROM {database}.dbo.Locations ORDER BY Location ASC"
        # input: N/A
        # output: [[Materials]]
        self.get_materials = "SELECT MaterialID, BrandID, Type, Description, SKU, ProductLine FROM {database}.dbo.Materials"
        # input: N/A
        # output: [[Name]]
        self.get_file_types = (
            "SELECT Name, ID, Description, Extension FROM {database}.dbo.FileTypes"
        )
        # input: N/A
        # output: [[ReasonType]]
        self.get_fixit_reasons = (
            "SELECT ReasonType, ID, Status FROM {database}.dbo.FixitReasons"
        )
        # input: N/A
        # output: [[LogType]]
        self.get_log_types = "SELECT LogType, ID FROM {database}.dbo.LogTypes"
        # input: N/A
        # output: [[SeverityType]]
        self.get_severity_types = (
            "SELECT SeverityType, ID FROM {database}.dbo.SeverityTypes"
        )

    # HELPER FUNCTIONS
    def list_to_dict(self, item_dict, values, level, *levels):
        """
        Description:
            - Converts a list into a dictionary given a specified number of
              key levels provided.
        """
        if len(list(levels)) == 0:
            return {}

        # user provided too many levels
        if len(list(levels)) > len(values):
            new_list = list(levels)
            new_list.pop()
            item_dict = self.list_to_dict(item_dict, values, level, *new_list)
            # return Exception("Length of levels > length of values!")

        # we have gone through all the levels in levels, append left over
        # stuff to last node, level - 1
        if level > (len(list(levels)) - 1):
            leftover = []
            for i, value in enumerate(values):
                if i not in list(levels):
                    leftover.append(value)
            return leftover
        # we are on a active level
        else:
            # check level
            if levels[level] > len(values) - 1:
                return []
                # raise Exception("Column {} is > length of
                # values!".format(levels[level]))

            # define value, this is the root based on the column
            value = values[levels[level]]  # will throw error if access out of bounds!

            # value is not in keys
            if value not in item_dict.keys():
                item_dict[value] = self.list_to_dict({}, values, level + 1, *levels)
            # value is in keys
            else:
                # if we reached a list, append next branch to current branch
                if type(item_dict[value]) == list:
                    item_dict[value].extend(
                        self.list_to_dict(item_dict[value], values, level + 1, *levels)
                    )
                # else we found a value in key
                else:
                    item_dict[value] = self.list_to_dict(
                        item_dict[value], values, level + 1, *levels
                    )

            # return item_dict
            return item_dict
