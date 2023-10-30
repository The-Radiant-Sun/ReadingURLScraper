import threading
import subprocess
import pools
from RoyalRoad import RoyalRoad

folder = '/Users/finn/Documents/Books/Temporary'
file = 'completed.txt'
websites = [RoyalRoad]

checkCompleted = True  # Checks if works are completed and notes them to not pull in future scrapes

pageLimit = 5  # Number of pages deep in each website to pull from
waitPeriod = 60  # Number of seconds to wait after each file pulled


def main():
    """Retrieves the urls from the websites, then formats them"""

    # Creates file to catch completed works if it does not exist
    try:
        open(file, mode='x')
    except FileExistsError:
        pass

    scrapeURLs(list(set(getURLs())), folder, waitPeriod)  # Remove duplicates through sets and start scraping
    renameFiles(folder)  # Remove unneeded aspects from files


def getURLs():
    """Create a thread for each website that will scan said website for book urls"""
    threads = []
    urlList = []

    print("\nBeginning scan")
    for website in websites:
        thread = threading.Thread(target=scanWebsite, args=[website, urlList])  # Create thread for each website
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    print("Ending scan\n")

    return unpack(urlList)  # Flatten list


def scanWebsite(website, urlList):
    """Activate website class functions to retrieve valid urls"""
    website = website(pageLimit)
    websiteURLs = []
    pools.cprint(f"Started scan of {website.name}")
    website.getURLs(websiteURLs, checkCompleted)  # Retrieve URLs
    urlList.append(websiteURLs)
    pools.cprint(f"Ended scan of {website.name}")


def scrapeURLs(urls, path, pause):
    """Use the shell to run fanficfare and retrieve the provided urls in ebook form"""
    print(f"Targeting folder at {path}")
    print(f"Beginning scraping of {len(urls)} urls\n")
    for url in urls:
        print(f"{(urls.index(url) * 100) // len(urls)}% - {urls.index(url) + 1} of {len(urls)}: Started scrape of {url}")
        subprocess.run(["fanficfare", f"{url}"], cwd=path)  # Scrape url
        subprocess.run(["sleep", f"{pause}"])  # Pause to avoid mass requesting
        print(f"Ended scrape of {url}\n")
    print(f"Ended scraping\n")


def renameFiles(path):
    """Format files to only include the book name"""
    print("Formatting scraped files")
    files = subprocess.run(["ls"], capture_output=True, text=True, cwd=path).stdout.split('\n')[:-1]  # Find all files in folder
    for file in files:
        subprocess.run(["mv", file, f"{'-'.join(file.split('-')[:-1])}.epub"], cwd=path)  # Remove all bar the book name
        print(f"{'-'.join(file.split('-')[:-1])} formatted")


def unpack(array):
    """Flattens inputted list through recursion"""
    repack = []
    for item in array:
        if type(item) == list:
            for subItem in unpack(item):
                repack.append(subItem)
        else:
            repack.append(item)
    return repack


if __name__ == '__main__':
    main()
