from .config import Config
from .sql_config import SQLConfig


class ProductionLineConfig(Config):
    # CONSTRUCTOR
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        ## Production Line Queries

        # Returns all active production lines
        self.get_active_production_lines = "SELECT [ID],[Line],[Description],[ProductionShare],[Status] FROM {database}.[dbo].[ProductionLines] where Status = 11"
