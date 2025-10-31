import json
import re
import scrapy
import urllib.parse
from indiamart_scraper.items import IndiamartProductItem


class TextileSpider(scrapy.Spider):
    name = "textiles_spider"

    start_urls = [
        "https://dir.indiamart.com/impcat/cotton-fabric.html",
        "https://dir.indiamart.com/impcat/polyester-fabric.html",
        "https://dir.indiamart.com/impcat/yarn.html",
        "https://dir.indiamart.com/impcat/mens-t-shirt.html",
        "https://dir.indiamart.com/impcat/sarees.html",
        "https://dir.indiamart.com/impcat/denim-jeans.html",
        "https://dir.indiamart.com/impcat/leather-fabric.html",
        "https://dir.indiamart.com/impcat/woolen-shawls.html",
    ]

    def parse(self, response):
        """
        Parses the product listing pages (e.g., "cotton-fabric.html").
        
        This method iterates over each product "card" on the listing page,
        extracts the link to its dedicated detail page, and yields a new
        scrapy.Request to follow that link. The 'parse_product_detail'
        method is set as the callback to handle the response from the
        detail page.
        
        It also includes logic for pagination to move to the next page
        of listings.
        """
        self.logger.info(f'Parsing listing page: {response.url}')
        
        # 1. Iterate over each product item on the listing page
        # The selector 'li.mList.tc.bgw' targets each product container
        for product_card in response.css('li.mList.tc.bgw'):
            
            # 2. Extract the URL for the product detail page
            # The URL is in the 'href' attribute of the 'a' tag with class 'prodNameClamp'
            product_url = product_card.css('a.prodNameClamp::attr(href)').get()
            
            if product_url:
                # 3. Yield a new Request to follow the product URL.
                # 'response.follow' automatically handles relative URLs.
                # The 'callback' parameter specifies which method will
                # process the response from this new URL.
                yield response.follow(
                    product_url,
                    callback=self.parse_product_detail
                )

        # 4. Handle Pagination
        # Find the "Next" button's URL. We use a selector for an 'a' tag
        # with title="Next", which is a common pattern for pagination.
        next_page_url = response.css('a[title="Next"]::attr(href)').get()
        
        if next_page_url:
            # If a "Next" page URL is found, yield a new request to follow it.
            # The callback is 'self.parse' because we want to repeat
            # the same listing page logic on the next page.
            yield response.follow(next_page_url, callback=self.parse)

    def parse_product_detail(self, response):
        """
        Parses the product detail page.
        
        This method is called for each product URL followed from the 'parse'
        method. It extracts all the detailed information (like name, price,
        specifications, etc.) from the product's dedicated page and
        populates the IndiamartProductItem.
        """
        self.logger.info(f'Parsing product detail: {response.url}')
        
        # Initialize the item loader or item object
        item = IndiamartProductItem()

        # --- Basic Information Extraction ---
        
        # 'product_url': Get the URL from the response object itself
        item['product_url'] = response.url
        
        # 'product_name': From the main H1 tag
        item['product_name'] = response.css('h1.bo.center-heading::text').get()
        
        # 'product_id': From the 'data-dispid' attribute in a div
        item['product_id'] = response.css('div.pdp_enq::attr(data-dispid)').get()

        # 'price': Price and unit (e.g., "/Meter") are separate text nodes.
        # We use ::text to get all text nodes, then .getall() to list them,
        # and finally .join() to merge them into a single string.
        price_texts = response.css('span#askprice_pg-1 ::text').getall()
        item['price'] = "".join(price_texts).strip() if price_texts else None

        # 'location': From the specific span with class 'city-highlight'
        item['location'] = response.css('span.city-highlight::text').get()
        
        # 'images': Get the high-resolution image link from 'data-zoom' attribute.
        # Use .getall() in case there are multiple main images.
        item['images'] = response.css('img#img_id::attr(data-zoom)').getall()

        # 'brand': This is the supplier/company name
        item['brand'] = response.css('h2.fs15::text').get()

        # 'product_description': Join all text from the description div
        desc_texts = response.css('div#descp2 div.pro-descN ::text').getall()
        item['product_description'] = "".join(desc_texts).strip() if desc_texts else None

        # --- Specification Table Extraction ---
        # For fields like 'fabric_type', 'pattern', 'gsm', 'usage'.
        # These are in a table, so we loop through rows, build a dictionary,
        # and then map the dictionary values to our item fields.
        # This is robust against missing fields or changing order.
        
        details_dict = {}
        # Iterate over each row (tr) in the specification table
        for row in response.css('div.isq-container table tbody tr'):
            
            # Get the key (column 1, e.g., "Fabric Type")
            key = row.css('td.tdwdt::text').get()
            
            # Get the value (column 2, e.g., "Yarn Dyed Fabrics")
            value = row.css('td.tdwdt1 ::text').get()
            
            if key and value:
                # Clean the key: lowercase, strip whitespace, remove colon
                clean_key = key.strip().lower().replace(':', '')
                # Add to dictionary
                details_dict[clean_key] = value.strip()
        
        # Map the extracted details from the dictionary to the item fields
        # Using .get(key) safely returns None if the key doesn't exist
        # (e.g., if 'gsm' or 'usage' is not listed for this product).
        item['fabric_type'] = None
        item['pattern'] = None
        item['gsm'] = None
        item['usage'] = None
        item['availability'] = None 

        # Loop through the dictionary to find matching keys "fuzzy-ly"
        for key, value in details_dict.items():
            
            # Find 'fabric_type' OR 'material'
            if 'fabric' in key or 'material' in key:
                item['fabric_type'] = value
            
            # Find 'pattern' (e.g., matches 'prints/pattern')
            if 'pattern' in key:
                item['pattern'] = value
            
            # Find 'gsm' (e.g., matches 'gsm' or 'gsm (grams per sq. meter)')
            if 'gsm' in key:
                item['gsm'] = value
            
            # Find 'usage'
            if 'usage' in key:
                item['usage'] = value
            
            # Find 'availability' (and fix typo)
            if 'availability' in key:
                item['availability'] = value 

        # Finally, yield the populated item
        yield item