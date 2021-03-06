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
import urllib
from stem.control import Controller
import os

      
def getDefaultParametersFromCSV(fileName):
    fileName = os.path.join(os.path.dirname(__file__), "../", fileName)
    with open(fileName, 'r', encoding='utf-8') as csvFile:
        defaultParametersFileReader = csv.reader(csvFile, delimiter=',')
        for row in defaultParametersFileReader:
            defaultParameters = {"userNumber" : int(row[0]), "year" : int(row[1]), "month" : int(row[2]), "day" : int(row[3]), "daysToSearch" : int(row[4]), "fileName" : row[5]}
        csvFile.close()
        return defaultParameters
def getDefaultParametersFromDict(fileName):
    fileName = os.path.join(os.path.dirname(__file__),"../", fileName)
    with open(fileName, 'r', encoding='utf-8') as file:
       return eval(file.read())
def getUsersInfo(fileName):
    fileName = os.path.join(os.path.dirname(__file__), "../", fileName)
    with open(fileName, 'r', encoding='utf-8') as csvFile:
        apiKeysFileReader = csv.reader(csvFile, delimiter=',')
        userInfo = []
        for row in apiKeysFileReader:
            apiObject = {"APIKey" : row[0], "userName" : row[1], "subscriptionID" : row[2] if len(row) >= 3 else None}
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
    #proc = subprocess.Popen(["pgrep -x", "tor"], stdout=subprocess.PIPE) 
    #print("process is " + str(proc))
    '''import stem
    import stem.connection
    import stem.socket
    try:
        control_socket = stem.socket.ControlPort(port = 9050)
        #stem.connection.authenticate(control_socket)
    except stem.SocketError as exc:
        print("Unable to connect to tor on port 9051: %s" % exc)
        sys.exit(1)
    except stem.connection.AuthenticationFailure as exc:
        print("Unable to authenticate: %s" % exc)
        sys.exit(1)
    
    print("Issuing 'GETINFO version' query...\n")
    control_socket.send('GETINFO version')
    print(control_socket.recv())
    '''
    params = getDefaultParametersFromDict("ProductData/DefaultParameters.dict")
    userInfo = getUsersInfo("ProductData/API_Keys.csv")
    if (len(sys.argv) != 8):
        print("usage: ./main <user_number> <year_to_start_search> <month_to_start_search> <day_to_start_search> <days_to_search> <output_file_name> <use_tor>")
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
        params['useTor'] = sys.argv[7]
        
    params['fileName'] = os.path.join(os.path.dirname(__file__), "../", params['fileName'])
    if params['useTor'][:1].lower() == 'y':
        params['useTor'] = True
    else:
        params['useTor'] = False
        
    print("\tRunning with values: user_number: " + str(params['userNumber']) + ", year: " + str(params['year']) + ", month: " + str(params['month']) + ", day: " + str(params['day']) + ", days to search: " + str(params['daysToSearch']) + ", file name: " + params['fileName'] + ", use tor: " + str(params['useTor']))
    
    #getProxies("united_states_proxies.txt")
    crawler = Crawler.Crawler()
    crawler.crawl(userInfo, params['userNumber'], datetime(params['year'], params['month'], params['day'], 12, 0, 0, 0), params['daysToSearch'], params['fileName'], params['useTor'])

if __name__ == "__main__":
    main()