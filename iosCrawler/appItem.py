
class iOSappItem():
    # define the fields for your item here like:
    app_dict = {}

    def __init__(self):
        self.app_dict['category'] = ""  # category
        self.app_dict['title'] = ""     # app name
        self.app_dict['update'] = ""    # last update time
        self.app_dict['version'] = ""   # version
        self.app_dict['source'] = ""    # source
        self.app_dict['size'] = ""      # size in MB
        self.app_dict['url'] = ""       # download url
        self.app_dict['bundle'] = ""    # bundle name
        self.app_dict['des'] = ""       # description

    def __str__(self):
        return str(self.app_dict)

    def set_value(self, attr, value):
        try:
            self.app_dict[attr] = value
        except Exception:
            self.app_dict[attr] = ""
            raise Exception

    def get_value(self, attr):
        try:
            value = self.app_dict.get(attr)
            return value
        except Exception:
            raise Exception
