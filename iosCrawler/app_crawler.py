# encoding: utf-8
import requests
import json
import base64
import time
import datetime
import sqlite3
import traceback
from appItem import iOSappItem

# catid constant
CAT_DICT = {88: u'书籍', 89: u'商业', 90: u'教育', 91: u'娱乐', 92: u'财经', 93: u'健康', 94: u'生活', 95: u'医疗', 96: u'音乐',
            97: u'导航', 98: u'新闻', 99: u'摄影', 100: u'效率', 101: u'参考', 102: u'社交', 103: u'体育', 104: u'旅行',
            105: u'工具', 106: u'天气', 167: u'美食',

            72: u'角色扮演', 73: u'休闲娱乐', 74: u'射击游戏', 75: u'益智游戏', 76: u'棋牌天地', 77: u'情景游戏',
            78: u'冒险游戏', 79: u'策略游戏', 80: u'模拟经营', 81: u'动作游戏', 82: u'体育竞技', 83: u'竞速游戏',
            84: u'格斗游戏', 169: u'儿童教育'}

root_path = '/Users/romangol/Desktop/whh/iosCrawler/iosCrawler/'
db_path = root_path + 'ios_25pp.db'
log_path = root_path + 'spider_log.txt'
log = None
conn = None

# restype constant
RES_SOFT = 1
RES_GAME = 2
MAX_PAGE = 200
PER_COUNT = 50


def post_request_for_app(category, page):
    url = "http://jsondata.25pp.com/index.html"

    headers = {
        'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36",
        'Accept': "*/*",
        'Referer': "http://jsondata.25pp.com/index.html?tunnel-command=4261421120",
        'Content-Type': "application/x-www-form-urlencoded",
        'Accept-Language': "zh-cn",
        'Tunnel-Command': "4261421088",
        'Accept-Encoding': "gzip, deflate",
        'Host': "jsondata.25pp.com",
        'Cache-Control': "no-cache",
        'Postman-Token': "7258984e-99b9-4e41-8920-53a5c19d5d19"
    }

    if 88 <= category <= 106 or category == 167:
        res = 1
    else:
        res = 2

    # parameters
    # dcType:   device type.    0.all,      1.iphone,   2.ipad
    # resType:  resource type.  1.software  2.games
    # listType: list type       1.newest    2.hottest   3.week top  4.month top 5.top board
    # catId:    category type   [88, 106]+167 for soft      [72,84]+169 for game    all for jail-broken apps
    # perCount: number of apps in one page
    # page:     page number
    payload = '{"dcType":0,"resType":%d,"listType":5,"catId":%d,"perCount":%d,"page":%d}' % (res, category, PER_COUNT, page)
    response = requests.request("POST", url, data=payload, headers=headers)
    if response.status_code == 200:
        write_log("Request for catid %d of page %d... Return status code = 200" % (category, page))
        return response
    else:
        write_log("Request failed when trying to get apps of category %d and page %d. "
                  "Response code %d, please check your network status." % (category, page, response.status_code))


