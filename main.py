import threading
import subprocess
from RoyalRoad import RoyalRoad

folder = '/Users/finn/Documents/Books/Temporary'
websites = [RoyalRoad]

pageLimit = 5  # Number of pages deep in each website to pull from
waitPeriod = 60  # Number of seconds to wait after each file pulled

printPool = threading.Semaphore()  # Make only one thread able to use the pool at a time


def cprint(sema, text):
    """Ensures there is only one thread printing at a time"""
    sema.acquire()
    print(text)
    sema.release()


def main():
    """Retrieves the urls from the websites, then formats them"""
    scrapeURLs(list(set(getURLs())), folder, waitPeriod)  # Remove duplicates through sets and start scraping
    renameFiles(folder)  # Remove unneeded aspects from files


def getURLs():
    """Create a thread for each website that will scan said website for book urls"""
    threads = []
    urlList = []

    print("\nBeginning scan")
    for website in websites:
        thread = threading.Thread(target=scanWebsite, args=[website, urlList, printPool])  # Create thread for each website
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    print("Ending scan\n")

    return [urls for urlSet in urlList for urls in urlSet]  # Flatten list


def scanWebsite(website, urlList, sema):
    """Activate website class functions to retrieve valid urls"""
    website = website(pageLimit, sema)
    cprint(sema, f"Started scan of {website.name}")
    website.getURLs(urlList)  # Retrieve URLs
    cprint(sema, f"Ended scan of {website.name}")


def scrapeURLs(urls, path, pause):
    """Use the shell to run fanficfare and retrieve the provided urls in ebook form"""
    print(f"Targeting folder at {path}")
    print(f"Beginning scraping of {len(urls)} urls\n")
    for url in urls:
        print(f"{urls.index(url) + 1} of {len(urls)}: Started scrape of {url}")
        subprocess.run(["fanficfare", f"{url}"], cwd=path)  # Scrape url
        subprocess.run(["sleep", f"{pause}"])  # Pause to avoid mass requesting
        print(f"Ended scrape of {url}\n")
    print(f"Ended scraping\n")


def renameFiles(path):
    """Format files to only include the book name"""
    files = subprocess.run(["ls"], capture_output=True, text=True, cwd=path).stdout.split('\n')[:-1]  # Find all files in folder
    for file in files:
        subprocess.run(["mv", file, f"{'-'.join(file.split('-')[:-1])}.epub"], cwd=path)  # Remove all bar the book name


if __name__ == '__main__':
    main()
