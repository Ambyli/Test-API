from .config import Config
from .sql_config import SQLConfig


class LocationConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # # Location Functions
        # input: Location
        # output: [[ID, Location, Core100, Core200, Core300]]
        self.get_location_goal_by_location = "SELECT ID, Location, Core100, Core200, Core300 FROM {database}.dbo.CoreGoals WHERE Location = ? ORDER BY ID DESC"
        # input: N/A
        # output: [[ID, Location, Core100, Core200, Core300]]
        self.get_location_goals = "SELECT ID, Location, Core100, Core200, Core300 FROM {database}.dbo.CoreGoals ORDER BY ID DESC"
        # input: Location
        # output: [[ID, Location, PreviousLocation]]
        self.get_previous_locations_by_location = "SELECT ID, LocationID, PreviousLocationID FROM {database}.dbo.PreviousLocations WHERE LocationID = ? and Status = 16 ORDER BY ID ASC"
        # input: Location
        # output: [[ID, Location, FollowingLocation]]
        self.get_following_locations_by_location = "SELECT ID, LocationID, FollowingLocationID FROM {database}.dbo.FollowingLocations WHERE LocationID = ? and Status = 16 ORDER BY ID ASC"
        # input: StockID
        # output: [[ID, Location, ...]]
        self.get_locations_with_stock_info_by_stockID = "SELECT COUNT(a.ID) as Units, a.Location as LocationID, b.Location, c.Location as Parent FROM {database}.dbo.StockStorage as a LEFT JOIN {database}.dbo.Locations as b ON a.Location = b.ID OUTER APPLY (SELECT Location FROM {database}.dbo.Locations WHERE ID = b.Parent) as c WHERE a.StockID = ? and a.Status = 11 and a.Removed IS NULL GROUP BY a.Location, b.Location, c.Location"
        # input: StatusID
        # output: [[ID, Location, ...]]
        self.get_locations_from_status = "SELECT ID, Location, Color, Parent, Description, Status, Weight FROM {database}.dbo.Locations WHERE Status = ? ORDER BY Location ASC"
