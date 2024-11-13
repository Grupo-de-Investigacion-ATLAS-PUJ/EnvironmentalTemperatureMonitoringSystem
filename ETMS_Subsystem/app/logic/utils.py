# app/logic/utils.py

def filter_sensors_by_group(df, group):
    """Filter sensors based on the selected group."""
    if group == "Pixels":
        df = df[df['sensor_number'].between(0, 23)]
    elif group == "Strips":
        df = df[df['sensor_number'].between(24, 47)]
    # If 'All' is selected, no filtering is needed
    return df
