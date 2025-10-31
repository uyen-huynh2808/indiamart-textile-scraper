# Mini Project: IndiaMart Textile Scraper & ETL

This project is a complete data pipeline built in Python using the Scrapy framework. It is designed to crawl and extract detailed product information for various textile categories from [IndiaMart](https://dir.indiamart.com/).

After extraction, a separate ETL script processes the raw JSON data, cleans it using Pandas, and saves the final structured dataset as a CSV file ready for analysis.

---

## Technology & Tools Used

This project utilizes the following core technologies:
* **Python 3**: The core programming language.
* **Scrapy**: A powerful, high-level web crawling and scraping framework used for the "Extract" (E) part of the pipeline.
* **Pandas**: A data analysis and manipulation library used for the "Transform" (T) and "Load" (L) parts of the pipeline.

---

## File Structure

The project is organized into three main components: the Scrapy scraper (`indiamart_scraper`), the data storage (`data`), and the ETL script (`etl`).

```text
mini_project/
├── requirements.txt
├── scrapy.cfg
├── indiamart_scraper/
│   ├── items.py
│   ├── settings.py
│   ├── middlewares.py
│   └── spiders/
│       └── textiles_spider.py
├── data/
│   ├── processed/
│   └── raw/
└── etl/
    └── data_cleaner.py
```

### File Functions

* **`requirements.txt`**: Lists all Python dependencies (Scrapy, Pandas).
* **`scrapy.cfg`**: Scrapy project configuration file. It tells Scrapy where to find the project's settings.

#### `indiamart_scraper/`
* **`items.py`**: Defines the `IndiamartProductItem`, which is a Scrapy `Item` class. This acts as a schema or blueprint for the data we want to collect (e.g., `product_name`, `price`, `fabric_type`).
* **`settings.py`**: Configures the Scrapy crawler. This file includes settings for:
    * Bot identity (`BOT_NAME`, `USER_AGENT`).
    * Crawl politeness (`DOWNLOAD_DELAY`, `AUTOTHROTTLE_ENABLED`) to avoid banning.
    * The `FEEDS` setting, which automatically exports the scraped data to a time-stamped JSON file in the `data/raw/` directory.
* **`middlewares.py`**: Contains `UserAgentRotationMiddleware`, a custom middleware that rotates the `User-Agent` header for each request. This makes the scraper appear as different browsers, reducing the risk of being blocked.
* **`spiders/textiles_spider.py`**: The heart of the scraper. This file contains the `TextileSpider` class which:
    * Defines the `start_urls` (the initial category pages).
    * Contains the `parse()` method to find all product links on a listing page and follow the "Next" page link (pagination).
    * Contains the `parse_product_detail()` callback method to extract all data from a single product's page and yield the final `IndiamartProductItem`.

#### `data/`
* **`data/raw/`**: This directory stores the raw, unprocessed output from the Scrapy spider. The `settings.py` file is configured to save data here as `.json` files.
* **`data/processed/`**: This directory stores the final, cleaned output (`indiamart_processed_data.csv`) after the ETL script runs.

#### `etl/`
* **`data_cleaner.py`**: A Pandas script that performs the full ETL process:
    1.  **Extract**: Loads all raw `.json` files from `data/raw/` into a single DataFrame.
    2.  **Transform**:
        * Drops duplicate records based on `product_url`.
        * Creates a new sequential `product_id`.
        * Parses the `price` column using regex to extract numeric `price`, `unit` (e.g., "Meter"), and `currency`.
        * Drops non-essential columns (`product_name`, `product_url`, `description`, `images`) to create a more compact, analytical dataset.
        * Re-orders columns for clarity.
    3.  **Load**: Saves the final, cleaned DataFrame to `data/processed/indiamart_processed_data.csv`.

## How to Run Locally

Follow these steps to set up the environment and run the pipeline.

**1. Create and activate a virtual environment:** (The commands below assume a Linux/macOS environment)

```bash
# Create a virtual environment
python3 -m venv ~/venvs/miniproj-env

# Activate it
source ~/venvs/miniproj-env/bin/activate
```

**2. Install the required dependencies:**

```bash
pip install -r requirements.txt
```

**3. Run the Scrapy spider (Extract):**

This command will start the crawler. The raw data will be saved automatically to the `data/raw/` folder, named something like textiles_spider_2025-10-31T13-30-00.json.

```bash
# Navigate to the project root (e.g., ~/mini_project)
scrapy crawl textiles_spider
```

**4. Run the ETL script (Transform & Load):**

Once the spider is finished, run this script to clean the data.

```bash
# This will read from data/raw/ and save the clean CSV to data/processed/
python etl/data_cleaner.py
```

**5. Find your results:**

The final, clean dataset is now available at: `data/processed/indiamart_processed_data.csv`

