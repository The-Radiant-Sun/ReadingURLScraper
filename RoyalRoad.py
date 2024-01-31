import requests
import threading
import re
import pools
from bs4 import BeautifulSoup


class RoyalRoad:
    def __init__(self, pageLimit, urlData):
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
        self.urlData = urlData
        self.urlDataDifferenceActions = []

        self.search = [f'{searchItem}{self.page}{i}' for searchItem in search for i in range(1, pageLimit + 1)]  # Add page count to search

    def getURLs(self, websiteURLs, checkUpdate):
        """Generate a thread and scan fiction urls for each selected page"""
        threads = []

        for fictionList in self.search:
            thread = threading.Thread(target=self.scanURLs, args=[fictionList])  # Create thread for each page
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        websiteURLs.append([urls for urlSet in self.urlList for urls in urlSet])  # Flatten list

        if checkUpdate:
            self.checkURLs(websiteURLs)

    def scanURLs(self, webpage):
        """Retrieve valid fiction urls within the provided webpage"""
        pools.pPrint(f"{self.name} - Started scan of {webpage}")

        page = requests.get(webpage)
        soup = BeautifulSoup(page.content, 'html.parser')

        self.urlList.append([self.websiteURL + a['href'] for [a] in [entry.find_all('a', href=True) for entry in soup.find_all('h2', class_='fiction-title')]])

        pools.pPrint(f"{self.name} - Ended scan of {webpage}")

    def checkURLs(self, urlList):
        """Uses saved data to check and note the url. Depending on whether url status is different from the last scrape, either remove or continue with the url"""
        for n, urlSet in enumerate(urlList):
            for c, url in enumerate(urlSet):
                content = "/".join(url.split("/")[:-1])  # Remove unnecessary url components
                percentage = f"{(n * 100) // len(urlList) + (c * 100) // (len(urlSet) * len(urlList))}%"

                scrapedCompletionStatus = BeautifulSoup(requests.get(url).content, 'html.parser').find('span', class_='label label-default label-sm bg-blue-hoki', string=re.compile("COMPLETED")) is not None
                scrapedChapterCount = int(BeautifulSoup(requests.get(url).content, 'html.parser').find('span', class_='label label-default pull-right').getText().split(" ")[0])

                pools.pPrint(f"{percentage} Checking {url}")

                try:  # Try to get saved data on the specific url
                    pools.pPrint(" - Found within saved data")

                    if self.urlData[content] == "Completed":  # Remove if already completed
                        pools.pPrint(" - Url is recorded as completed\n - Removing url from list due to being already completed")
                        urlList[n].remove(url)

                    elif scrapedCompletionStatus:
                        pools.pPrint(" - Changing url status to completed")
                        self.urlData[content] = "Completed"

                    else:  # Check progress by chapter count comparison, remove if no positive progress from last recorded value
                        pools.pPrint(f" - Url is recorded at {self.urlData[content]} chapters, compared to {scrapedChapterCount} chapters online")

                        if int(self.urlData[content]) < scrapedChapterCount:
                            pools.pPrint(" - Sending new chapter count to be saved")
                            self.urlData[content] = scrapedChapterCount
                        else:
                            pools.pPrint(f" - Removing url from list due to no positive progress")
                            urlList[n].remove(url)

                except Exception is ValueError or KeyError:  # If there is no saved data, note data to be saved
                    if content not in self.urlData:
                        pools.pPrint(" - Noting url data to be saved")
                        if scrapedCompletionStatus:
                            pools.pPrint(f" - Url is noted as completed")  # Note if completed
                            self.urlData[content] = "Completed"
                        else:
                            scrapedChapterCount = int(BeautifulSoup(requests.get(url).content, 'html.parser').find('span', class_='label label-default pull-right').getText().split(" ")[0])
                            pools.pPrint(f" - Url is noted as {scrapedChapterCount} chapters long")  # Note chapter count
                            self.urlData[content] = scrapedChapterCount
                    else:
                        pools.pPrint(f" - Removing url to be rescanned due to error")
