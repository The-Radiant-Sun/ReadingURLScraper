from RoyalRoad import RoyalRoad

file = 'urls.txt'
websites = [RoyalRoad]
pageLimit = 5


def main():
    storage = open(file, mode='w', errors='replace')
    storage.write('\n'.join(getURLs()))


def getURLs():
    urlList = []
    for website in websites:
        urlList.append(website(pageLimit).getURLs())
    return [urls for urlSet in urlList for urls in urlSet]


if __name__ == '__main__':
    main()
