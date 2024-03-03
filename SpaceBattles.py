import requests
import pools
from bs4 import BeautifulSoup


class SpaceBattles:
    def __init__(self, pageLimit, urlData):
        """Set up variables, search terms, and print access"""
        search = [
            'https://forums.spacebattles.com/forums/creative-writing.18/?order=view_count&direction=desc&min_word_count=30000',
            'https://forums.spacebattles.com/forums/quests.240/?order=view_count&direction=desc&min_word_count=30000&nodes[0]=-1'
        ]

        self.websiteURL = 'https://forums.spacebattles.com'
        self.page = 'page-'
        self.name = "SpaceBattles"

        self.urlList = []
        self.urlData = urlData

        self.search = [f'{self.page}{i}?'.join(searchItem.split("?")) for searchItem in search for i in range(1, pageLimit + 1)]  # Add page count to search

    def scanURLs(self, webpage):
        """Retrieve valid fiction urls within the provided webpage"""
        pools.pPrint(f"{self.name} - Started scan of {webpage}")

        page = requests.get(webpage)
        soup = BeautifulSoup(page.content, 'html.parser')

        self.urlList.append([self.websiteURL + a['href'] for [a] in [entry.find_all('a', href=True) for entry in soup.find_all('div', class_='structItem-title')]])

        pools.pPrint(f"{self.name} - Ended scan of {webpage}")

    def checkURLs(self, urlList):
        """Uses saved data to check and note the url. Depending on whether url status is different from the last scrape, either remove or continue with the url"""
        for n, urlSet in enumerate(urlList):
            for c, url in enumerate(urlSet):
                ratio = f"{self.name} at {(n * 100) // len(urlList) + (c * 100) // (len(urlSet) * len(urlList))}% - {n * len (urlList) + c}/{len(urlList) + len(urlSet)} - "

                urlInfo = f"\n{ratio} Checking {url}"

                loadedURL = BeautifulSoup(requests.get(url).content, 'html.parser')

                try:
                    scrapedChapterCount = int(loadedURL.find('span', class_='collapseTrigger collapseTrigger--block').getText().split('(')[1].split(' thread')[0])

                    try:  # Try to get saved data on the specific url
                        data = self.urlData[url]
                        urlInfo += "\n - Found within saved data"

                        # Check progress by chapter count comparison, remove if no positive progress from last recorded value
                        urlInfo += f"\n - Url is recorded at {data} chapters, compared to {scrapedChapterCount} chapters online"

                        if int(data) < scrapedChapterCount:
                            urlInfo += "\n - Sending new chapter count to be saved"
                            self.urlData[url] = scrapedChapterCount
                        else:
                            urlInfo += f"\n - Removing url from list due to no positive progress"
                            urlList[n].remove(url)

                    except Exception is ValueError or KeyError:  # If there is no saved data, note data to be saved
                        if url not in self.urlData:
                            urlInfo += "\n - Noting url data to be saved"
                            urlInfo += f"\n - Url is noted as {scrapedChapterCount} chapters long"  # Note chapter count
                            self.urlData[url] = scrapedChapterCount
                        else:
                            urlInfo += f"\n - Removing url to be rescanned due to error"

                except AttributeError:
                    urlInfo += "\n - Story does not use threadmarks"

                pools.pPrint(urlInfo)
