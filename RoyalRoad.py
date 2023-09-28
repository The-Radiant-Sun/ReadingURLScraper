import requests
from bs4 import BeautifulSoup


class RoyalRoad:
    def __init__(self, pageLimit):
        search = [
            'https://www.royalroad.com/fictions/complete',
            'https://www.royalroad.com/fictions/best-rated',
            'https://www.royalroad.com/fictions/trending',
            'https://www.royalroad.com/fictions/rising-stars'
        ]

        self.website = 'https://www.royalroad.com'

        self.page = '?page='

        self.search = [f'{searchItem}{self.page}{i}' for i in range(1, pageLimit + 1) for searchItem in search]


    def getURLs(self):
        urlList = []

        for fictionList in self.search:
            page = requests.get(fictionList)
            soup = BeautifulSoup(page.content, 'html.parser')

            urlList.append([self.website + a['href'] for [a] in [entry.find_all('a', href=True) for entry in soup.find_all('h2', class_='fiction-title')]])

        return [urls for urlSet in urlList for urls in urlSet]

