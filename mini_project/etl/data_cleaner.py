import pandas as pd
import re
import os
import glob
import logging

# --- Configuration ---
RAW_DATA_PATH = os.path.join('data', 'raw')
PROCESSED_DATA_PATH = os.path.join('data', 'processed')
OUTPUT_FILENAME = 'indiamart_processed_data.csv'

# Setup basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def load_raw_data(raw_path: str) -> pd.DataFrame:
    """
    Loads all .json files from the raw data path into a single DataFrame.
    """
    # Find all JSON files in the directory
    json_files = glob.glob(os.path.join(raw_path, '*.json'))
    
    if not json_files:
        logging.warning(f"No JSON files found in {raw_path}")
        return pd.DataFrame()

    dataframes = []
    for file in json_files:
        try:
            # Scrapy FEEDS setting creates a list of items in one JSON file,
            # so 'read_json' with default 'orient' is correct.
            df = pd.read_json(file, orient='records')
            dataframes.append(df)
            logging.info(f"Successfully loaded {len(df)} records from {file}")
        except Exception as e:
            logging.error(f"Failed to load {file}: {e}")
    
    if not dataframes:
        logging.warning("No data was loaded. Returning empty DataFrame.")
        return pd.DataFrame()
        
    # Combine all individual DataFrames into one
    return pd.concat(dataframes, ignore_index=True)

def process_price(df: pd.DataFrame) -> pd.DataFrame:
    """
    Parses the 'price' string column to extract:
    1. new 'price' (float)
    2. 'unit' (string)
    3. 'currency' (string, default 'INR')
    """
    if 'price' not in df.columns:
        logging.warning("'price' column not found. Skipping price processing.")
        return df

    # Regex to capture:
    # 1. (Optional) Currency Symbol (₹, Rs, $, €)
    # 2. (Required) Price (digits, commas, optional decimal)
    # 3. (Required) Unit (e.g., /Meter, /Piece)
    # Example: "₹ 1,200.50/Meter"
    price_regex = r'(?P<currency_symbol>₹|Rs\.?|\$|€)?\s*(?P<new_price>[\d,]+\.?\d*)(\s*/\s*(?P<unit>[a-zA-Z]+))?'
    
    # Extract data into new columns
    extracted_data = df['price'].str.extract(price_regex)
    
    # --- 1. Create new 'price' (float) ---
    # Replace commas, convert to numeric. Errors='coerce' turns non-matches into NaN
    df['price'] = (
        extracted_data['new_price']
        .str.replace(',', '', regex=False)
        .pipe(pd.to_numeric, errors='coerce')
    )
    
    # --- 2. Create 'unit' ---
    df['unit'] = extracted_data['unit']
    
    # --- 3. Create 'currency' ---
    currency_map = {
        '₹': 'INR',
        'Rs.': 'INR',
        'Rs': 'INR',
        '$': 'USD',
        '€': 'EUR',
    }
    df['currency'] = extracted_data['currency_symbol'].map(currency_map)
    
    # Fill default 'INR' *only* for rows where a price was successfully parsed but no symbol was found
    df.loc[df['price'].notna() & df['currency'].isna(), 'currency'] = 'INR'
    
    return df

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies all cleaning steps: deduplication, creating new ID, 
    price processing, and dropping columns.
    """
    if df.empty:
        logging.info("Input DataFrame is empty. No processing needed.")
        return df

    logging.info(f"Original record count: {len(df)}")
    
    # 1. Drop duplicates based on 'product_url'
    df = df.drop_duplicates(subset=['product_url'], keep='first')
    logging.info(f"After deduplication ('product_url'): {len(df)} records")
    
    # 2. Reset index (crucial step) to ensure it runs sequentially from 0
    df = df.reset_index(drop=True)
    
    # 3. CREATE NEW PRODUCT_ID
    # Overwrite 'product_id' column (if it exists) with the new index, starting from 1
    df['product_id'] = df.index + 1
    logging.info(f"Created new sequential 'product_id' (1 to {len(df)})")

    # 4. Process the price column (creates 'price', 'unit', 'currency')
    df = process_price(df)
    
    # 5. Drop unwanted columns
    columns_to_drop = [
        'product_name', 
        'product_url', 
        'product_description', 
        'images'
    ]
    
    # Check which columns actually exist before trying to drop them
    existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
    df = df.drop(columns=existing_columns_to_drop)
    logging.info(f"Dropped columns: {existing_columns_to_drop}")
    
    # Get all current columns
    all_cols = df.columns.tolist()
    
    # Remove the columns we want to re-order manually
    all_cols.remove('product_id')
    all_cols.remove('price')
    all_cols.remove('unit')
    all_cols.remove('currency')

    # Add them back in the desired order
    final_cols = ['product_id'] + all_cols + ['price', 'unit', 'currency']
    
    # Apply the new column order
    df = df[final_cols]
    
    return df

def save_processed_data(df: pd.DataFrame, path: str, filename: str):
    """
    Saves the processed DataFrame to a CSV file.
    """
    if df.empty:
        logging.warning("Processed DataFrame is empty. No file will be saved.")
        return
        
    # Ensure the output directory exists
    os.makedirs(path, exist_ok=True)
    
    output_filepath = os.path.join(path, filename)
    
    try:
        # 'index=False' avoids saving the pandas index
        # 'encoding='utf-8-sig'' helps Excel read special characters (like ₹) correctly
        df.to_csv(output_filepath, index=False, encoding='utf-8-sig')
        logging.info(f"Successfully saved processed data to {output_filepath} ({len(df)} records)")
    except Exception as e:
        logging.error(f"Failed to save data to {output_filepath}: {e}")

def main():
    """
    Main function to orchestrate the loading, processing, and saving of data.
    """
    logging.info("--- Starting Data Processing Pipeline ---")
    
    # 1. Load data
    raw_df = load_raw_data(RAW_DATA_PATH)
    
    # 2. Process data
    processed_df = clean_data(raw_df)
    
    # 3. Save data
    save_processed_data(processed_df, PROCESSED_DATA_PATH, OUTPUT_FILENAME)
    
    logging.info("--- Data Processing Pipeline Finished ---")

if __name__ == "__main__":
    main()