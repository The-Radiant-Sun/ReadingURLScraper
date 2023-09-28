import threading
from RoyalRoad import RoyalRoad

file = 'urls.txt'  # Name of storage file
websites = [RoyalRoad]
pageLimit = 5  # Number of pages deep in each website to pull from

printPool = threading.Semaphore()


def cprint(sema, text):
    sema.acquire()
    print(text)
    sema.release()


def main():
    storage = open(file, mode='w', errors='replace')  # Open or create storage file
    storage.write('\n'.join(list(set(getURLs()))))  # Remove duplicates through sets and write to storage


def getURLs():
    threads = []
    urlList = []

    for website in websites:
        thread = threading.Thread(target=scanWebsite, args=[website, urlList, printPool])  # Create thread for each website
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    return [urls for urlSet in urlList for urls in urlSet]  # Flatten list


def scanWebsite(website, urlList, sema):
    website = website(pageLimit, sema)
    cprint(sema, f"Started scan of {website.name}")
    website.getURLs(urlList)  # Retrieve URLs
    cprint(sema, f"Ended scan of {website.name}")


if __name__ == '__main__':
    main()
