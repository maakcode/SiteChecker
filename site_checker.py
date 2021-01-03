import json
import enum
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
from pushbullet import Pushbullet


class SiteChecker:
    options = {}
    path = ""
    is_verbose = False
    is_quiet = False
    pb_object = ""
    max_fail_count = 15
    update_cycle = 120

    class Fail(enum.Enum):
        """ 에러 종류 """

        connection = 0
        pattern = 1

    class Message(enum.Enum):
        """ 에러 메세지 """

        connectionFailed = "Connection error"
        patternFailed = "Pattern error"

    def __init__(
        self, option_path, api_key, is_quiet, is_verbose, max_fail_count, update_cycle
    ):
        self.path = option_path
        self.options = self._read_option(option_path)
        self.pb_object = Pushbullet(api_key)

        if is_quiet:
            self.is_quiet = True

        if is_verbose:
            self.is_verbose = True

        if max_fail_count is not None:
            self.max_fail_count = max_fail_count[0]

        if update_cycle is not None:
            self.update_cycle = update_cycle[0]

    def _read_option(self, path):
        if self.is_verbose:
            print("Read file: " + path)

        with open(path, "r") as file:
            return json.load(file)

    def _write_option(self, path):
        with open(path, "w") as file:
            json.dump(self.options, file)

        if self.is_verbose:
            print("Save file: " + path)

    def _is_outdated(self, last_updated):
        """ 업데이트할 시간이 지났는지 체크 """
        last_update = datetime.strptime(last_updated, "%Y-%m-%dT%H:%M:%S%z")
        now = datetime.now().replace(microsecond=0, tzinfo=timezone(timedelta(hours=9)))
        return (now - last_update).seconds > self.update_cycle

    def _updated_list(self, saved, found):
        """ 새로 바뀐 내용만 필터해서 반환 """
        saved_set = set(saved)
        new_set = {x for x in found if not x in saved_set}

        return list(new_set)

    def _fetch_site(self, url, pattern):
        request = requests.get(url)

        if request.status_code != 200:
            return (False, self.Fail.connection)

        request.encoding = "utf-8"
        soup = BeautifulSoup(request.text, "html.parser")
        result = []
        parsed_list = soup.select(pattern)

        for key, value in enumerate(parsed_list):
            result.append(next(value.stripped_strings))

        if len(result) > 0:
            return (True, result)

        return (False, self.Fail.pattern)

    def check(self):
        for key, value in enumerate(self.options["Sites"]):
            if self.is_verbose:
                print(value["name"], end=" ")

            if value["enabled"] > 0 and self._is_outdated(value["lastUpdate"]):
                result, data = self._fetch_site(value["url"], value["pattern"])

                if result:
                    news = self._updated_list(value["lastData"], data)

                    if self.is_verbose:
                        if len(news) == 0:
                            print("--- Not chainged")
                        else:
                            print("--- Updated")

                    for title in news:
                        if self.is_quiet:
                            print(title, value["url"])
                        else:
                            self.pb_object.push_link(title, value["url"])

                    value["failCount"] = 0
                    value["lastData"] = data

                else:
                    if self.is_verbose:
                        print("--- Error")

                    value["failCount"] += 1
                    if value["failCount"] <= self.max_fail_count:
                        continue

                    value["failCount"] = 0
                    value["enabled"] = 0
                    if data == self.Fail.connection:
                        if self.is_quiet:
                            print(value["name"])
                        else:
                            self.pb_object.push_note(
                                value["name"], self.Message.connectionFailed
                            )
                    elif data == self.Fail.pattern:
                        if self.is_quiet:
                            print(value["name"])
                        else:
                            self.pb_object.push_note(
                                value["name"], self.Message.patternFailed
                            )

                value["lastUpdate"] = (
                    datetime.datetime.now()
                    .replace(microsecond=0, tzinfo=timezone(timedelta(hours=9)))
                    .strftime("%Y-%m-%dT%H:%M:%S%z")
                )

        self._write_option(self.path)
