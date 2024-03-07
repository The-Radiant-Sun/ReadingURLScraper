from Websites import Website


class SpaceBattles(Website):
    def __init__(self, pageLimit, urlData):
        """Set up variables, search terms, and print access"""

        websiteURL = 'https://forums.spacebattles.com'
        name = "SpaceBattles"

        page = 'page-'
        search = [
            'https://forums.spacebattles.com/forums/creative-writing.18/?order=view_count&direction=desc&min_word_count=30000',
            'https://forums.spacebattles.com/forums/quests.240/?order=view_count&direction=desc&min_word_count=30000&nodes[0]=-1'
        ]

        search = [f'{page}{i}?'.join(searchItem.split("?")) for searchItem in search for i in range(1, pageLimit + 1)]  # Add page count to search
        searchTerms = [['div'], {'class_': 'structItem-title'}]

        bookChapters = True
        bookCompletion = False

        def chapterSearch(url):
            return int(url.find('span', class_='collapseTrigger collapseTrigger--block').getText().split('(')[1].split(' thread')[0])

        completionSearch = None

        super().__init__(name, websiteURL, urlData, search, searchTerms, bookChapters, bookCompletion, chapterSearch, completionSearch)
