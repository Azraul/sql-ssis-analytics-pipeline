# SQL & SSIS Analytics Platform and Pipeline
This project is a demonstration of a full data pipeline, developed to showcase the core competencies for a Data Specialist roles. It transforms a series of raw, difficult-to-use public data reports from [Vipunen.fi](https://vipunen.fi/en-gb/) into a clean, structured MS SQL database, processes it with SSIS and visualizes it with an interactive Power BI dashboard.


## Objective

This project simulates a full data pipeline, including:
1.  **Database Management:** Designing and deploying a relational database on MS SQL Server.
2.  **ETL Processes:** Extracting data from source files and loading it into the database.
3.  **BI & Reporting:** Creating an interactive dashboard with Power BI.

## Project Status

*Ground truth data aquired, next phase: loading the data into the SQL database.*

## Part 1: Data Sourcing & Automated Transformation

*This initial phase is a case study in solving a real-world data engineering problem: acquiring and cleaning messy, inconsistent data from a protected public source.*

### 1. The Business Problem: A Manual and Inefficient Process

The project began by sourcing admissions data from the Finnish education statistics portal, [Vipunen.fi](https://vipunen.fi/en-gb/). Initial investigation revealed a significant business challenge:

*   **No Raw Data Access:** Instead of providing raw data files, the portal utilizes a Single-Page Application (SPA) to embed a Microsoft Excel Online instance. This architecture, likely using Microsoft's WOPI protocol, is designed for interactive user reports, creating a significant barrier to automated data extraction.
*   **Manual, Repetitive Work Required:** The only way to acquire detailed data was to manually filter and download dozens of individual report files. I choose a limited dataset of 3 years, broken down by gender and 16 separate age groups. This required downloading and managing over 100 individual `.xlsb` report files.

### 2. The Data Transformation Challenge

Vipunens raw `.xlsb` files were formatted for visual reporting, not machine processing, and presented several technical challenges as they are Binary files rather than more common XML structured data found in `xlsx` files:

*   **Binary Format:** The data was in a binary `.xlsb` format, making it unreadable by standard text-based parsers.
*   **Hierarchical Structure:** The data used visual indentation to represent the relationship between Universities, Faculties, and Programs rather than seperate cells.
*   **Inconsistent Data Types:** Numbers were stored as text, included ranges (`1-4`), and were mixed with `None` or blank values.
*   **Report Formatting:** The files contained extra header rows, titles, and empty rows for spacing that needed to be programmatically ignored.

### 3. The Solution: An Automated Python Pipeline

`1_Database/process_data.py` is a script that solves these challenges. It is a reusable asset that fully automates the cleaning of the raw report files.

The script performs the following steps:
1.  **Loads a Master Institution List:** Reads the `institutions.txt` file to know all valid University and Faculty names in advance.
2.  **Directly Reads `.xlsb` Files:** Uses the `pyxlsb` library to parse the binary Excel format, avoiding the need for manual conversion to CSV.
3.  **Parses Metadata from Filenames:** Intelligently extracts the `Year`, `Gender`, and `AgeGroup` for each file based on the established naming convention.
4.  **Executes a State Machine:** Iterates through each report, using the master list to understand the current context.
5.  **Extracts Granular Data:** Saves only the most detailed, program-level rows, discarding the aggregated total rows to ensure data integrity.
6.  **Standardizes and Consolidates:** Cleans and converts all data to the correct types and combines the data from all ~50 source files into a single master CSV.

*The final version was the result of an iterative development and debugging process. Initial hypotheses based on visual cues (like indentation or comma counts) proved insufficient against the complex and inconsistent nature of the data. The definitive solution was to engineer a "state machine" parser that uses a master list of institutions (`institutions.txt`) as its source of truth. This allows the script to reliably distinguish between institutional context rows and granular data rows.*

### 4. The Result: An Analysis-Ready Data Asset

The outcome of this automated pipeline is a single, clean file: `processed_data/all_admissions_clean.csv`.

*   **Structure:** A flat, "tidy" table with over 60,000 rows of granular data.
*   **Columns:** `Year`, `Gender`, `AgeGroup`, `University`, `Faculty`, `ProgramName`, `FirstTimeApplicants`, `TotalApplicants`, `Admitted`.
*   **Value:** This clean, consolidated CSV file eliminates the initial data sourcing problem

### 5. Database Design

The final step of preparation was to design and deploy a SQL database schema for storing this data efficiently for analysis. Wanting to learn more I choose a **Star Schema**, this is supposed to be industry best practice for BI and a nice learning opportunity. It uses small efficient dimension tables for descriptive data (DimGender, DimUniversity, etc.,).

To also simulate a professional environment, with environment variables, `SQLCMD` was used for DatabaseNames to be reusable.

## Part 2: ETL Pipeline with SSIS

The next phase was to build an enterprise-grade ETL (Extract, Transform, Load) pipeline to populate the database using **SQL Server Integration Services (SSIS)**.

The complete SSIS solution can be found in the `2_ETL_SSIS/` directory and includes:

*   `SQL_SSIS_Analytics_Pipeline_Project.sln` - The Visual Studio solution file.
*   `Package.dtsx` - The SSIS package file containing all the ETL logic described below.

A step-by-step explanation of the ETL architecture, including screenshots of the Control Flow and Data Flows, is available in the [ETL Process Walkthrough](./2_ETL_SSIS/etl_walkthrough.md).

## Part 3: BI Reporting & Visualization (Next Steps)

The final phase of this project will be to connect to the newly populated SQL database and build an interactive dashboard using **Microsoft Power BI**. This dashboard will be designed to provide clear, actionable insights into the admissions data, showcasing skills in data analysis, DAX, and data visualization.