import requests
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

        self.search = [f'{searchItem}{self.page}{i}' for searchItem in search for i in range(1, pageLimit + 1)]  # Add page count to search

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
                ratio = f"{self.name} at {(n * 100) // len(urlList) + (c * 100) // (len(urlSet) * len(urlList))}% - {n * len (urlList) + c}/{len(urlList) + len(urlSet)} - "

                urlInfo = f"\n{ratio} Checking {url}"

                loadedURL = BeautifulSoup(requests.get(url).content, 'html.parser')

                scrapedCompletionStatus = loadedURL.find('span', class_='label label-default label-sm bg-blue-hoki', string=re.compile("COMPLETED")) is not None
                scrapedChapterCount = int(loadedURL.find('span', class_='label label-default pull-right').getText().split(" ")[0])

                try:  # Try to get saved data on the specific url
                    data = self.urlData[content]
                    urlInfo += "\n - Found within saved data"

                    if data == "Completed":  # Remove if already completed
                        urlInfo += "\n - Url is recorded as completed\n - Removing url from list due to being already completed"
                        urlList[n].remove(url)

                    elif scrapedCompletionStatus:
                        urlInfo += "\n - Changing url status to completed"
                        self.urlData[content] = "Completed"

                    else:  # Check progress by chapter count comparison, remove if no positive progress from last recorded value
                        urlInfo += f"\n - Url is recorded at {data} chapters, compared to {scrapedChapterCount} chapters online"

                        if int(data) < scrapedChapterCount:
                            urlInfo += "\n - Sending new chapter count to be saved"
                            self.urlData[content] = scrapedChapterCount
                        else:
                            urlInfo += f"\n - Removing url from list due to no positive progress"
                            urlList[n].remove(url)

                except Exception is ValueError or KeyError:  # If there is no saved data, note data to be saved
                    if content not in self.urlData:
                        urlInfo += "\n - Noting url data to be saved"
                        if scrapedCompletionStatus:
                            urlInfo += f"\n - Url is noted as completed"  # Note if completed
                            self.urlData[content] = "Completed"
                        else:
                            urlInfo += f"\n - Url is noted as {scrapedChapterCount} chapters long"  # Note chapter count
                            self.urlData[content] = scrapedChapterCount
                    else:
                        urlInfo += f"\n - Removing url to be rescanned due to error"

                pools.pPrint(urlInfo)
