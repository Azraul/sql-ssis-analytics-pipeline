import os
import pandas as pd
import glob
from pyxlsb import open_workbook

# --- Configuration ---
INPUT_FOLDER = '1_Database/raw_xlsb_data' 
OUTPUT_FOLDER = 'processed_data'
OUTPUT_FILENAME = os.path.join(OUTPUT_FOLDER, 'all_admissions_clean.csv')

# --- Helper function to clean numeric values ---
def clean_numeric_value(value):
    """Cleans the numeric data from the report cells."""
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

# --- Main Processing Logic ---
def process_all_xlsb_files():
    """Finds, reads, cleans, and combines all raw .xlsb report files."""
    if not os.path.exists(OUTPUT_FOLDER):
        os.makedirs(OUTPUT_FOLDER)

    xlsb_files = glob.glob(os.path.join(INPUT_FOLDER, '*.xlsb'))
    if not xlsb_files:
        print(f"Error: No .xlsb files found in the '{INPUT_FOLDER}' directory.")
        return

    print(f"Found {len(xlsb_files)} files to process...")
    all_processed_data = []

    for filepath in xlsb_files:
        filename = os.path.basename(filepath)
        print(f"Processing: {filename}")

        # =================================================================
        # === FILENAME EXTRACTION LOGIC
        # == Files come in two shapes
        # == admissions_GENDER_YEAR_AGEGROUP.xlsb
        # == admissions_total_YEAR.xlsb
        # ** GENDER == men || women
        # ** YEAR == 2022 || 2023 || 2024
        # ** AGEGROUPS, se Vipunen.fi
        # =================================================================
        try:
            parts = filename.replace('.xlsb', '').split('_')
            
            if parts[1] == 'total':
                gender = 'Total'
                year = int(parts[2])
                age_group = 'All Ages'
            else:
                gender = parts[1].capitalize()
                year = int(parts[2])
                age_part = parts[3]

                # Apply formatting to create clean labels for youngest / oldest
                if age_part == '18':
                    age_group = '18 and under'
                elif age_part == '65':
                    age_group = '65 and above'
                else:
                    # Handles both single agegroups ('19') and ranges ('25-29')
                    age_group = age_part
        except (IndexError, ValueError) as e:
            print(f"  - WARNING: Could not parse filename '{filename}'. Skipping. Error: {e}")
            continue

        with open_workbook(filepath) as wb:
            try:
                sheet = wb.get_sheet(1)
            except IndexError:
                print(f"  - WARNING: Could not find any sheets in '{filename}'. Skipping.")
                continue

            for row in sheet.rows():
                row_values = [c.v for c in row]
                if len(row_values) < 4: continue

                program_name_raw = row_values[1]
                first_time_raw = row_values[2]
                total_raw = row_values[3]
                admitted_raw = row_values[4] if len(row_values) > 4 else None

                if isinstance(program_name_raw, str) and program_name_raw.strip() != '':
                    if clean_numeric_value(total_raw) > 0 or (isinstance(total_raw, str) and '-' in total_raw):
                        
                        program_name_clean = program_name_raw.strip()
                        university_name = program_name_clean.split(',')[0].strip()
                        
                        all_processed_data.append({
                            'Year': year,
                            'Gender': gender,
                            'AgeGroup': age_group,
                            'University': university_name,
                            'ProgramName': program_name_clean,
                            'FirstTimeApplicants': clean_numeric_value(first_time_raw),
                            'TotalApplicants': clean_numeric_value(total_raw),
                            'Admitted': clean_numeric_value(admitted_raw)
                        })

    if not all_processed_data:
        print("\nPROCESSING FAILED: No data was extracted.")
        return

    final_df = pd.DataFrame(all_processed_data)
    final_df.to_csv(OUTPUT_FILENAME, index=False, encoding='utf-8-sig')
    
    print("\n----------------------------------------------------")
    print("AUTOMATED DATA PROCESSING COMPLETE!")
    print(f"Successfully created '{OUTPUT_FILENAME}' with {len(final_df)} rows.")
    print("----------------------------------------------------")
    print("\nSample of the final, clean data:")
    print(final_df.head())

# Run
if __name__ == "__main__":
    process_all_xlsb_files()