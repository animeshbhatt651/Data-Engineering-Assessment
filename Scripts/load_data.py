import pandas as pd
import mysql.connector
import json

def get_db_connection():

    try:
        conn = mysql.connector.connect(
            host='localhost',
            port=3306,
            user='root',
            password='Animesh@property',
            database='property_db'
        )
        print("MySQL Database connection successful")
        return conn
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def extract_data(json_file_path):
    
    print(f"Extracting data from {json_file_path}...")
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
        print(f"Extracted {len(df)} records.")
        return df
    except FileNotFoundError:
        print(f"ERROR: JSON file not found at {json_file_path}")
        return None
    except json.JSONDecodeError:
        print(f"ERROR: Could not decode JSON. Check the file format.")
        return None

def transform_and_load(df, conn):
    
    cursor = conn.cursor()
    print("Starting data transformation and loading...")

    try:
        
        print("Preparing 'properties' table...")
        prop_cols = [
            'Address', 'Street_Address', 'City', 'State', 'Zip', 
            'Property_Type', 'Year_Built', 'SQFT_MU', 'SQFT_Total', 'Bed', 'Bath'
        ]
        properties_df = df[prop_cols].drop_duplicates(subset=['Address'])
        
        properties_df = properties_df.copy()
        properties_df['SQFT_Total'] = (
            properties_df['SQFT_Total']
            .str.replace(' sqft', '', regex=False)
            .str.strip()
            .fillna(0)
            .astype(int)
        )
        properties_df['Year_Built'] = properties_df['Year_Built'].fillna(0).astype(int)
        properties_df['SQFT_MU'] = properties_df['SQFT_MU'].fillna(0).astype(int)
        properties_df['Bed'] = properties_df['Bed'].fillna(0).astype(int)
        properties_df['Bath'] = properties_df['Bath'].fillna(0).astype(int)

        properties_sql = """
            INSERT IGNORE INTO properties 
            (address, street_address, city, state, zip_code, 
             property_type, year_built, sqft_mu, sqft_total, beds, baths)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        properties_tuples = [tuple(x) for x in properties_df.to_numpy()]
        
        cursor.executemany(properties_sql, properties_tuples)
        print(f"Loaded/skipped {cursor.rowcount} records into 'properties' (pending commit).")

       
        print("Mapping properties to new IDs...")
        conn.commit() 
        
        id_mapping_df = pd.read_sql("SELECT property_id, address FROM properties", conn)
        address_to_id_map = dict(zip(id_mapping_df['address'], id_mapping_df['property_id']))

        print("Un-nesting and preparing child tables...")
        valuations_to_load = []
        hoas_to_load = []
        rehabs_to_load = []

        for index, row in df.iterrows():
            pid = address_to_id_map.get(row['Address'])
            if not pid:
                continue

            if isinstance(row['Valuation'], list):
                for valuation in row['Valuation']: 
                    valuations_to_load.append((
                        pid, valuation.get('List_Price'), valuation.get('Zestimate'),
                        valuation.get('Rent_Zestimate'), valuation.get('Redfin_Value'),
                        valuation.get('Expected_Rent'), valuation.get('Previous_Rent'),
                        valuation.get('ARV'), valuation.get('Low_FMR'), valuation.get('High_FMR')
                    ))
            
            if isinstance(row['HOA'], list):
                for hoa in row['HOA']:
                    hoas_to_load.append((
                        pid, hoa.get('HOA'), hoa.get('HOA_Flag')
                    ))
            
            if isinstance(row['Rehab'], list):
                for rehab in row['Rehab']:
                    rehabs_to_load.append((
                        pid, rehab.get('Underwriting_Rehab'), rehab.get('Rehab_Calculation'),
                        rehab.get('Paint'), rehab.get('Flooring_Flag'), rehab.get('Foundation_Flag'),
                        rehab.get('Roof_Flag'), rehab.get('HVAC_Flag'), rehab.get('Kitchen_Flag'),
                        rehab.get('Bathroom_Flag'), rehab.get('Appliances_Flag'),
                        rehab.get('Windows_Flag'), rehab.get('Landscaping_Flag'), rehab.get('Trashout_Flag')
                    ))

        if valuations_to_load:
            print(f"Loading {len(valuations_to_load)} 'valuation' records...")
            valuation_sql = """
                INSERT IGNORE INTO valuations 
                (property_id, list_price, zestimate, rent_zestimate, redfin_value, 
                 expected_rent, previous_rent, arv, low_fmr, high_fmr)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(valuation_sql, valuations_to_load)
            print(f"Loaded/skipped {cursor.rowcount} records into 'valuations' (pending commit).")

        if hoas_to_load:
            print(f"Loading {len(hoas_to_load)} 'hoa' records...")
            hoa_sql = "INSERT IGNORE INTO hoa (property_id, hoa_fee, hoa_flag) VALUES (%s, %s, %s)"
            cursor.executemany(hoa_sql, hoas_to_load)
            print(f"Loaded/skipped {cursor.rowcount} records into 'hoa' (pending commit).")

        if rehabs_to_load:
            print(f"Loading {len(rehabs_to_load)} 'rehab' records...")
            rehab_sql = """
                INSERT IGNORE INTO rehab 
                (property_id, underwriting_rehab, rehab_calculation, paint, 
                 flooring_flag, foundation_flag, roof_flag, hvac_flag,
                 kitchen_flag, bathroom_flag, appliances_flag, windows_flag,
                 landscaping_flag, trashout_flag)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.executemany(rehab_sql, rehabs_to_load)
            print(f"Loaded/skipped {cursor.rowcount} records into 'rehab' (pending commit).")

        print("Committing all changes to the database...")
        conn.commit()
        print("All data loaded successfully.")

    except Exception as err:
        print(f"--- AN ERROR OCCURRED ---")
        print(f"Error: {err}")
        print("Rolling back changes...")
        conn.rollback()
    finally:
        cursor.close()

def main():
    JSON_FILE_PATH = '/Users/acer/Downloads/animesh-100x-assessment/data/fake_property_data_new.json'

    conn = get_db_connection()
    if not conn:
        print("Exiting: Database connection failed.")
        return

    raw_df = extract_data(JSON_FILE_PATH)
    if raw_df is not None:
        transform_and_load(raw_df, conn)
    else:
        print("Exiting: Failed to extract data from JSON.")

    conn.close()
    print("ETL process finished.")

if __name__ == "__main__":
    main()

