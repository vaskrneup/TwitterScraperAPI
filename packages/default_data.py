class DefaultData:
    __HEADERS = {}
    __BASE_URL = "https://mobile.twitter.com"
    __DEFAULT_PARSER = "lxml"

    def create_or_update_headers(self, _k, _v):
        self.__HEADERS[_k] = _v
        return self.__HEADERS

    def get_headers(self):
        return self.__HEADERS

    def get_base_url(self):
        return self.__BASE_URL

    def get_default_parser(self):
        return self.__DEFAULT_PARSER

    def get_user_profile_link(self, username):
        return f"{self.__BASE_URL}/{username}"
