# SQL & SSIS Analytics Platform and Pipeline
This project is a demonstration of a full data pipeline, developed to showcase the core competencies for a Data Specialist roles. It transforms a series of raw, difficult-to-use public data reports from [Vipunen.fi](https://vipunen.fi/en-gb/) into a clean, structured MS SQL database, processes it with SSIS and visualizes it with an interactive Power BI dashboard.


## Objective

This project simulates a full data pipeline, including:
1.  **Database Management:** Designing and deploying a relational database on MS SQL Server.
2.  **ETL Processes:** Extracting data from source files and loading it into the database.
3.  **BI & Reporting:** Creating an interactive dashboard with Power BI.

## Project Status

*Ground truth data aquired, next phase: loading the data into the SQL database.*


## Part 1: Data Sourcing & Automated Processing

*Representative of a real-world data engineering problem with aquired data from a public source.*

### 1. The Problem: A Manual and Inefficient Process

Sourcing admissions data from the Finnish education statistics portal, [Vipunen.fi](https://vipunen.fi/en-gb/) is gruesome and problematic as there is:

*   **No Raw Data Access:** The portal does not provide a direct way to download a complete, granular dataset. Instead `Vipunen` shows data using a Single-Page Application (SPA) that is then embeded into another web application, *Microsofts own Excel Online*.
    *   **WOPI:** Microsoft has developed Web Application Open Platform Interface (WOPI), this lets them host a version of an Office document in similar fashin to basic <iframes>. To my knowledge The WOPIframe then fetches and shows only what is necessary and heavily restricting any datamanipulation, bots and scrapers, *leaving us data scrapers in the dust.*

### 2. Data Sourcing & Acquisition
*   **Manual, Repetitive Work Required:** The only way to acquire detailed data was to manually filter and download dozens of individual report files. I choose a limited dataset 3 years, broken down by gender and 16 separate age groups. This required downloading and managing over 100 individual `.xlsb` report files. This manual process took hours (and as such is highly susceptible to human error), please excuse any inaccuracies!

*   **Using a systematic process** to gather the ground-truth data with a strong file naming convention, to enable automation later, each file was saved with a structured name (e.g., `admissions_men_2022_30-34.xlsb`).

### 3. The Data Transformation Challenge

Vipunens raw `.xlsb` files were formatted for visual reporting, not machine processing, and presented several technical challenges as they are Binary files rather than more common XML structured data found in `xlsx` files:

*   **Hierarchical Structure:** The data used visual indentation to represent the relationship between Universities, Faculties, and Programs rather than seperate cells.
*   **Inconsistent Data Types:** Numbers were stored as text, included ranges (`1-4`), and were mixed with `None` or blank values.
*   **Report Formatting:** The files contained extra header rows, titles, and empty rows for spacing that needed to be programmatically ignored.

### 4. The Solution: An Automated Python Pipeline

`1_Database/process_data.py` is a script that solves these challenges. It is a reusable asset that fully automates the cleaning of the raw report files.

The script performs the following steps:
1.  **Directly Reads `.xlsb` Files:** Uses the `pyxlsb` library to parse the binary Excel format, avoiding the need for manual conversion to CSV.
2.  **Parses Metadata from Filenames:** Intelligently extracts the `Year`, `Gender`, and `AgeGroup` for each file based on the established naming convention.
3.  **Identifies and Cleans Data Rows:** It iterates through each report, identifies rows containing actual data, and discards junk/header rows.
4.  **Parses Hierarchy and Extracts University:** It extracts the parent University name for each program, creating a clean, flat data structure.
5.  **Standardizes Data:** It cleans and converts all numeric data to integers and standardizes text fields.
6.  **Consolidates Data:** It combines the cleaned data from all ~100 source files into a single, master CSV file.

### 5. Part 1: Conclusion

The result of this pipeline is a single, clean file: `processed_data/all_admissions_clean.csv`.

*   **Structure:** A flat table with over 60,000 rows.
*   **Columns:** `Year`, `Gender`, `AgeGroup`, `University`, `ProgramName`, `FirstTimeApplicants`, `TotalApplicants`, `Admitted`.


