import config
from influxdb import InfluxDBClient
import pandas as pd
from flask import session

# InfluxDB client setup using credentials
client = InfluxDBClient(
    host=config.INFLUXDB_HOST,
    port=config.INFLUXDB_PORT,
    username=config.INFLUXDB_USER,
    password=config.INFLUXDB_PASSWORD,
    database=config.INFLUXDB_DATABASE
)

def query_data():
    # Get the time range from the session, default to 1 minute
    time_range = session.get('time_range', '1m')
    query = f"SELECT * FROM TEMP_SENSORS.TEMP_SENSORS WHERE variabletype='FwElmbAi' AND time > now() - {time_range}"
    result = client.query(query)
    
    df = pd.DataFrame(list(result.get_points()))
    
    if df.empty:
        print("No data available for the specified query.")
        return pd.DataFrame(columns=['time', 'name', 'original_value_float'])
    
    # Return the relevant columns: time, name, and original_value_float
    return df[['time', 'name', 'original_value_float']]

client2 = InfluxDBClient(
    host=config.INFLUXDB_HOST,
    port=config.INFLUXDB_PORT,
    username=config.INFLUXDB_USER,
    password=config.INFLUXDB_PASSWORD,
    database="sensors_data"
)

def get_sensor_info():
    query2 = "SELECT * FROM sensor_info"
    result = client2.query(query2)
    return list(result.get_points())

def query_historical_data(start_datetime, end_datetime):
    """
    Query historical data based on the given start and end datetime.
    """
    query = f"""
        SELECT * FROM TEMP_SENSORS.TEMP_SENSORS 
        WHERE time >= '{start_datetime}' AND time <= '{end_datetime}'
    """
    result = client.query(query)
    
    df = pd.DataFrame(list(result.get_points()))
    
    if df.empty:
        print("No data available for the specified query.")
        return pd.DataFrame(columns=['time', 'name', 'original_value_float'])
    
    # Return the relevant columns: time, name, and original_value_float
    return df[['time', 'name', 'original_value_float']]