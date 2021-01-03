import json
import enum
import datetime
import requests
from bs4 import BeautifulSoup
from pushbullet import Pushbullet


class SiteChecker:
    options = {}
    path = ""
    isVerbose = False
    isQuiet = False
    pb = ""
    maxFailCount = 15
    updateCycle = 120

    class Fail(enum.Enum):
        connection = 0
        pattern = 1

    class Message(enum.Enum):
        connectionFailed = "Connection error"
        patternFailed = "Pattern error"

    def __init__(
        self, optionPath, apiKey, isQuiet, isVerbose, maxFailCount, updateCycle
    ):
        self.path = optionPath
        self.options = self.readOption(optionPath)
        self.pb = Pushbullet(apiKey)

        if isQuiet:
            self.isQuiet = True

        if isVerbose:
            self.isVerbose = True

        if maxFailCount != None:
            self.maxFailCount = maxFailCount[0]

        if updateCycle != None:
            self.updateCycle = updateCycle[0]

    def readOption(self, path):
        if self.isVerbose:
            print("Read file: " + path)
        with open(path, "r") as f:
            return json.load(f)

    def writeOption(self, path):
        with open(path, "w") as f:
            json.dump(self.options, f)
        if self.isVerbose:
            print("Save file: " + path)

    def isOutdated(self, lastUpdated):
        lastUpdate = datetime.datetime.strptime(lastUpdated, "%Y-%m-%dT%H:%M:%S%z")
        now = datetime.datetime.now().replace(
            microsecond=0, tzinfo=datetime.timezone(datetime.timedelta(hours=9))
        )

        return (now - lastUpdate).seconds > self.updateCycle

    def updatedList(self, saved, found):
        savedSet = set(saved)
        news = []

        for value in found:
            if not value in savedSet:
                news.append(value)

        return news

    def fetchSite(self, url, pattern):
        request = requests.get(url)

        if request.status_code == 200:
            request.encoding = "utf-8"
            soup = BeautifulSoup(request.text, "html.parser")
            result = []
            parsedList = soup.select(pattern)

            for key, value in enumerate(parsedList):
                result.append(next(value.stripped_strings))

            if len(result) > 0:
                return (True, result)
            else:
                return (False, self.Fail.pattern)

        else:
            return (False, self.Fail.connection)

    def check(self):
        for key, value in enumerate(self.options["Sites"]):
            if self.isVerbose:
                print(value["name"], end=" ")

            if value["enabled"] > 0 and self.isOutdated(value["lastUpdate"]):
                result, data = self.fetchSite(value["url"], value["pattern"])

                if result:
                    news = self.updatedList(value["lastData"], data)

                    if len(news) == 0:
                        if self.isVerbose:
                            print("--- Not chainged")
                    else:
                        if self.isVerbose:
                            print("--- Updated")

                    for title in news:
                        if self.isQuiet:
                            print(title, value["url"])
                        else:
                            self.pb.push_link(title, value["url"])

                    value["failCount"] = 0
                    value["lastData"] = data
                else:
                    if self.isVerbose:
                        print("--- Error")

                    value["failCount"] += 1

                    if value["failCount"] > self.maxFailCount:
                        value["failCount"] = 0
                        value["enabled"] = 0
                        if data == Fail.connection:
                            if self.isQuiet:
                                print(value["name"])
                            else:
                                self.pb.push_note(
                                    value["name"], Message.connectionFailed
                                )
                        elif data == Fail.pattern:
                            if self.isQuiet:
                                print(value["name"])
                            else:
                                self.pb.push_note(value["name"], Message.patternFailed)

                value["lastUpdate"] = (
                    datetime.datetime.now()
                    .replace(
                        microsecond=0,
                        tzinfo=datetime.timezone(datetime.timedelta(hours=9)),
                    )
                    .strftime("%Y-%m-%dT%H:%M:%S%z")
                )

        self.writeOption(self.path)
