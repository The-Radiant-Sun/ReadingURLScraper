from RoyalRoad import RoyalRoad

file = 'urls.txt' #Name of storage file
websites = [RoyalRoad]
pageLimit = 5 #Number of pages deep in each website to pull from


def main():
    storage = open(file, mode='w', errors='replace') #Open or create storage file
    storage.write('\n'.join(list(set(getURLs())))) #Remove duplicates through sets and write to storage


def getURLs():
    urlList = []
    for website in websites:
        urlList.append(website(pageLimit).getURLs()) #Retrieve URLs
    return [urls for urlSet in urlList for urls in urlSet] #Flatten list


if __name__ == '__main__':
    main()
