# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class iOSappItem(scrapy.Item):
    # define the fields for your item here like:
    category = scrapy.Field()
    title = scrapy.Field()      # app name
    update = scrapy.Field()     # last update time
    version = scrapy.Field()    # version
    source = scrapy.Field()     # source
    size = scrapy.Field()       # size in MB
    url = scrapy.Field()        # download url
    req = scrapy.Field()        # system requirement (e.g. iOS version >= 9.0)
    des = scrapy.Field()        # description

    def __init__(self):
        scrapy.Item.__init__(self)

    def set_attr(self, attr, value):
        if str(attr) in self.keys():
            print "[*] Debug Log: item has not attribute of " + attr
        else:
            try:
                self[attr] = value.encode('utf-8')
            except Exception:
                self[attr] = " "
                print "[*] Deubg Log: Exception caught when trying to set value of item: " + str(self)
