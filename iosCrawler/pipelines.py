# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import sqlite3
from scrapy.exceptions import DropItem
import datetime


class iOScrawlerPipeline(object):

    root_path = '/Users/romangol/Desktop/whh/iosCrawler/iosCrawler/spiders/'
    db_path = 'ios_25pp.db'
    log_path = 'spider_log.txt'
    file = None
    conn = None

    def open_spider(self, spider):
        try:
            self.conn = sqlite3.connect(self.db_path)
            if self.conn is None:
                self.write_log("Fail to find database in path " + self.db_path + ". Exiting...")
                raise Exception
            self.file = open(self.log_path, 'w')
        except Exception:
            self.write_log("Fail to find database in path " + self.db_path + ". Exiting...")
            raise Exception
        self.conn.execute("CREATE TABLE IF NOT EXISTS app ( "
                          "`title` TEXT NOT NULL, `category` TEXT, "
                          "`update` TEXT, `version` TEXT, "
                          "`source`	TEXT, "
                          "`size` TEXT, `url` TEXT, "
                          "`req` TEXT, `des` TEXT,"
                          "PRIMARY KEY(`title`,`version`))")
        self.conn.commit()

    def process_item(self, item, spider):
        try:
            self.conn.execute("replace into app values ('%s', '%s', '%s', '%s', '%s', "
                              "'%s' ,'%s', '%s', '%s')" % (item['title'], item['category'],
                                                           item['update'], item['version'], item['source'],
                                                           item['size'], item['url'],
                                                           item['req'], item['des']))
            self.conn.commit()
            return item
        except Exception:
            self.write_log('Fail to write item to database. Item: ' + str(item))
            raise DropItem()

    def close_spider(self, spider):
        self.write_log('Closing database...')
        self.conn.close()
        self.file.close()

    def write_log(self, string):
        print >> self.file, "[*]Debug " + self.get_time() + " :" + string + '\n'

    @staticmethod
    def get_time():
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

