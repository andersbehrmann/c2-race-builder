import csv
import os
import streamlit as st
from tempfile import NamedTemporaryFile, TemporaryDirectory
import zipfile

def read_csv(file_path):
    heats = {}
    with open(file_path, mode='r') as file:
        reader = csv.reader(file)
        next(reader)  # Skip header row if there is one
        for row in reader:
            heat_number, lane_number, team_name = row
            if heat_number not in heats:
                heats[heat_number] = []
            heats[heat_number].append((lane_number, team_name))
    return heats

def write_files(heats, output_dir, duration, event_name, type):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for heat_number, entries in heats.items():
        file_path = os.path.join(output_dir, f"Heat{heat_number}.rac2")
        with open(file_path, mode='w') as file:
            file.write('{\n')
            file.write('    "race_definition": {\n')
            file.write(f'        "{type}": [\n')
            for lane_number, team_name in entries:
                file.write('            {\n')
                file.write('                "class_name": "",\n')
                file.write(f'                "lane_number": {lane_number},\n')
                file.write(f'                "name": "{team_name}",\n')
                file.write('                "participants": [\n')
                file.write('                    {\n')
                file.write('                        "name": "A1"\n')
                file.write('                    },\n')
                file.write('                    {\n')
                file.write('                        "name": "A2"\n')
                file.write('                    }\n')
                file.write('                ]\n')
                file.write('            },\n')
            file.write('        ],\n')
            file.write('        "c2_race_id": "",\n')
            file.write(f'        "duration": {duration},\n')
            file.write('        "duration_type": "time",\n')
            file.write(f'        "event_name": "{event_name}",\n')
            file.write(f'        "name_long": "Heat {heat_number}",\n')
            file.write(f'        "name_short": "H{heat_number}",\n')
            file.write('        "race_id": "",\n')
            file.write('        "race_type": "team calorie score",\n')
            file.write('        "round": 1,\n') 
            file.write('        "split_value": 60,\n')
            file.write('        "team_scoring": "sum",\n')
            file.write(f'        "team_size": 2,\n')
            file.write('        "time_cap": 0\n')
            file.write('    }\n')
            file.write('}\n')

def main():
    st.set_page_config(page_title="CSV to .rac2 Converter", layout="wide")
    
    # Add custom CSS
    st.markdown("""
        <style>
        h1 {color: #ffffff}
        p {color: #ffffff}
        .stButton p {color: #000000}
        .stMain {background-color: #000000}
        .main {
            background-color: #000000;
            border-radius: 10px;
            color: #ffffff
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.title("CSV to .rac2 Converter")
    st.markdown("This app converts a csv file to .rac2 files. The csv needs to have three columns:\n1. Heat Number\n2. Lane Number\n3. Team Name\n\nThe app will create a .rac2 file for each heat and compress them in a zip-file that you can download.")


    uploaded_file = st.file_uploader("Choose a CSV file", type="csv")
    duration_minutes = st.number_input("Duration (minutes)", min_value=1, step=1)
    event_name = st.text_input("Event Name", value="")
    type = st.selectbox("Type", ["boats", "bikes"], index=0)
    ## number_of_athletes = st.number_input("Number of Athletes in each lane", min_value=1, step=1)

    if st.button("Convert"):
        if uploaded_file is not None and duration_minutes and event_name:
            duration_seconds = duration_minutes * 60
            with NamedTemporaryFile(delete=False) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_file_path = tmp_file.name

            heats_data = read_csv(tmp_file_path)
            
            with TemporaryDirectory() as tmp_dir:
                write_files(heats_data, tmp_dir, duration_seconds, event_name, type)
                
                zip_path = os.path.join(tmp_dir, "output_files.zip")
                with zipfile.ZipFile(zip_path, 'w') as zipf:
                    for root, _, files in os.walk(tmp_dir):
                        for file in files:
                            if file.endswith(".rac2"):
                                zipf.write(os.path.join(root, file), arcname=file)
                
                with open(zip_path, "rb") as zip_file:
                    st.download_button(
                        label="Download ZIP",
                        data=zip_file,
                        file_name="output_files.zip",
                        mime="application/zip"
                    )
        else:
            st.error("Please upload a CSV file, specify duration and event name.")

if __name__ == "__main__":
    main()