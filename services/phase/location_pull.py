#!/usr/bin/env python3.7


from .sql_config import SQLConfig
from .sql_pull import SQL_Pull
from .location_config import LocationConfig


class Location(LocationConfig):
    # CONSTRUCTOR
    # initialize variables above
    def __init__(self, sql_config=SQLConfig):
        LocationConfig.__init__(self, sql_config)

        # Current working values
        result = []
        with SQL_Pull()(self.sql_config)() as sql:
            result, _ = sql.execute(self.get_status)
            for stat in result:
                self.statuses[stat["ID"]] = stat["StatusType"]
            result, _ = sql.execute(self.get_locations)
            for loc in result:
                self.locations[loc["ID"]] = loc["Location"]

    # used for entering class instance with with
    def __enter__(self):
        return self

    # used for exiting class instance with with
    def __exit__(self, exc_type, exc_value, traceback):
        # clear linked values
        return

    def get_locations_by_id(self, locationID: int) -> list:
        try:
            self.LOG.info("get_locations_by_id: locationID={}".format(locationID))

            locations = []

            # get locations from status
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_locations_by_locationID, (locationID,))
                if len(sql.table) > 0:
                    locations = sql.table
                else:
                    raise Exception(
                        "No results found with the get_locations_by_locationID query!"
                    )

        except Exception as e:
            self.LOG.error("get_locations_by_id: error={}".format(e))
            return []

        self.LOG.info("get_locations_by_id: locations={0}".format(len(locations)))
        self.LOG.info("get_locations_by_id: END")
        return locations

    def get_locations_by_status(self, status: int | None = None) -> list:
        try:
            self.LOG.info("get_locations_by_status: status={}".format(status))

            locations = []

            # get locations from status
            with SQL_Pull()(self.sql_config)() as sql:
                if status is None:
                    sql.execute(self.get_locations)
                else:
                    sql.execute(self.get_locations_from_status, (status))
                if len(sql.table) > 0:
                    locations = sql.table
                else:
                    raise Exception(
                        "No results found with the get_locations_by_status query!"
                    )

        except Exception as e:
            self.LOG.error("get_locations_by_status: error={}".format(e))
            return []

        self.LOG.info("get_locations_by_status: locations={0}".format(len(locations)))
        self.LOG.info("get_locations_by_status: END")
        return locations

    # gets the core goals for a given location
    # input: Location
    # output: Goals on success, [] on error
    def get_location_aligner_goal_by_location(self, location: int) -> list:
        try:
            self.LOG.info(
                "get_location_aligner_goal_by_location: location={}".format(location)
            )

            goal = []

            # get aligners from location
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_location_goal_by_location, (location))
                if len(sql.table) > 0:
                    goal = sql.table
                else:
                    raise Exception(
                        "No results found with the get_location_goal_by_location query!"
                    )

        except Exception as e:
            self.LOG.error("get_location_aligner_goal_by_location: error={}".format(e))
            return []

        self.LOG.info(
            "get_location_aligner_goal_by_location: goal={0}".format(len(goal))
        )
        self.LOG.info("get_location_aligner_goal_by_location: END")
        return goal

    # gets the core goals for a given location
    # input: N/A
    # output: Goals on success, [] on error
    def get_location_aligner_goals(self) -> list:
        try:
            self.LOG.info("get_location_aligner_goals: BEGIN")

            goals = []

            # get aligners from location
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_location_goals)
                if len(sql.table) > 0:
                    goals = sql.table
                else:
                    raise Exception(
                        "No results found with the get_location_goals query!"
                    )

        except Exception as e:
            self.LOG.error("get_location_aligner_goals: error={}".format(e))
            return []

        self.LOG.info("get_location_aligner_goals: goals={0}".format(len(goals)))
        self.LOG.info("get_location_aligner_goals: END")
        return goals

    # gets a locations previous location routes
    # input: Location
    # output: Locations on success, [] on error
    def get_locations_previous_location(self, location: int) -> list:
        try:
            self.LOG.info(
                "get_locations_previous_location: location={}".format(location)
            )

            locations = []

            # get locations from location
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_previous_locations_by_location, (location))
                if len(sql.table) > 0:
                    locations = sql.table
                else:
                    raise Exception(
                        "No results found with the get_previous_locations_by_location query!"
                    )

        except Exception as e:
            self.LOG.error("get_locations_previous_location: error={}".format(e))
            return []

        self.LOG.info(
            "get_locations_previous_location: locations={0}".format(len(locations))
        )
        self.LOG.info("get_locations_previous_location: END")
        return locations

    # gets a locations following location routes
    # input: Location
    # output: Locations on success, [] on error
    def get_locations_following_location(self, location: int) -> list:
        try:
            self.LOG.info(
                "get_locations_following_location: location={}".format(location)
            )

            locations = []

            # get locations from location
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_following_locations_by_location, (location))
                if len(sql.table) > 0:
                    locations = sql.table
                else:
                    raise Exception(
                        "No results found with the get_following_locations_by_location query!"
                    )

        except Exception as e:
            self.LOG.error("get_locations_following_location: error={}".format(e))
            return []

        self.LOG.info(
            "get_locations_following_location: locations={0}".format(len(locations))
        )
        self.LOG.info("get_locations_following_location: END")
        return locations

    # gets a locations by stockID
    # input: StockID
    # output: Locations on success, [] on error
    def get_locations_by_stock(self, stockID: int) -> list:
        try:
            self.LOG.info("get_locations_by_stock: stockID={}".format(stockID))

            locations = []

            # get locations from stockID
            with SQL_Pull()(self.sql_config)() as sql:
                sql.execute(self.get_locations_with_stock_info_by_stockID, (stockID))

                if len(sql.table) > 0:
                    locations = sql.table
                else:
                    raise Exception(
                        "No results found with the get_locations_by_stock query!"
                    )

        except Exception as e:
            self.LOG.error("get_locations_by_stock: error={}".format(e))
            return []

        self.LOG.info("get_locations_by_stock: locations={0}".format(len(locations)))
        self.LOG.info("get_locations_by_stock: END")
        return locations

    # given a string location, gets its matching id if found
    def get_id_from_location(self, location: str) -> int:
        try:
            self.LOG.info("get_id_from_location: location={0}".format(location))

            Id = -1

            for key, value in self.locations.items():
                if location == value:
                    Id = key
                    break

        except Exception as e:
            self.LOG.error("get_id_from_location: error={}".format(e))
            self.LOG.info("get_id_from_location: END")
            return -1  # other error

        self.LOG.info("get_id_from_location: Id={}".format(Id))
        self.LOG.info("get_id_from_location: END")
        return Id  # no error


# UNIT TESTING
def main():
    return


if __name__ == "__main__":
    main()
