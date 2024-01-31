import threading
import subprocess
import pools
from RoyalRoad import RoyalRoad

folder = '/Users/finn/Documents/Books/Temporary'
file = 'urlData.txt'
websites = [RoyalRoad]

checkUpdate = True  # Checks if works have updated and notes data to focus scrape

pageLimit = 5  # Number of pages deep in each website to pull from
waitPeriod = 60  # Number of seconds to wait after each file pulled


def main():
    """Retrieves the urls from the websites, then formats them"""
    try:
        open(file, mode='x')  # Creates file to catch works that are not updated if it does not exist
    except FileExistsError:
        pass

    scrapeURLs(list(set(getURLs())), folder, waitPeriod)  # Remove duplicates through sets and start scraping
    renameFiles(folder)  # Remove unneeded aspects from files


def getURLs():
    """Create a thread for each website that will scan said website for book urls"""
    threads = []
    urlList = []

    with open("urlData.txt", mode="r+") as urlDataFile:
        urlData = {}
        if len(urlDataFile.readlines()) > 1:
            urlData = {data[0]: data[1] for data in [item.split(' ') for item in urlDataFile.read().split('\n')]}
        urlDataBackup = urlData
        urlDataFile.close()

    print("\nBeginning scan")
    for website in websites:
        thread = threading.Thread(target=scanWebsite, args=[website, urlList, urlData])  # Create thread for each website
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Ending scan\n")

    with open("urlData.txt", mode="w") as urlDataFile:
        try:  # Update urlData except for errors, then revert to previous data
            urlDataFile.write('\n'.join(f'{" ".join([urlEntry, str(urlData[urlEntry])])}' for urlEntry in urlData))
        except Exception as Error:
            print(f"{type(Error)}: {Error}")
            print("Reverting Url Data to Recorded Backup")
            urlDataFile.write('\n'.join(f'{" ".join([urlEntry, urlDataBackup[urlEntry]])}' for urlEntry in urlDataBackup))
        urlDataFile.close()

    return unpack(urlList)  # Flatten list


def scanWebsite(website, urlList, urlData):
    """Activate website class functions to retrieve valid urls"""
    website = website(pageLimit, urlData)
    websiteURLs = []
    pools.pPrint(f"Started scan of {website.name}")
    website.getURLs(websiteURLs, checkUpdate)  # Retrieve URLs and update stored URL data if checking for updates
    urlList.append(websiteURLs)
    pools.pPrint(f"Ended scan of {website.name}")

    if checkUpdate:
        pools.pToggle(True)
        for key in website.urlData:
            urlData[key] = website.urlData[key]
        pools.pToggle(False)

        pools.pPrint(f"Updated saved data from {website.name}")


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
