# --- Basic Identity ---
BOT_NAME = "indiamart_scraper"
SPIDER_MODULES = ["indiamart_scraper.spiders"]
NEWSPIDER_MODULE = "indiamart_scraper.spiders"

# --- Crawl Politeness & Anti-Ban ---
ROBOTSTXT_OBEY = True

# Set a realistic browser User-Agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# Configure a delay for requests for the same website (seconds)
DOWNLOAD_DELAY = 2

# Enable the AutoThrottle extension to automatically adjust crawl speed
AUTOTHROTTLE_ENABLED = True
AUTOTHROTTLE_START_DELAY = 5
AUTOTHROTTLE_MAX_DELAY = 60
AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0 

# --- Data Export Configuration ---
FEEDS = {
    'data/raw/%(name)s_%(time)s.json': {
        'format': 'json',
        'encoding': 'utf8',
        'store_empty': False,
        'fields': None,
        'indent': 4,  
    }
}