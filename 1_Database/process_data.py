import os
import pandas as pd
import glob
from pyxlsb import open_workbook
from typing import List, Dict, Set

# --- Configuration ---
INPUT_FOLDER = '1_Database/raw_xlsb_data' 
OUTPUT_FOLDER = 'processed_data'
MASTER_LIST_FILE = '1_Database/institutions.txt'
OUTPUT_FILENAME = os.path.join(OUTPUT_FOLDER, 'all_admissions_clean.csv')

def clean_numeric_value(value: any) -> int:
    """Cleans numeric data from report cells, handling ranges and blanks."""
    if value is None or str(value).strip() == '':
        return 0
    if isinstance(value, str) and '-' in value:
        parts = value.split('-')
        if len(parts) == 2 and parts[0].strip().isdigit() and parts[1].strip().isdigit():
            return 2 
    try:
        return int(float(str(value).replace(' ', '')))
    except (ValueError, TypeError):
        return 0

def process_single_file(filepath: str, institution_set: Set[str]) -> List[Dict]:
    """
    Processes a single .xlsb file, extracting granular program data.

    Args:
        filepath: The full path to the .xlsb file.
        institution_set: A set of known university/faculty names for lookups.

    Returns:
        A list of dictionaries, where each dictionary is a clean row of data.
    """
    filename = os.path.basename(filepath)
    print(f"Processing: {filename}")
    # === FILENAME EXTRACTION LOGIC ========
    # admissions_GENDER_YEAR_AGEGROUP.xlsb
    # * GENDER == men || women
    # ** YEAR == 2022 || 2023 || 2024
    # *** AGEGROUPS, se Vipunen.fi
    # ======================================
    try:
        parts = filename.replace('.xlsb', '').split('_')
        gender, year, age_part = parts[1].capitalize(), int(parts[2]), parts[3]
        if age_part == '18': age_group = '18 and under'
        elif age_part == '65': age_group = '65 and above'
        else: age_group = age_part
    except (IndexError, ValueError) as e:
        print(f"  - WARNING: Could not parse filename '{filename}'. Skipping. Error: {e}")
        return []

    clean_rows = []
    with open_workbook(filepath) as wb:
        try:
            sheet = wb.get_sheet(1)
        except IndexError:
            print(f"  - WARNING: Could not find any sheets in '{filename}'. Skipping.")
            return []

        current_university = None
        current_faculty = None

        for row in sheet.rows():
            row_values = [c.v for c in row]
            if len(row_values) < 4 or not isinstance(row_values[1], str) or row_values[1].strip() == '':
                continue

            name_cell = row_values[1].strip()
            total_applicants_cell = row_values[3]

            if clean_numeric_value(total_applicants_cell) > 0 or (isinstance(total_applicants_cell, str) and '-' in total_applicants_cell):
                if name_cell in institution_set:
                    if ',' not in name_cell:
                        current_university = name_cell
                        current_faculty = None
                    else:
                        current_faculty = name_cell
                # Special case for NDU Faculty
                elif name_cell == "Information saknas":
                    current_faculty = None
                else:
                    clean_rows.append({
                        'Year': year,
                        'Gender': gender,
                        'AgeGroup': age_group,
                        'University': current_university,
                        'Faculty': current_faculty,
                        'ProgramName': name_cell,
                        'FirstTimeApplicants': clean_numeric_value(row_values[2]),
                        'TotalApplicants': clean_numeric_value(total_applicants_cell),
                        'Admitted': clean_numeric_value(row_values[4] if len(row_values) > 4 else None)
                    })
    return clean_rows

def process_all_xlsb_files():
    """
    The main function. Processes all xlsb files and tracks Universities and Faculties using a Master List
    """
    # Master list to track Universities & Faculties
    try:
        with open(MASTER_LIST_FILE, 'r', encoding='utf-8') as f:
            institution_set = {line.strip() for line in f if line.strip()}
        print(f"Successfully loaded {len(institution_set)} institutions from master list.")
    except FileNotFoundError:
        print(f"FATAL ERROR: The master list '{MASTER_LIST_FILE}' was not found.")
        return

    # Find all source files
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)
    xlsb_files = glob.glob(os.path.join(INPUT_FOLDER, '*.xlsb'))
    if not xlsb_files:
        print(f"Error: No .xlsb files found in the '{INPUT_FOLDER}' directory.")
        return
    print(f"Found {len(xlsb_files)} files to process...")

    # Collect the results
    all_processed_data = []
    for filepath in xlsb_files:
        processed_rows = process_single_file(filepath, institution_set)
        all_processed_data.extend(processed_rows)

    # Finalize and save
    if not all_processed_data:
        print("\nPROCESSING FAILED: No data was extracted.")
        return

    final_df = pd.DataFrame(all_processed_data)
    final_df['Faculty'] = final_df['Faculty'].fillna('')
    final_df = final_df[['Year', 'Gender', 'AgeGroup', 'University', 'Faculty', 'ProgramName', 'FirstTimeApplicants', 'TotalApplicants', 'Admitted']]
    final_df.to_csv(OUTPUT_FILENAME, index=False, encoding='utf-8-sig')
    
    print("\n----------------------------------------------------")
    print("AUTOMATED DATA PROCESSING COMPLETE!")
    print(f"Successfully created '{OUTPUT_FILENAME}' with {len(final_df)} rows.")
    print("----------------------------------------------------")
    print("\nSample of the final, clean data:")
    print(final_df.head())


if __name__ == "__main__":
    process_all_xlsb_files()