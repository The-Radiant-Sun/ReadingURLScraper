from bs4 import BeautifulSoup
import requests
import pools


class Website:
    def __init__(self, name: str, url: str, urlData, search: [str], searchTerms, bookCompletion: bool, bookChapters: bool, completionSearch, chapterSearch):
        """Set up variables and url information"""
        self.name = name  # Name of website
        self.websiteURL = url  # Url of website

        self.urlList = []  # List of book urls pulled from webpages
        self.urlData = urlData  # Pre-saved information on book urls

        self.search = search  # Webpages to be scanned and searched for book urls
        self.searchTerms = searchTerms  # What to find for a webpage url to be valid to downloaded as a book

        self.bookCompletion = bookCompletion  # Whether a book can be known as complete or not
        self.bookChapters = bookChapters  # Whether a book's chapter count can be known

        self.completionSearch = completionSearch  # A function that when given a Beautiful Soup page returns if the book is 'completed'
        self.chapterSearch = chapterSearch  # A function that when given a Beautiful Soup page returns the chapter count

    def scanURLs(self, webpage: str):
        """Retrieve valid fiction urls within the provided webpage"""
        pools.pPrint(f"{self.name} - Started scan of {webpage}")

        page = requests.get(webpage)
        soup = BeautifulSoup(page.content, 'html.parser')

        self.urlList.append([self.websiteURL + a['href'] for [a] in [entry.find_all('a', href=True) for entry in soup.find_all(*self.searchTerms[0], **self.searchTerms[1])]])

        pools.pPrint(f"{self.name} - Ended scan of {webpage}")

    def checkURLs(self, urlList: [[str]]):
        """Uses saved data to check and note the url. Depending on whether url status is different from the last scrape, either remove or continue with the url"""
        for n, urlSet in enumerate(urlList):
            for c, url in enumerate(urlSet):
                content = "/".join(url.split("/")[:-1])  # Remove unnecessary url components
                ratio = f"{self.name} at {(n * 100) // len(urlList) + (c * 100) // (len(urlSet) * len(urlList))}% - {n * len (urlList) + c}/{len(urlList) + len(urlSet)} - "

                urlInfo = f"\n{ratio} Checking {url}"  # Text to print at end of section

                loadedURL = BeautifulSoup(requests.get(url).content, 'html.parser')

                try:
                    scrapedCompletionStatus = self.completionSearch(loadedURL) if self.bookCompletion else None
                    scrapedChapterCount = self.chapterSearch(loadedURL) if self.bookChapters else None

                    try:  # Try to get saved data on the specific url
                        data = self.urlData[content]
                        urlInfo += "\n - Found within saved data"

                        if data == "Completed":  # Remove if already completed
                            urlInfo += "\n - Url is recorded as completed\n - Removing url from list due to being already completed"
                            urlList[n].remove(url)

                        elif self.bookCompletion and scrapedCompletionStatus:
                            urlInfo += "\n - Changing url status to completed"
                            self.urlData[content] = "Completed"

                        elif self.bookChapters:  # Check progress by chapter count comparison, remove if no positive progress from last recorded value
                            urlInfo += f" - Url is recorded at {data} chapters, compared to {scrapedChapterCount} chapters online"

                            if int(data) < scrapedChapterCount:
                                urlInfo += "\n - Sending new chapter count to be saved"
                                self.urlData[content] = scrapedChapterCount
                            else:
                                urlInfo += f"\n - Removing url from list due to no positive progress"
                                urlList[n].remove(url)

                    except Exception is ValueError or KeyError:  # If there is no saved data, note data to be saved
                        if content not in self.urlData:
                            urlInfo += "\n - Noting url data to be saved"
                            if self.bookCompletion and scrapedCompletionStatus:
                                urlInfo += f"\n - Url is noted as completed"  # Note if completed
                                self.urlData[content] = "Completed"
                            elif self.bookChapters:
                                urlInfo += f"\n - Url is noted as {scrapedChapterCount} chapters long"  # Note chapter count
                                self.urlData[content] = scrapedChapterCount
                        else:
                            urlInfo += f"\n - Removing url to be rescanned due to error"

                except AttributeError:
                    urlInfo += "\n - Url does not have expected information"

                pools.pPrint(urlInfo)
