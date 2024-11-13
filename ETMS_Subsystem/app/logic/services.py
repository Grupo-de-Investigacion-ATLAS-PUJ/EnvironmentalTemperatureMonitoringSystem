import plotly.graph_objs as go
import pandas as pd
import numpy as np
from app.data.models import query_data
import json
import os
from app.data.models import query_historical_data


SETTINGS_FILE = "app/settings.json"

def get_thresholds():
    """
    Obtiene los umbrales de temperatura desde el archivo de configuración.
    Si el archivo no existe, devuelve valores por defecto.
    """
    if not os.path.exists(SETTINGS_FILE):
        return {"max_threshold": 60, "min_threshold": -80}  # Defaults

    with open(SETTINGS_FILE, "r") as file:
        return json.load(file)

def set_thresholds(max_threshold, min_threshold):
    """
    Establece nuevos umbrales de temperatura y los guarda en el archivo de configuración.
    """
    thresholds = {"max_threshold": max_threshold, "min_threshold": min_threshold}
    with open(SETTINGS_FILE, "w") as file:
        json.dump(thresholds, file)

def create_performance_graph():
    """
    Genera un gráfico interactivo de rendimiento del sistema utilizando Plotly.
    Muestra la temperatura medida por los sensores en función del tiempo.
    """
    df = query_data()

    # Parse the 'time' column to datetime
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    df = df.dropna(subset=['time'])  # Drop rows with invalid time values

    # Extract the numeric part from the name column
    df['sensor_number'] = df['name'].str.extract(r'voltage_(\d+)\.value$')[0].astype(int)

    # Filter out excluded channels 48, 49, 50, and 51
    df = df[df['sensor_number'] < 48]

    fig = go.Figure()

    # Group by 'sensor_number' to plot each temperature channel
    for sensor_number, group in df.groupby('sensor_number'):
        fig.add_trace(go.Scatter(
            x=group['time'],
            y=group['original_value_float'],
            mode='lines+markers',
            name=f"Sensor {sensor_number}"  # Use the simplified sensor name
        ))

    fig.update_layout(
        title='System Performance',
        xaxis_title='Time',
        yaxis_title='Temperature (C°)',
        legend_title="Sensors"
    )
    
    return fig

def create_trend_graph():
    """
    Genera un gráfico de tendencia promedio de temperatura.
    Calcula la media de las temperaturas de todos los sensores a lo largo del tiempo.
    """
    df = query_data()

    # Parse the 'time' column to datetime
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    df = df.dropna(subset=['time'])  # Drop rows with invalid time values

    # Extract the numeric part from the name column
    df['sensor_number'] = df['name'].str.extract(r'voltage_(\d+)\.value$')[0].astype(int)

    # Filter out excluded channels 48, 49, 50, and 51
    df = df[df['sensor_number'] < 48]

    # Set the 'time' column as the index for resampling
    df.set_index('time', inplace=True)

    # Resample the data to each second and forward-fill missing values
    resampled_df = df.groupby('sensor_number')['original_value_float'].resample('1s').ffill().reset_index()

    # Calculate the average across all sensors for each second
    avg_df = resampled_df.groupby('time')['original_value_float'].mean().reset_index()

    # Plot the average trend over time
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=avg_df['time'],
        y=avg_df['original_value_float'],
        mode='lines',
        name='Average Trend'
    ))

    fig.update_layout(
        title='Average Trend Analysis',
        xaxis_title='Time',
        yaxis_title='Average Temperature (C°)',
        legend_title="Trend"
    )

    return fig


# Define alert thresholds
temperature_HIGH_THRESHOLD = 80
temperature_LOW_THRESHOLD = -60
excluded_channels = [48, 49, 50, 51]

def filter_sensors(df):
    """
    Filtra los sensores excluyendo los canales 48, 49, 50 y 51.
    """
    df['sensor_number'] = df['name'].str.extract(r'voltage_(\d+)\.value$')[0].astype(int)
    return df[~df['sensor_number'].isin(excluded_channels)]

def get_temperature_highlights():
    df = query_data()
    df = filter_sensors(df)

    if df.empty:
        return {"highest": None, "lowest": None}

    highest = df['original_value_float'].max()
    lowest = df['original_value_float'].min()

    return {"highest": highest, "lowest": lowest}


