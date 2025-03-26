from .config import Config
from .sql_config import SQLConfig


# iot config
class IOTConfig(Config):
    def __init__(self, sql_config=SQLConfig) -> None:
        super().__init__(sql_config)

        # iot queries
        self.insert_iot = "INSERT INTO {database}.dbo.IOTSensorData (DateIn, Sensor, Temperature_Avg, Humidity_Avg, Battery_Avg) OUTPUT Inserted.ID VALUES (GETDATE(), ?, ?, ?, ?)"
        self.get_iot = "SELECT ID, DateIn, Sensor, Temperature_Avg, Humidity_Avg, Battery_Avg FROM {database}.dbo.IOTSensorData WHERE (DATEDIFF(SECOND, ?, DateIn) >= 0 and DATEDIFF(SECOND, ?, DateIn) <= 0) ORDER BY ID DESC OFFSET(?) ROWS FETCH NEXT ? ROWS ONLY"
        self.get_iot_by_sensor = ""
