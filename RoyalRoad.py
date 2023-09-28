import requests
import threading
from bs4 import BeautifulSoup


class RoyalRoad:
    def __init__(self, pageLimit, printPool):
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

        self.printPool = printPool

        self.search = [f'{searchItem}{self.page}{i}' for searchItem in search for i in range(1, pageLimit + 1)]  # Add page count to search

    def getURLs(self, websiteURLs):
        threads = []

        for fictionList in self.search:
            thread = threading.Thread(target=self.scanURLs, args=[fictionList])  # Create thread for each page
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        websiteURLs.append([urls for urlSet in self.urlList for urls in urlSet])  # Flatten list

    def scanURLs(self, webpage):
        self.cprint(f"{self.name} - Started scan of {webpage}")

        page = requests.get(webpage)
        soup = BeautifulSoup(page.content, 'html.parser')
        self.urlList.append([self.websiteURL + a['href'] for [a] in [entry.find_all('a', href=True) for entry in soup.find_all('h2', class_='fiction-title')]])

        self.cprint(f"{self.name} - Ended scan of {webpage}")

    def cprint(self, text):
        self.printPool.acquire()
        print(text)
        self.printPool.release()

