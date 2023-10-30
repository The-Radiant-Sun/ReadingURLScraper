import requests
import threading
import re
import pools
from bs4 import BeautifulSoup


class RoyalRoad:
    def __init__(self, pageLimit):
        """Set up variables, search terms, and print access"""
        search = [
            'https://www.royalroad.com/fictions/complete',
            'https://www.royalroad.com/fictions/best-rated',
            'https://www.royalroad.com/fictions/trending',
            'https://www.royalroad.com/fictions/rising-stars'
        ]

        self.websiteURL = 'https://www.royalroad.com'
        self.page = '?page='
        self.name = "Royal Road"

        self.urlList = []

        self.search = [f'{searchItem}{self.page}{i}' for searchItem in search for i in range(1, pageLimit + 1)]  # Add page count to search

    def getURLs(self, websiteURLs, checkCompleted):
        """Generate a thread and scan fiction urls for each selected page"""
        threads = []

        for fictionList in self.search:
            thread = threading.Thread(target=self.scanURLs, args=[fictionList])  # Create thread for each page
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        websiteURLs.append([urls for urlSet in self.urlList for urls in urlSet])  # Flatten list

        if checkCompleted:
            self.checkURLs(websiteURLs)

    def scanURLs(self, webpage):
        """Retrieve valid fiction urls within the provided webpage"""
        pools.cprint(f"{self.name} - Started scan of {webpage}")

        page = requests.get(webpage)
        soup = BeautifulSoup(page.content, 'html.parser')

        self.urlList.append([self.websiteURL + a['href'] for [a] in [entry.find_all('a', href=True) for entry in soup.find_all('h2', class_='fiction-title')]])

        pools.cprint(f"{self.name} - Ended scan of {webpage}")

    @staticmethod
    def checkURLs(urlList):
        """Checks each url to find completed works and notes them to skip in future scrapes"""
        for n, urlSet in enumerate(urlList):
            for c, url in enumerate(urlSet):
                percentage = f"{(n * 100) // len(urlList) + (c * 100) // (len(urlSet) * len(urlList))}%"
                pools.cprint(f"{percentage} Checking {url}")
                completed = open("completed.txt", mode="r+")
                if "/".join(url.split("/")[:-1]) not in completed.read():
                    if BeautifulSoup(requests.get(url).content, 'html.parser').find('span', class_='label label-default label-sm bg-blue-hoki', string=re.compile("COMPLETED")) is not None:
                        pools.cprint(f"{' ' * len(percentage)}  - Noted {url}")
                        pools.cwrite(completed, "/".join(url.split("/")[:-1]))  # Remove title from url when writing
                else:
                    pools.cprint(f"{' ' * len(percentage)}  - Found {url}")
                    urlList[n].remove(url)
                completed.close()

