# Property Data ETL Pipeline & Normalization

This project contains a Python-based ETL (Extract, Transform, Load) script to process a nested, monolithic JSON file. It normalizes the data and loads it into a clean, relational MySQL database.

**Submitted by: Animesh Bhatt**

---

## Database Design

The original JSON file was a monolithic, nested structure. To normalize this, I adopted a relational **3rd Normal Form (3NF)** model. This design separates distinct entities into their own tables, reducing redundancy and improving data integrity.

* `properties` (Parent Table): This table holds the core, one-to-one attributes of a property (e.g., `Address`, `City`, `SQFT_Total`). The `property_id` is its **Primary Key**, and the `address` column has a `UNIQUE` constraint to prevent duplicate property entries.
* `valuations` (Child Table): This table stores the one-to-many valuation records from the nested "Valuation" list in the JSON.
* `hoa` (Child Table): This table stores the one-to-many HOA records from the nested "HOA" list.
* `rehab` (Child Table): This table stores the one-to-many rehab estimate records from the nested "Rehab" list.

All three child tables use `property_id` as a **Foreign Key** to link back to the `properties` table, creating a clear and efficient relational structure.

## ETL Logic

The data pipeline is handled by `scripts/load_data.py`, which follows a sequential ETL process:

1.  **Extract**: The script reads the raw `data/fake_property_data_new.json` file into a pandas DataFrame.
2.  **Transform**:
    * **Core Data**: It selects the core property columns (e.g., `Address`, `City`, `Zip`) and creates a clean `properties_df`, dropping any duplicates based on the `Address`.
    * **Data Cleaning**: It cleans the `SQFT_Total` column (which is a string like "5649 sqft") by removing the text, stripping whitespace, and converting it to an integer.
3.  **Load (Multi-Stage Transaction)**:
    * **Stage 1 (Parent)**: The clean `properties_df` is loaded into the `properties` table. This transaction is committed immediately so that the database generates the `property_id` for each row.
    * **Stage 2 (Mapping)**: The script queries the `properties` table to create a Python dictionary that maps each property's `Address` to its new `property_id` (e.g., `{'875 Davis...': 1, ...}`).
    * **Stage 3 (Children)**: The script iterates through the original DataFrame, un-nests the `Valuation`, `HOA`, and `Rehab` lists, and uses the `address_to_id_map` to link each child record to its correct `property_id`.
    * **Stage 4 (Final Commit)**: All child records are loaded into their respective tables (`valuations`, `hoa`, `rehab`), and this final transaction is committed.

The script also uses `INSERT IGNORE` (in the `scripts/load_data.py` file) and `CREATE TABLE IF NOT EXISTS` (in `sql/01_create_schema.sql`) to make the pipeline **idempotent**, meaning it can be re-run safely without crashing on "Duplicate entry" errors.

---

## After Execution Glimpse
## After Execution Glimpse
![Terminal Output Screenshot](https://github.com/animeshbhatt651/Data-Engineering-Assessment/blob/main/Snapshots/Screenshot%202025-10-23%20at%2002.07.15.png)

![Terminal Output Screenshot](https://github.com/animeshbhatt651/Data-Engineering-Assessment/blob/main/Snapshots/Screenshot%202025-10-23%20at%2003.15.10.png)


Here is the terminal output after a successful ETL run, showing the records being processed and loaded.

```bash
(venv) $ python scripts/load_data.py
MySQL Database connection successful
Extracting data from data/fake_property_data_new.json...
Extracted 9788 records.
--- JSON Columns ---
Index(['Property_Title', 'Address', 'Reviewed_Status', 'Most_Recent_Status',
       'Source', 'Market', 'Occupancy', 'Flood', 'Street_Address', 'City',
       ...
       'Neighborhood_Rating', 'Latitude', 'Longitude', 'Subdivision', 'Taxes',
       'Selling_Reason', 'Seller_Retained_Broker', 'Final_Reviewer',
       'School_Average', 'Valuation', 'HOA', 'Rehab'],
      dtype='object', length=41)
----------------------
Starting data transformation and loading...
Preparing 'properties' table...
Loaded/skipped 9788 records into 'properties' (pending commit).
Mapping properties to new IDs...
Un-nesting and preparing child tables...
Loading 24898 'valuation' records...
Loaded/skipped 24898 records into 'valuations' (pending commit).
Loading 10100 'hoa' records...
Loaded/skipped 10100 records into 'hoa' (pending commit).
Loading 20219 'rehab' records...
Loaded/skipped 20219 records into 'rehab' (pending commit).
Committing all changes to the database...
All data loaded successfully.
ETL process finished.

---


## Getting Started

Here's how you can get the project running on your local machine, from installing MySQL to running the script.

### Prerequisites(that i have used)

* **VS Code**
* **Python 3.8++**
* **Git**


---

### Step 1: Install and Set Up MySQL Server

You need a MySQL 8.0 server running on your computer.

**On macOS (using Homebrew as i have done on this mac os):**
```bash

brew install mysql@8.0

brew services start mysql@8.0