def parse_response(res, cat):
    result = json.loads(res.content[3:])
    if result['status'] == 0:
        # for each app
        for i in range(result['content'].__len__()):
            item = iOSappItem()
            temp = result['content'][i]
            try:
                item.set_value('category', CAT_DICT.get(cat))
            except Exception:
                write_log("Exception caught when trying to set value %s of attribute: %s" % (CAT_DICT.get(cat), 'category'))

            try:
                item.set_value('title', temp['title'])
            except Exception:
                write_log("Exception caught when trying to set value %s of attribute: %s" % (temp['title'], 'title'))

            try:
                item.set_value('update', time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(temp['updatetime'])))
            except Exception:
                write_log("Exception caught when trying to set value %s of attribute: %s" % (temp['updatetime'], 'update'))

            try:
                item.set_value('version', temp['version'])
            except Exception:
                write_log("Exception caught when trying to set value %s of attribute: %s" % (temp['version'], 'version'))

            try:
                item.set_value('source', 'https://www.25pp.com/ios/detail_%s' % temp['id'])
            except Exception:
                write_log("Exception caught when trying to set value %s of attribute: %s" % (temp['id'], 'source'))

            try:
                item.set_value('size', temp['fsize'])
            except Exception:
                write_log("Exception caught when trying to set value %s of attribute: %s" % (temp['fsize'], 'size'))

            try:
                item.set_value('url', base64.b64decode(temp['downurl']))
            except Exception:
                write_log("Exception caught when trying to set value %s of attribute: %s" % (temp['downurl'], 'url'))

            try:
                item.set_value('bundle', temp['buid'])
            except Exception:
                write_log("Exception caught when trying to set value %s of attribute: %s" % (temp['buid'], 'bundle'))
                write_log(traceback.format_exc())

            try:
                item.set_value('des', temp['remark'])
            except Exception:
                write_log("Exception caught when trying to set value %s of attribute: %s" % (temp['remark'], 'des'))
                write_log(traceback.format_exc())

            write_app_to_db(item)
    else:
        # request fail
        write_log("Request failed when trying to get apps of category %d. "
                  "Fail to request of apps, return status code error: %d " % (cat, result['status']))


def write_app_to_db(item):
    global conn
    try:
        conn.execute('replace into app values ("%s", "%s", "%s", "%s", "%s", '
                     '"%s" ,"%s", "%s", "%s")' % (item.get_value('title'), item.get_value('category'),
                                                  item.get_value('update'), item.get_value('version'),
                                                  item.get_value('source'),
                                                  item.get_value('size'), item.get_value('url'),
                                                  item.get_value('bundle'), item.get_value('des')))
    except Exception:
        try:
            # dealing with "
            if item.get_value('title').__contains__('"'):
                item.set_value('title', item.get_value('title').replace('"', ""))

            if item.get_value('des').__contains__('"'):
                item.set_value('des', item.get_value('des').replace('"', ""))

            conn.execute('replace into app values ("%s", "%s", "%s", "%s", "%s", '
                         '"%s" ,"%s", "%s", "%s")' % (item.get_value('title'), item.get_value('category'),
                                                      item.get_value('update'), item.get_value('version'),
                                                      item.get_value('source'),
                                                      item.get_value('size'), item.get_value('url'),
                                                      item.get_value('bundle'), item.get_value('des')))
        except Exception as e:
            write_log("Error while writing item %s to database" % str(item))
            write_log(traceback.format_exc())

    conn.commit()


def start_request():
    for cat in CAT_DICT.keys():
        for p in range(MAX_PAGE):
            response = post_request_for_app(cat, p)
            time.sleep(0.1)
            parse_response(response, cat)


def write_log(string):
    global log
    print >> log, "[*]Debug " + get_time() + " : " + string + '\n'


def get_time():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def main():
    global conn
    try:
        conn = sqlite3.connect(db_path)
        if conn is None:
            write_log("Fail to find database in path " + db_path + ". Exiting...")
            raise Exception
    except Exception:
        write_log("Fail to find database in path " + db_path + ". Exiting...")
        raise Exception

    conn.execute("CREATE TABLE IF NOT EXISTS app ( "
                 "`title` TEXT NOT NULL, `category` TEXT, "
                 "`update` TEXT, `version` TEXT, "
                 "`source`	TEXT, "
                 "`size` TEXT, `url` TEXT, "
                 "`bundle` TEXT, `des` TEXT,"
                 "PRIMARY KEY(`title`,`version`))")
    conn.commit()

    global log
    log = open(log_path, 'w')
    write_log("Successfully open database from path " + db_path)
    write_log("Log file open from path " + log_path)

    write_log("Crawler starts requesting for apps...")
    start_request()

    write_log("Crawler finished crawling apps, closing database and log...")
    conn.close()
    log.close()


if __name__ == '__main__':
    main()
