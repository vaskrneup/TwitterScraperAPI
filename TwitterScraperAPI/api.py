import requests
from bs4 import BeautifulSoup

from TwitterScraperAPI.packages import extractor, default_data


class TwitterAPI(default_data.DefaultData):
    def __init__(self, username=None, use_session=False, display_logs=True, max_retries=5, min_wait_time_per_retry=100,
                 max_wait_per_retry=500):
        self.username = username

        self.use_session = use_session
        self.session = requests.Session() if self.use_session else None

        self.display_logs = display_logs

        self.max_retries = max_retries
        self.min_wait_time_per_retry = min_wait_time_per_retry
        self.max_wait_per_retry = max_wait_per_retry

        self.__extractor = None

    def set_display_log(self, display_logs=True):
        self.display_logs = display_logs

    def display_log(self, *args, **kwargs):
        if self.display_logs:
            print(*args, **kwargs)

    def request_manager(self, method="GET", headers=None, *args, **kwargs) -> requests:
        headers = headers or self.get_headers()

        for _ in range(self.max_retries):
            try:
                if self.session:
                    if method == "GET":
                        return self.session.get(*args, headers=headers, **kwargs)
                    elif method == "POST":
                        return self.session.post(*args, headers=headers, **kwargs)
                else:
                    if method == "GET":
                        return requests.get(*args, headers=headers, **kwargs)
                    elif method == "POST":
                        return requests.post(*args, headers=headers, **kwargs)
            except Exception as e:
                self.display_log(f"[!!] ERROR: {e}")

    def get_soup(self, html):
        return BeautifulSoup(html, self.get_default_parser())

    def get_html(self, *args, **kwargs) -> str:
        res = self.request_manager(*args, **kwargs)
        return res.content.decode("utf-8")

    def get_page_soup(self, url):
        return self.get_soup(self.get_html(url=url))

    def get_or_create_user_extractor(self, soup, override=False) -> extractor.ProfileExtractors:
        return self.__extractor if (self.__extractor and not override) else extractor.ProfileExtractors(soup)

    def get_user_data(self, username) -> extractor.ProfileExtractors:
        user_profile_url = self.get_user_profile_link(username)
        user_profile_soup = self.get_page_soup(url=user_profile_url)

        user_extractor = self.get_or_create_user_extractor(user_profile_soup)
        return user_extractor

    def reset_session(self):
        self.close_session()
        self.session = requests.Session()

    def close_session(self):
        if self.session:
            self.session.close()

    def close(self):
        self.close_session()
