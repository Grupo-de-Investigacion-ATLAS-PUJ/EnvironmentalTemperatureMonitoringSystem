# app/logic/utils.py

def filter_sensors_by_group(df, group):
    """
    Filtra los sensores del DataFrame según el grupo seleccionado.

    Args:
        df (DataFrame): DataFrame que contiene los datos de los sensores, 
                        incluyendo la columna 'sensor_number' con los números de los sensores.
        group (str): Grupo seleccionado para filtrar. Puede ser "Pixels", "Strips" o "All".

    Returns:
        DataFrame: DataFrame filtrado que contiene solo los sensores pertenecientes al grupo especificado.
    """
    """Filter sensors based on the selected group."""
    if group == "Pixels":
        df = df[df['sensor_number'].between(0, 23)]
    elif group == "Strips":
        df = df[df['sensor_number'].between(24, 47)]
    # If 'All' is selected, no filtering is needed
    return df