def generate_alerts():
    """
    Genera alertas para los sensores que exceden los umbrales configurados.
    """
    thresholds = get_thresholds()
    max_threshold = thresholds['max_threshold']
    min_threshold = thresholds['min_threshold']

    df = query_data()
    alerts = []

    df['name'] = df['name'].astype(str)
    df['channel_number'] = df['name'].str.extract(r'voltage_(\d+)\.value$')[0]

    excluded_channels = ['48', '49', '50', '51']
    df = df[~df['channel_number'].isin(excluded_channels)]

    df['time'] = pd.to_datetime(df['time'], utc=True, errors='coerce')
    df['sensor_number'] = df['channel_number'].astype(int)

    for _, row in df.iterrows():
        temperature = row['original_value_float']
        sensor_number = row['sensor_number']
        timestamp = row['time']

        if pd.isna(timestamp):
            alert_time = "Unknown time"
        else:
            alert_time = timestamp.strftime("%Y-%m-%d %H:%M:%S")

        if temperature > max_threshold:
            alerts.append(
                f"Sensor {sensor_number} exceeded the threshold at {alert_time} with a temperature of {temperature:.2f}°C."
            )
        elif temperature < min_threshold:
            alerts.append(
                f"Sensor {sensor_number} fell below the threshold at {alert_time} with a temperature of {temperature:.2f}°C."
            )

    return alerts

def create_historical_graph(start_datetime, end_datetime):
    """
    Genera un gráfico histórico dentro de un rango de tiempo especificado.
    Muestra las temperaturas por sensor y una línea para el promedio general.
    """
    df = query_historical_data(start_datetime, end_datetime)

    if df.empty:
        return go.Figure(
            layout=go.Layout(
                title="No data available for the selected range",
                xaxis_title="Time",
                yaxis_title="Temperature (C°)"
            )
        )

    # Parse the 'time' column to datetime
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    df = df.dropna(subset=['time'])  # Drop rows with invalid time values

    # Extract the numeric part from the sensor name column
    df['sensor_number'] = df['name'].str.extract(r'voltage_(\d+)\.value$')[0].astype(int)

    # Calculate the overall average
    overall_average = df['original_value_float'].mean()

    fig = go.Figure()

    # Group by 'sensor_number' to plot each sensor's data
    for sensor_number, group in df.groupby('sensor_number'):
        fig.add_trace(go.Scatter(
            x=group['time'],
            y=group['original_value_float'],
            mode='lines+markers',
            name=f"Sensor {sensor_number}"
        ))

    # Add a horizontal line for the average
    fig.add_trace(go.Scatter(
        x=df['time'],  # Use the same x-axis for consistency
        y=[overall_average] * len(df['time']),  # A constant line at the average
        mode='lines',
        name=f"Average ({overall_average:.2f}°C)",
        line=dict(color='red', dash='dash')  # Dashed red line
    ))

    fig.update_layout(
        title='Historical Data Viewer',
        xaxis_title='Time',
        yaxis_title='Temperature (C°)',
        legend_title="Sensors"
    )

    return fig

    """
    Generate a Plotly graph for the historical data within the specified time range.
    """
    df = query_historical_data(start_datetime, end_datetime)

    if df.empty:
        return go.Figure(
            layout=go.Layout(
                title="No data available for the selected range",
                xaxis_title="Time",
                yaxis_title="Temperature (C°)"
            )
        )

    # Parse the 'time' column to datetime
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    df = df.dropna(subset=['time'])  # Drop rows with invalid time values

    # Extract the numeric part from the sensor name column
    df['sensor_number'] = df['name'].str.extract(r'voltage_(\d+)\.value$')[0].astype(int)

    fig = go.Figure()

    # Group by 'sensor_number' to plot each sensor's data
    for sensor_number, group in df.groupby('sensor_number'):
        fig.add_trace(go.Scatter(
            x=group['time'],
            y=group['original_value_float'],
            mode='lines+markers',
            name=f"Sensor {sensor_number}"
        ))

    fig.update_layout(
        title='Historical Data Viewer',
        xaxis_title='Time',
        yaxis_title='Temperature (C°)',
        legend_title="Sensors"
    )

    return fig