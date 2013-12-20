'''
Created on Dec 1, 2013

@author: KevinVillela
'''
MAX_PROXIES = 50
numberOfArticlePages = 0
total = 0
proxies = {}

from datetime import datetime
import time # To sleep
#import grequests # Not being used because of a potential memory leak: leaking file descriptors
import sys
#import gevent.monkey
import Crawler
import pprint
import csv # To read the API Keys
#gevent.monkey.patch_socket()
      
def getDefaultParameters(fileName):
    with open(fileName, 'r', encoding='utf=-8') as csvFile:
        defaultParametersFileReader = csv.reader(csvFile, delimiter=',')
        for row in defaultParametersFileReader:
            defaultParameters = {"userNumber" : int(row[0]), "year" : int(row[1]), "month" : int(row[2]), "day" : int(row[3]), "daysToSearch" : int(row[4]), "fileName" : row[5]}
        csvFile.close()
        return defaultParameters
def getUsersInfo(fileName):
    with open(fileName, 'r', encoding='utf=-8') as csvFile:
        apiKeysFileReader = csv.reader(csvFile, delimiter=',')
        userInfo = []
        for row in apiKeysFileReader:
            apiObject = {"userNumber" : row[0], "APIKey" : row[1], "userName" : row[2], "subscriptionID" : row[3] if len(row) >= 4 else None}
            userInfo.append(apiObject)
        csvFile.close()
        return userInfo
def getProxies(fileName):
    f = open(fileName, 'r')
    global proxies
    proxies = {}
    i = 0
    for line in f:
        proxy = line.strip()
        proxies[proxy] = 0
        i = i + 1
        if (i >= MAX_PROXIES):
            break
    f.close()
def main():
    params = getDefaultParameters("Data/DefaultParameters.csv")
    userInfo = getUsersInfo("Data/DatumBoxAPIKeys.csv")
    if (len(sys.argv) != 7):
        print("usage: ./main <user_number> <year_to_start_search> <month_to_start_search> <day_to_start_search> <days_to_search> <output_file_name>")
        print("Note that search goes backwards in time each day for <days_to_search> days or until API calls are exhausted")
        delay = 1
        print("Now running with default values in " + str(delay) + " seconds")
        time.sleep(delay);
    else:
        params['userNumber'] = int(sys.argv[1]) 
        params['year'] = int(sys.argv[2])
        params['month'] = int(sys.argv[3])
        params['day'] = int(sys.argv[4])
        params['daysToSearch'] = int(sys.argv[5])
        params['fileName'] = sys.argv[6]
    print("\tRunning with values: user_number: " + str(params['userNumber']) + ", year: " + str(params['year']) + ", month: " + str(params['month']) + ", day: " + str(params['day']) + ", days to search: " + str(params['daysToSearch']) + ", file name: " + params['fileName'])
    
    #getProxies("united_states_proxies.txt")
    crawler = Crawler.Crawler()
    crawler.crawl(userInfo, params['userNumber'], datetime(params['year'], params['month'], params['day'], 12, 0, 0, 0), params['daysToSearch'], "Data/" + params['fileName'])

if __name__ == "__main__":
    main()