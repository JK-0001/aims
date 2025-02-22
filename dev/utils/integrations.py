import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
from utils.database import init_db

def parse_apple_health_data(file_path):
    """
    Parse Apple Health export file (XML) and return a DataFrame.
    """
    tree = ET.parse(file_path)
    root = tree.getroot()

    data = []
    for record in root.findall('.//Record'):
        record_data = {
            'type': record.attrib.get('type'),
            'value': record.attrib.get('value'),
            'start_date': record.attrib.get('startDate'),
            'end_date': record.attrib.get('endDate'),
        }
        data.append(record_data)

    return pd.DataFrame(data)

def load_apple_health_data(file_path):
    """
    Load Apple Health data into the SQLite database.
    """
    df = parse_apple_health_data(file_path)
    conn = init_db()
    c = conn.cursor()

    # Filter relevant data (e.g., sleep, steps)
    sleep_data = df[df['type'].str.contains('SleepAnalysis', na=False)]
    steps_data = df[df['type'].str.contains('StepCount', na=False)]

    # Save to database
    for _, row in sleep_data.iterrows():
        c.execute("INSERT INTO health_data (date, sleep) VALUES (?, ?)",
                  (row['start_date'], row['value']))
    for _, row in steps_data.iterrows():
        c.execute("INSERT INTO health_data (date, steps) VALUES (?, ?)",
                  (row['start_date'], row['value']))

    conn.commit()
    st.success("Apple Health data loaded successfully!")