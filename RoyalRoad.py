from Websites import Website
import re


class RoyalRoad(Website):
    def __init__(self, pageLimit, urlData):
        """Set up variables, search terms, and print access"""

        websiteURL = 'https://www.royalroad.com'
        name = "Royal Road"

        page = '?page='
        search = [
            'https://www.royalroad.com/fictions/complete',
            'https://www.royalroad.com/fictions/best-rated',
            'https://www.royalroad.com/fictions/trending',
            'https://www.royalroad.com/fictions/rising-stars'
        ]

        search = [f'{searchItem}{page}{i}' for searchItem in search for i in range(1, pageLimit + 1)]  # Add page count to search
        searchTerms = [['h2'], {'class_': 'fiction-title'}]

        bookChapters = True
        bookCompletion = True

        def chapterSearch(url):
            return int(url.find('span', class_='label label-default pull-right').getText().split(" ")[0])

        def completionSearch(url):
            return url.find('span', class_='label label-default label-sm bg-blue-hoki', string=re.compile("COMPLETED")) is not None

        super().__init__(name, websiteURL, urlData, search, searchTerms, bookChapters, bookCompletion, chapterSearch, completionSearch)
