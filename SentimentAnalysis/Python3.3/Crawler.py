'''
Created on Dec 18, 2013

@author: KevinVillela
'''
import sys #To flush stdout
from DatumBox import DatumBox
#import urllib3
from math import trunc
import jdcal
from urllib.parse import quote_plus
import urllib.request, urllib.error, urllib.parse
from bs4 import BeautifulSoup
#from gevent.pool import Pool
from SentimentThread import SentimentThread
from TorThread import TorThread
from datetime import timedelta
import threading
import gc
import ssl
from queue import Queue
import time
import chardet
import atexit
import random
import Article
import FetchArticle
from urllib.parse import urlencode
#import gevent.monkey
#gevent.monkey.patch_all(thread=False)

BROWSERS = (
    # Top most popular browsers in my access.log on 2009.02.12
    # tail -50000 access.log |
    #  awk -F\" '{B[$6]++} END { for (b in B) { print B[b] ": " b } }' |
    #  sort -rn |
    #  head -20
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.0.6) Gecko/2009011912 Firefox/3.0.6',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.6) Gecko/2009020911 Ubuntu/8.10 (intrepid) Firefox/3.0.6',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6',
    'Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.0.6) Gecko/2009011913 Firefox/3.0.6 (.NET CLR 3.5.30729)',
    'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/1.0.154.48 Safari/525.19',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727; .NET CLR 3.0.04506.30; .NET CLR 3.0.04506.648)',
    'Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.0.6) Gecko/2009020911 Ubuntu/8.10 (intrepid) Firefox/3.0.6',
    'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.5) Gecko/2008121621 Ubuntu/8.04 (hardy) Firefox/3.0.5',
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_5_6; en-us) AppleWebKit/525.27.1 (KHTML, like Gecko) Version/3.2.1 Safari/525.27.1',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 1.1.4322)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; .NET CLR 2.0.50727)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
)

