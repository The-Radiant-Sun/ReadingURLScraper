import threading
import subprocess
import pools
import WebsiteList

folder = '/Users/finn/Documents/Books/Temporary'  # Path to folder where scraped books will be downloaded
recordsFileName = 'urlData.txt'  # Name of file for record-keeping to allow checks for if works have updated
bufferFileName = 'urlList.txt'  # Name of a file for record-keeping to show urls to be downloaded from a bulk scrape

websites = WebsiteList.websites

checkUpdate = True  # Checks if works have updated and notes data to focus scrape

pageLimit = 5  # Number of pages deep in each website to pull from
waitPeriod = 60  # Number of seconds to wait after each file pulled


def main():
    """Retrieves the urls from the websites, then formats them"""
    try:
        open(recordsFileName, mode='x').close()  # Creates file to catch works that are not updated if it does not exist
        open(bufferFileName, mode='x').close()  # Creates file to store urls not yet converted to epubs after scrape
    except FileExistsError:
        pass

    with open(bufferFileName, mode="r") as bufferFile:
        bufferData = bufferFile.read().split('\n')

    scrapeURLs(getURLs() if bufferData == [''] else bufferData, folder, waitPeriod)  # Remove duplicates through sets and start scraping

    renameFiles(folder)  # Remove unneeded aspects from files


def getURLs():
    """Create a thread for each website that will scan said website for book urls"""
    threads = []
    urlList = []

    with open(recordsFileName, mode="r+") as recordsFile:
        fileData = recordsFile.read().split('\n')
        urlData = {}
        if len(fileData) > 1:
            urlData = {data[0]: data[1] for data in [item.split(' ') for item in fileData]}

    print("\nBeginning scan")
    for website in websites:
        thread = threading.Thread(target=scanWebsite, args=[website, urlList, urlData])  # Create thread for each website
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    print("Ending scan\n")

    urlList = list(set(unpack(urlList)))  # Flatten list and remove duplicates

    with open(bufferFileName, mode="w") as urlBufferFile:
        try:
            urlBufferFile.write('\n'.join(urlList))
        except Exception as Error:
            print(Error)

    with open(recordsFileName, mode="w") as recordsFile:
        try:  # Update urlData except for in the event of errors which will revert it to previous data
            recordsFile.write('\n'.join(f'{" ".join([urlEntry, str(urlData[urlEntry])])}' for urlEntry in urlData))
        except Exception as Error:
            print(f"{type(Error)}: {Error}")
            print("Reverting Url Data to Recorded Backup")
            recordsFile.write('\n'.join(fileData))

    return urlList


def scanWebsite(website, urlList, urlData):
    """Activate website class functions to retrieve valid urls"""
    website = website(pageLimit, urlData)
    websiteURLs = []
    pools.pPrint(f"\nStarted scan of {website.name}")
    getWebsiteURLs(website, websiteURLs)  # Retrieve URLs and update stored URL data if checking for updates
    urlList.append(websiteURLs)
    pools.pPrint(f"\nEnded scan of {website.name}")

    if checkUpdate:
        pools.pToggle(True)
        for key in website.urlData:
            urlData[key] = website.urlData[key]
        pools.pToggle(False)

        pools.pPrint(f"\nUpdated saved data from {website.name}")


def scrapeURLs(urls, path, pause):
    """Use the shell to run fanficfare and retrieve the provided urls in ebook form"""
    print(f"Targeting folder at {path}")
    print(f"Beginning scraping of {len(urls)} urls\n")
    for url in urls:
        percentage = (urls.index(url) * 100) // len(urls)
        print(f"{percentage}% - {urls.index(url) + 1} of {len(urls)}: Started scrape of {url}")
        subprocess.run(["fanficfare", f"{url}"], cwd=path)  # Scrape url
        subprocess.run(["sleep", f"{pause}"])  # Pause to avoid mass requesting
        print(f"{len(str(percentage)) * ' '} - Ended scrape of {url}\n")

        with open(bufferFileName, mode="r+") as urlBufferFile:
            urlBufferData = urlBufferFile.read().split('\n')
            urlBufferFile.seek(0)
            if len(urlBufferData) > 1:
                urlBufferFile.write('\n'.join(urlBufferData[1:]))
            urlBufferFile.truncate()

    print(f"Ended scraping\n")

    open(bufferFileName, mode="w").close()


def getWebsiteURLs(website, websiteURLs):
    """Generate a thread and scan fiction urls for each selected page"""
    threads = []

    for fictionList in website.search:
        thread = threading.Thread(target=website.scanURLs, args=[fictionList])  # Create thread for each page
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    websiteURLs.append([urls for urlSet in website.urlList for urls in urlSet])  # Flatten list

    if checkUpdate:
        website.checkURLs(websiteURLs)


def renameFiles(path):
    """Format files to only include the book name"""
    print("Formatting scraped files")
    files = subprocess.run(["ls"], capture_output=True, text=True, cwd=path).stdout.split('\n')[:-1]  # Find all files in folder
    for book in files:
        subprocess.run(["mv", book, f"{'-'.join(book.split('-')[:-1])}.epub"], cwd=path)  # Remove all bar the book name
        print(f"{'-'.join(book.split('-')[:-1])} formatted")


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
