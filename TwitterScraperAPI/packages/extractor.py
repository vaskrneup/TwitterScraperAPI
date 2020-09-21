from bs4 import BeautifulSoup
import datetime


class ProfileExtractors:
    BASE_URL = "https://mobile.twitter.com"
    MAIN_TWITTER_BASE_URL = "https://twitter.com"

    DATE_FORMATS = [
        "%b %d %Y"
    ]

    def __init__(self, soup: BeautifulSoup, default_return="", post_process_func=None, use_post_process=True,
                 use_filter=True):
        self.soup = soup
        self.default_return = default_return

        self.post_process_func = post_process_func or [lambda obj: obj.strip() if hasattr(obj, "strip") else obj]
        self.use_post_process = use_post_process

        self.use_filter = use_filter

    def return_default(self, func, *args):
        try:
            return self.postprocessor(func()) if self.use_post_process else func()
        except args:
            return self.default_return

    def set_post_process_func(self, func):
        self.post_process_func.append(func)

    def postprocessor(self, data):
        list_out = []

        for func in self.post_process_func:
            if type(data) is list and data:
                for d in data:
                    list_out.append(func(d))
            else:
                data = func(data)

        return list_out.copy() if type(data) is list else data

    def get_profile_url(self, username: str):
        return f"{self.MAIN_TWITTER_BASE_URL}{'' if username.startswith('/') else '/'}{username}"

    def get_post_url(self, post_fix: str):
        return f"{self.MAIN_TWITTER_BASE_URL}{'' if post_fix.startswith('/') else ''}{post_fix}"

    def filter(self, data, functions):
        if self.use_filter:
            for func in functions:
                data = filter(func, data)

        return data

    def date_formatter(self, date):
        date = date.strip()
        _temp = date

        if len(date) < 4:
            return datetime.datetime.now()

        if len(date) < 8:
            date = f"{date} 2020"

        for date_format in self.DATE_FORMATS:
            try:
                return datetime.datetime.strptime(
                    date, date_format
                )
            except ValueError:
                pass

        return _temp

    # Extractor From Here !!
    def get_tweet_following_followers(self, remove_comma=False):
        data = [data.text.replace(",", "") if remove_comma else data.text for data in self.soup.select("div.statnum")]
        return data if len(data) == 3 else [0, 0, 0]

    def get_profile_picture(self):
        return self.return_default(
            lambda: self.soup.select("td.avatar img")[0].attrs.get('src'),
            IndexError
        )

    def get_full_name(self):
        return self.return_default(
            lambda: self.soup.select("div.fullname")[0].text,
            IndexError
        )

    def get_location(self):
        return self.return_default(
            lambda: self.soup.select("div.location")[0].text,
            IndexError
        )

    def get_website(self):
        return self.return_default(
            lambda: self.soup.select("a.twitter-timeline-link")[0].attrs["data-url"],
            IndexError, AttributeError, KeyError
        )

    def get_timestamp(self, soup, raw=False):
        date = self.return_default(
            lambda: soup.select("td.timestamp a")[0].text,
            AttributeError, IndexError
        )
        return date if raw else self.date_formatter(date)

    def get_tweets(self, filters=None, include=None):
        if include and type(include) != list:
            raise ValueError("include must be of type list")

        tweets = self.soup.select("table.tweet")
        _tweets = []

        if tweets:
            c = 0
            for tweet in tweets:
                try:
                    raw_timestamp = self.soup.select("tr.tweet-header")[c]
                except IndexError:
                    print("ERROR !!")
                c += 1

                container = {
                    "is_retweeted": False,
                    "username": self.default_return,
                    "profile_picture": self.default_return,
                    "full_name": self.default_return,
                    "profile_url": self.default_return,
                    "post_url": self.default_return,
                    "body": self.default_return,
                    "body_mentions": [],
                    "body_urls": [],
                    "time_stamp": self.get_timestamp(raw_timestamp) if raw_timestamp else "",
                    "raw_time_stamp": self.get_timestamp(raw_timestamp, raw=True) if raw_timestamp else "",
                }

                try:
                    is_retweeted = tweet.select("span.context")
                    container["is_retweeted"] = bool(is_retweeted)

                    post_user_profile_pic = tweet.select("td.avatar a img")[0]
                    container["full_name"] = post_user_profile_pic.attrs.get("alt")
                    container["profile_picture"] = post_user_profile_pic.attrs.get("src")

                    post_user_user_profile_url = tweet.select("td.user-info a")[0]
                    container["profile_url"] = self.get_profile_url(
                        post_user_user_profile_url.attrs.get("href")
                    )

                    post_user_username = tweet.select("div.username")[0]
                    container["username"] = post_user_username.text.replace("@", "")

                    post_body = tweet.select("div.dir-ltr")[0]
                    container["body"] = post_body.text

                    post_url = tweet.select("span.metadata a")
                    if post_url:
                        container["post_url"] = self.get_post_url(post_url[0].attrs.get("href").replace("?p=v", ""))

                    mentions = post_body.select("a.twitter-atreply")
                    if mentions:
                        container["body_mentions"] = [mention.attrs.get("data-screenname") for mention in mentions]

                    body_urls = post_body.select("a.twitter_external_link")
                    if body_urls:
                        container["body_urls"] = [
                            url.attrs.get("data-url") for url in body_urls if url.attrs.get("data-url")
                        ]
                except AttributeError:
                    pass

                for key in container:
                    container[key] = self.postprocessor(container[key])

                _tweets.append(
                    {k: container[k] for k in include} if include else container.copy()
                )
        else:
            return []

        return list(self.filter(_tweets, filters)) if filters else _tweets

    # All in one !!
    def get_user_profile_details(self, remove_comma=False, include=None):
        if include and type(include) != list:
            raise ValueError("include must be of type list.")

        tweets, following, followers = self.get_tweet_following_followers(remove_comma=remove_comma)

        temp = {
            "tweets": tweets,
            "following": following,
            "followers": followers,
            "profile_picture": self.get_profile_picture(),
            "full_name": self.get_full_name(),
            "location": self.get_location(),
            "website": self.get_website(),
        }

        return {key: temp[key] for key in include} if include else temp

    def get_all_data(self, filters=None, remove_comma=False, include_profile=None, include_tweets=None):
        return {
            "profile": self.get_user_profile_details(remove_comma=remove_comma, include=include_profile),
            "tweets": self.get_tweets(filters=filters, include=include_tweets)
        }

    def __call__(self, *args, **kwargs):
        return self.get_all_data(*args, **kwargs)
