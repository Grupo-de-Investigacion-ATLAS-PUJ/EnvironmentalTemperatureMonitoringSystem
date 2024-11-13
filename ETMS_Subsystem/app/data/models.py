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
    """
    Consulta datos de la base de datos de InfluxDB dentro de un rango de tiempo específico.
    El rango de tiempo se obtiene de la sesión (predeterminado a 1 minuto).
    
    Returns:
        DataFrame: Contiene columnas específicas ('time', 'name', 'original_value_float').
                  Devuelve un DataFrame vacío si no hay resultados.
    """


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
    """
    Consulta información general de los sensores desde la base de datos `sensors_data`.
    
    Returns:
        list: Lista de puntos de datos resultantes de la consulta.
    """
    query2 = "SELECT * FROM sensor_info"
    result = client2.query(query2)
    return list(result.get_points())

def query_historical_data(start_datetime, end_datetime):
    """
    Consulta datos históricos de InfluxDB en un rango de tiempo específico.
    
    Args:
        start_datetime (str): Fecha y hora de inicio en formato ISO 8601.
        end_datetime (str): Fecha y hora de fin en formato ISO 8601.
    
    Returns:
        DataFrame: Contiene columnas específicas ('time', 'name', 'original_value_float').
                  Devuelve un DataFrame vacío si no hay resultados.
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