class Crawler(object):
    '''def do_something(response, **kwargs):
        global numberOfArticlePages
        global total
        if (response.status_code == 200):
            numberOfArticlePages += 1
            print "\r" + str(numberOfArticlePages) + " / " + str(total) + " articles crawled to.",
            sys.stdout.flush()
    '''
    def __init__(self, MIN_ARTICLES_PERCENT = .9, MAX_THREADS = 50 ):
        self.threads = []
        self.articlesCompleted = 0
        self.MIN_ARTICLES_PERCENT = MIN_ARTICLES_PERCENT
        self.MAX_THREADS = MAX_THREADS
        self.dbError = False
        atexit.register(self.exitProgram)
        
    def getUser(self, userInfo, userNumber):
        for user in userInfo:
            if (user['userNumber'] == userNumber):
                return user
            
    def articleAnalyzed(self, success):
        self.articlesCompleted = self.articlesCompleted + 1
        if (success == False):
            self.dbError = True
        print(("\r" + str(self.articlesCompleted) + " / " + str(len(self.threads)) + " articles analyzed."), end=' ')
        sys.stdout.flush()

    def crawl(self, userInfo, userNumber, dateToSearch, daysToSearch, fileName, useTor):
        self.useTor = useTor
        global proxies
        user = userInfo[userNumber]
        datum_box = DatumBox(user['APIKey'])  
        sentimentsFile = open(fileName, "a")
        daysToGoBack = 1;
        if useTor:
            print("Starting Tor...")
            self.torThread = TorThread(self)
            self.torThread.start()
            time.sleep(5)
            proxyIP = '127.0.0.1:8118'
        else:
            proxyIP = ''
        #googleHttp = urllib3.PoolManager()
        while(daysToGoBack <= daysToSearch):
            print("Searching on date " + dateToSearch.strftime("%m/%d/%Y") + " (day " + str(daysToGoBack) + " of " + str(daysToSearch) + ")")
            
            julianDate = trunc(sum(jdcal.gcal2jd(dateToSearch.year, dateToSearch.month, dateToSearch.day)) + .5)
            #keyword = '"3M Co" OR "American Express" OR "AT&T" OR "Boeing" OR "Caterpillar" OR "Chevron" OR "Cisco" OR "Dupont E I De Nemours" OR "Exxon" OR "General Electric" OR "Goldman Sachs" OR "Home Depot" OR "Intel" OR "IBM"'# OR "Johnson & Johnson" OR "JPMorgan Chase" OR "McDonald\'s" OR "Merck and Co" OR "Microsoft" OR "Nike" OR "Pfizer" OR "Procter & Gamble" OR "Coca-Cola" OR "Travelers Companies" OR "United Technologies" OR "UnitedHealth" OR "Verizon" OR "Visa" OR "Wal-Mart" OR "Walt Disney"'
            #keywords = ["\"3M Co\"", "\"American Express\"", "\"AT&T Inc\"", "\"Boeing Co\"", "\"Caterpillar Inc\"", "\"Chevron\"", "\"Cisco Systems Inc\"", "\"DuPont\"","\"Exxon Mobil\"","\"General Electric\"","\"Goldman Sachs Group\"","\"Home Depot\"","\"Intel Corp\"","\"International Business Machines\"","\"johnson and johnson\" OR \"Johnson & Johnson\"","\"JP Morgan\"","\"McDonald's Corp\"","\"Merck & Co\"","\"Microsoft Corp\" OR \"Microsoft Corporation\"","\"Nike\"","\"Pfizer\"","\"Procter & Gamble\" OR \"Procter And Gamble\"","\"Coca-Cola\"","\"United Technologies Corp\"","\"UnitedHealth Group\"","\"Verizon Communications\"","\"Visa Inc\"","\"Wal-Mart\"","\"Walt Disney Company\""];
            keywords = ["\"3M Co\"", "\"American Express\"", "\"AT&T\"", "\"Boeing\"", "\"Caterpillar Inc\"", "\"Chevron\"", "\"Cisco Systems\"", "\"DuPont\"","\"Exxon Mobil\"","\"General Electric\"","\"Goldman Sachs Group\"","\"Home Depot\"","\"Intel Corp\"","\"International Business Machines\"","\"Johnson and Johnson\" OR \"Johnson & Johnson\"","\"JP Morgan\"","\"McDonald's Corp\"","\"Merck & Co\"","\"Microsoft Corp\" OR \"Microsoft Corporation\"","\"Nike\"","\"Pfizer\"","\"Procter & Gamble\" OR \"Procter And Gamble\"","\"Coca-Cola\"","\"United Technologies Corp\"","\"UnitedHealth Group\"","\"Verizon Communications\"","\"Visa Inc\"","\"Wal-Mart\"","\"Walt Disney Company\""];
            sites = ["http://money.cnn.com/" + dateToSearch.strftime("%Y"), "http://www.bloomberg.com/news/", "http://www.rttnews.com/", "http://www.reuters.com/finance", "money.usnews.com", "www.ft.com/home/us", "http://www.cnbc.com/", "http://www.fool.com", "http://www.thestreet.com", "http://www.zacks.com", "http://www.seekingalpha.com/article" ]
            baseQuery = "site:" + sites[0]
            first = True
            for site in sites:
                if (first):
                    first = False
                    continue
                baseQuery = baseQuery + " OR site:" + site
            baseQuery = baseQuery + " daterange:" + str(julianDate) + "-" + str(julianDate) + " ";
            
            numberOfResults = 50
            for keyword in keywords:
                query = quote_plus(baseQuery + keyword);
                startPageQuery = "https://startpage.com/do/search?cat=web&abp=1&prfh=lang_homepageEEEs%2Fair%2Feng%2FN1Nenable_post_methodEEE0N1Nrecent_results_filterEEE1N1Nlanguage_uiEEEenglishN1Ndisable_open_in_new_windowEEE1N1Nnum_of_resultsEEE" + str(numberOfResults) + "N1N&suggestOn=0&query=" + query 
                #startPageQuery = "http://ipinfo.io/"
                binaryData = urlencode({'language' : 'english', 'cmd' : 'process_search', 'engine0' :'v1all'}).encode('utf-8')
                print (startPageQuery)
                ssl_context = ssl.SSLContext(ssl.PROTOCOL_SSLv3) #monkey patch...
                proxy_support = urllib.request.ProxyHandler({'http': proxyIP})
                opener = urllib.request.build_opener(proxy_support, urllib.request.HTTPSHandler(context=ssl_context)) #monkey patch...
                urllib.request.install_opener(opener) #monkey patch...
                #headers={'User-agent' : 'Mozilla/5.0', 'Connection':'close'} #No longer used because StartPage blocked it for a while
                #headers={'User-agent' : 'Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.6) Gecko/2009020911 Ubuntu/8.10 (intrepid) Firefox/3.0.6', 'Connection':'close'}
                browser = random.choice(BROWSERS)
                headers={'User-agent' : browser}
                request = urllib.request.Request(url=startPageQuery, data = None, headers=headers)
                response = opener.open(request)
                resultsPage = response.read().decode('utf-8')#.decode('iso-8859-1')
                #print(resultsPage)
                soup = BeautifulSoup(resultsPage)
                resultDivs = soup.findAll("div", { "class" : "result" })
                results = []
                for resultDiv in resultDivs:
                    if ('none' in resultDiv.get('class')):
                        continue
                    parent = resultDiv.findParent('div')
                    if parent.get('id') == 'sponsored_container':
                        continue
                    h3 = resultDiv.find("h3")
                    if (h3 is None):
                        continue
                    url = h3.find("a", href=True)['href']
                    results.append(url)
                try:
                    numberOfArticlePages = 0
                    articles = []
                    articleURLs = []
                    articleRanks = []
                    total = len(results)
            
                    # Was using gevent, but then switched to python3.3, which does not yet support gevent
                    crawlThreads = []
                    for index,res in enumerate(results):
                        t = threading.Thread(target=FetchArticle.fetch, args=(keyword, res, index, articles, len(results)))
                        t.daemon = True  # thread dies when main thread (only non-daemon thread) exits.
                        t.start()
                        crawlThreads.append(t)
                    for thread in crawlThreads:
                        thread.join(60)
                        if (thread.isAlive()):
                            print("A URL has timed out")
                    # I was using grequests, but it appeared that they were leaking file descriptors... :(
                    #articleRequests = (grequests.get(res, hooks = {'response' : do_something}, timeout=60) for res in results)
                    #articlePages = grequests.map(articleRequests)
                    print()
                except gevent.Timeout:
                    if (numberOfArticlePages >= len(results) * self.MIN_ARTICLES_PERCENT):
                        print(("Timeout, but continuing because we have " + str(numberOfArticlePages) + " articles."))
                    else:
                        print(("Timeout, going to next day because we have only " + str(numberOfArticlePages) + " articles."))
                        continue
                print("All articles (" + str(len(articles)) + " of 'em) for date " + dateToSearch.strftime("%m/%d/%Y") + " and keyword " + keyword + " returned, now being analyzed...")
    
                i = 1
                mutex_writefile = threading.Lock()
                #for res in results:
                self.dbError = True
                while (self.dbError == True): # This might get some articles twice, but its okay because once they are in the db it won't matter
                    print("Gathering articles")
                    self.dbError = False
                    self.threads = []
                    for article in articles:
                        #articleURL = res.url.encode("utf8")
                        thread = SentimentThread(article, i, datum_box, proxyIP, self, keyword, fileName, dateToSearch, mutex_writefile, user['subscriptionID'])
                        #thread.daemon = True
                        thread.start()
                        self.threads.append(thread)
                        i = i + 1
                        if (len(self.threads) >= self.MAX_THREADS):
                            for thread in self.threads:
                                thread.join()
                    for thread in self.threads:
                        thread.join()
                    self.articlesCompleted = 0
                    if (self.dbError == True):
                        userNumber = userNumber - 1
                        if (userNumber < 0):
                            print("Out of Users")
                            return
                        user = userInfo[userNumber]
                        datum_box = DatumBox(user['APIKey']) 
                        print("Switching users and trying again.")
                        if self.useTor:
                            self.torThread.stop()
                            self.torThread.join()
                            time.sleep(5)
                            print("Tor stopped. Restarting...")
                            self.torThread = TorThread(self)
                            self.torThread.start()
                            time.sleep(5)
                            print("Tor restarted. Continuing...")
                print()        
            #Next day!
            print()        
            dateToSearch = dateToSearch - timedelta(1)
            daysToGoBack += 1
        sentimentsFile.close()
        print("Congratulations! All articles analyzed. Shutting down...")
    def killThreads(self):
        pass
        #for thread in self.threads:
            #   thread.stop()
    def exitProgram(self):
        if self.useTor:
            self.torThread.stop()
        print("Shut down successfully.")
    ''' End of Crawl Class ''' 