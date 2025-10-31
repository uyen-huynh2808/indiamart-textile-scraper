import scrapy

class IndiamartProductItem(scrapy.Item):
    product_name = scrapy.Field()
    product_id = scrapy.Field()
    product_url = scrapy.Field()
    price = scrapy.Field()
    fabric_type = scrapy.Field()
    gsm = scrapy.Field()
    pattern = scrapy.Field()
    usage = scrapy.Field()
    brand = scrapy.Field()
    product_description = scrapy.Field()
    images = scrapy.Field()
    location = scrapy.Field()
    availability = scrapy.Field()
